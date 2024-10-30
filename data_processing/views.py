from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from django.http import JsonResponse
from django.middleware.csrf import get_token
from backend.infer_data_types import infer_data_types
from django.shortcuts import render
import pandas as pd
import os
from .models import DatasetModel
from celery.result import AsyncResult
from django.core.files.storage import default_storage
from .tasks import long_running_task
import logging

# Initialize logger
logger = logging.getLogger(__name__)


# CSRF token view for frontend
def csrf_token_view(request):
    return JsonResponse({'csrfToken': get_token(request)})


# Improved file upload API view
@api_view(['POST'])
def api_upload_file(request):
    logger.info("Starting file upload")

    if 'file' not in request.FILES:
        logger.error("No file provided in the request")
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        uploaded_file = request.FILES['file']
        file_path = default_storage.save(f"temp/{uploaded_file.name}", uploaded_file)
        logger.info(f"File saved at {file_path}")

        # Trigger the task asynchronously
        task = infer_data_types.delay(file_path)
        logger.info(f"Task {task.id} started for file processing.")

        # Return a response with the task ID
        return Response({'message': 'File uploaded successfully! Processing task started.', 'task_id': task.id}, status=status.HTTP_202_ACCEPTED)

    except Exception as e:
        logger.exception("Exception occurred during file upload")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Display view for processed dataset with pagination
class DatasetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET'])
def get_processed_dataset(request):
    processed_dataset_path = os.path.join('temp', 'processed_dataset.csv')

    # Check if the processed file exists
    if not os.path.exists(processed_dataset_path):
        logger.error("Processed dataset file not found.")
        return Response({'error': 'No processed dataset found. Please upload a file first.'},
                        status=status.HTTP_404_NOT_FOUND)

    logger.info("Processed dataset file found. Loading data...")
    df = pd.read_csv(processed_dataset_path)
    logger.info(f"DataFrame loaded with {len(df)} rows.")

    # Infer data types for each column
    inferred_types = {col: str(dtype) for col, dtype in df.dtypes.items()}

    # Paginate the DataFrame records
    paginator = DatasetPagination()
    page = paginator.paginate_queryset(df.to_dict('records'), request)

    # Return the data with inferred data types
    return paginator.get_paginated_response({
        'data': page,
        'types': inferred_types,
        'total_rows': len(df)
    })


# Main dataset display view
def dataset_display_view(request):
    return render(request, 'data_processing/data_display.html')


@api_view(['GET'])
def check_task_status(request, task_id):
    task_result = AsyncResult(task_id)

    if task_result.state == 'PENDING':
        return Response({'status': 'Pending', 'progress': 0})
    elif task_result.state == 'PROGRESS':
        return Response({'status': 'In Progress', 'progress': task_result.info.get('progress', 0)})
    elif task_result.state == 'SUCCESS':
        return Response({
            'status': 'Completed',
            'inferred_types': task_result.result,
            'progress': 100
        })
    else:
        return Response({'status': 'Failed', 'error': str(task_result.info)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def start_long_task(request):
    task = long_running_task.delay()
    return JsonResponse({'task_id': task.id})


def check_task_progress(request, task_id):
    task = AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {'state': task.state, 'progress': 0}
    elif task.state != 'FAILURE':
        response = {'state': task.state, 'progress': task.info.get('current', 0) / task.info.get('total', 1) * 100}
    else:
        response = {'state': task.state, 'progress': 100, 'error': str(task.info)}  # In case of error

    return JsonResponse(response)
