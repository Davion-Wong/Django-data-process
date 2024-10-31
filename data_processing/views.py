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


processed_data_ready = False

# CSRF token view for frontend
def csrf_token_view(request):
    return JsonResponse({'csrfToken': get_token(request)})


# Improved file upload API view
@api_view(['POST'])
def api_upload_file(request):
    logger.info("Starting file upload")
    global processed_data_ready
    processed_data_ready = False

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


# Check processed data readiness status
@api_view(['GET'])
def get_processed_data_status(request):
    global processed_data_ready
    return JsonResponse({"processed_data_ready": processed_data_ready})

@api_view(['GET'])
def processed_data_status(request):
    processed_data_path = os.path.join('temp', 'processed_dataset.csv')  # Ensure this matches the output file path in your task
    is_ready = os.path.exists(processed_data_path)  # Check file existence
    return Response({'processed_data_ready': is_ready})


#
# @api_view(['GET'])
# def get_processed_dataset(request):
#     global processed_data_ready
#     processed_dataset_path = os.path.join('temp', 'processed_dataset.csv')
#
#     if not processed_data_ready or not os.path.exists(processed_dataset_path):
#         return Response({'error': 'No processed dataset found. Please upload a file first.'},
#                         status=status.HTTP_404_NOT_FOUND)
#
#     logger.info("Processed dataset file found. Loading data...")
#     df = pd.read_csv(processed_dataset_path)
#     logger.info(f"DataFrame loaded with {len(df)} rows.")
#
#     # Use improved type inference for each column
#     inferred_types = {col: infer_column_type(df[col]) for col in df.columns}
#     logger.info(f"Custom Inferred data types: {inferred_types}")
#
#     # Paginate the DataFrame records
#     paginator = DatasetPagination()
#     page = paginator.paginate_queryset(df.to_dict('records'), request)
#
#     # Return the data with inferred custom data types
#     return paginator.get_paginated_response({
#         'data': page,
#         'types': inferred_types,
#         'total_rows': len(df)
#     })



# Main dataset display view
def dataset_display_view(request):
    return render(request, 'data_processing/data_display.html')


# Check task status and set processed_data_ready flag
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
        processed_data_ready = True  # Set processed data as ready
        return Response({
            'status': 'Completed',
            'inferred_types': task_result.result,
            'progress': 100
        })
    else:
        logger.error(f"Task failed with error: {task_result.info}")
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

# Function to infer custom data types
def infer_column_type(series):
    """Infer custom types for a DataFrame column."""
    if pd.api.types.is_numeric_dtype(series):
        if series.nunique() < 20:
            return "Category"  # Consider columns with few unique values as categorical
        return "Numeric"
    elif pd.api.types.is_datetime64_any_dtype(series):
        return "Date"
    elif pd.api.types.is_string_dtype(series):
        if series.nunique() < 20:
            return "Category"
        return "Text"
    return "Unknown"

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

    # Use improved type inference for each column
    inferred_types = {col: infer_column_type(df[col]) for col in df.columns}
    logger.info(f"Custom Inferred data types: {inferred_types}")

    # Paginate the DataFrame records
    paginator = DatasetPagination()
    page = paginator.paginate_queryset(df.to_dict('records'), request)

    # Return the data with inferred custom data types
    return paginator.get_paginated_response({
        'data': page,
        'types': inferred_types,
        'total_rows': len(df)
    })