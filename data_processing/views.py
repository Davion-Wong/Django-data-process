from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from django.http import JsonResponse
from django.middleware.csrf import get_token
from backend.infer_data_types import infer_data_types
from django.shortcuts import render
import pandas as pd
import os
from celery.result import AsyncResult
from django.core.files.storage import default_storage
import logging
from backend.utils import infer_column_type


logger = logging.getLogger(__name__)


processed_data_ready = False


def csrf_token_view(request):
    return JsonResponse({'csrfToken': get_token(request)})



@api_view(['POST'])
def api_upload_file(request):
    global processed_data_ready
    processed_data_ready = False

    if 'file' not in request.FILES:
        logger.error("No file provided in the request")
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        uploaded_file = request.FILES['file']
        file_path = default_storage.save(f"temp/{uploaded_file.name}", uploaded_file)
        task = infer_data_types.delay(file_path)
        return Response({'message': 'File uploaded successfully! Processing task started.', 'task_id': task.id}, status=status.HTTP_202_ACCEPTED)

    except Exception as e:
        logger.exception("Exception occurred during file upload")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DatasetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET'])
def get_processed_data_status(request):
    global processed_data_ready
    return JsonResponse({"processed_data_ready": processed_data_ready})

@api_view(['GET'])
def processed_data_status(request):
    processed_data_path = os.path.join('temp', 'processed_dataset.csv')
    is_ready = os.path.exists(processed_data_path)
    return Response({'processed_data_ready': is_ready})

def dataset_display_view(request):
    return render(request, 'data_processing/data_display.html')


@api_view(['GET'])
def check_task_status(request, task_id):
    global processed_data_ready
    task_result = AsyncResult(task_id)
    logger.info(f"Checking task status: {task_result.state}")

    if task_result.state == 'PENDING':
        return Response({'status': 'Pending', 'progress': 0})
    elif task_result.state == 'PROGRESS':
        return Response({'status': 'In Progress', 'progress': task_result.info.get('progress', 0)})
    elif task_result.state == 'SUCCESS':
        logger.info("Task completed successfully.")
        processed_data_ready = True
        return Response({
            'status': 'Completed',
            'inferred_types': task_result.result,
            'progress': 100
        })
    else:
        logger.error(f"Task failed with error: {task_result.info}")
        return Response({'status': 'Failed', 'error': str(task_result.info)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_processed_dataset(request):
    global processed_data_ready
    processed_dataset_path = os.path.join('temp', 'processed_dataset.csv')

    if not processed_data_ready or not os.path.exists(processed_dataset_path):
        return Response({'error': 'No processed dataset found. Please upload a file first.'},
                        status=status.HTTP_404_NOT_FOUND)

    logger.info("Processed dataset file found. Loading data...")
    df = pd.read_csv(processed_dataset_path)
    logger.info(f"DataFrame loaded with {len(df)} rows.")

    inferred_types = {col: infer_column_type(df[col]) for col in df.columns}
    logger.info(f"Custom Inferred data types: {inferred_types}")

    paginator = DatasetPagination()
    page = paginator.paginate_queryset(df.to_dict('records'), request)

    return paginator.get_paginated_response({
        'data': page,
        'types': inferred_types,
        'total_rows': len(df)
    })