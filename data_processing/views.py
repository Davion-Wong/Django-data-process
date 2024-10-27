from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view
from backend.infer_data_types import infer_data_types
from django.shortcuts import render
import pandas as pd
import os
from .models import DatasetModel
from .tasks import long_running_task
from django.http import JsonResponse
from celery.result import AsyncResult
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.files.storage import default_storage
from .tasks import long_running_task  # Import your task function

def upload_file_view(request):
    if request.method == 'POST':
        # Handle file upload logic here
        return JsonResponse({"message": "File uploaded successfully"})
    return JsonResponse({"error": "Invalid request method"}, status=400)

@csrf_exempt  # Ensure CSRF is properly configured if using this decorator
def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        file_path = default_storage.save(f"uploads/{uploaded_file.name}", uploaded_file)  # Save file

        # Trigger long-running task with the file path
        task = long_running_task.delay(file_path)
        return JsonResponse({'task_id': task.id})
    else:
        return JsonResponse({'error': 'File not provided'}, status=400)

def check_task_progress(request, task_id):
    task = AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {'state': task.state, 'progress': 0}
    elif task.state != 'FAILURE':
        response = {'state': task.state, 'progress': task.info.get('current', 0) / task.info.get('total', 1) * 100}
    else:
        response = {'state': task.state, 'progress': 100, 'error': str(task.info)}  # In case of error

    return JsonResponse(response)

def start_long_task(request):
    task = long_running_task.delay()
    return JsonResponse({'task_id': task.id})


def dataset_display_view(request):
    # Assuming you pass the processed data to the template
    # You can load the dataset to render in the template
    context = {
        'data': processed_data,  # Replace with your actual dataset or context
    }
    return render(request, 'data_display.html', context)


# View to handle file upload
@api_view(['POST'])
def api_upload_file(request):
    if 'file' not in request.FILES:
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

    # Save the uploaded file temporarily
    uploaded_file = request.FILES['file']
    file_path = os.path.join('temp', uploaded_file.name)
    with open(file_path, 'wb+') as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)

    # Process the uploaded file (e.g., infer data types)
    inferred_dtypes_series = infer_data_types(file_path)

    if isinstance(inferred_dtypes_series, pd.Series):
        inferred_types = inferred_dtypes_series.astype(str).to_dict()

        # Save the processed dataset to a file (for later display)
        processed_dataset_path = os.path.join('temp', 'processed_dataset.csv')
        df = pd.read_csv(file_path)  # Assuming file processing happens here
        df.to_csv(processed_dataset_path, index=False)

        # Return inferred types and a success message
        return Response({'inferred_types': inferred_types, 'message': 'File uploaded and processed successfully!'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Data processing error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# View to handle dataset display with pagination
class DatasetPagination(PageNumberPagination):
    page_size = 10  # Adjust the page size as needed
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET'])
def get_processed_dataset(request):
    # Load the processed dataset (assuming it's stored temporarily after upload)
    processed_dataset_path = os.path.join('temp', 'processed_dataset.csv')

    # Check if the dataset file exists
    if not os.path.exists(processed_dataset_path):
        return Response({'error': 'No processed dataset found. Please upload a file first.'}, status=status.HTTP_404_NOT_FOUND)

    df = pd.read_csv(processed_dataset_path)

    # Paginate the dataset
    paginator = DatasetPagination()
    page = paginator.paginate_queryset(df.to_dict('records'), request)

    return paginator.get_paginated_response(page)

def check_task_status(request, task_id):
    task_result = AsyncResult(task_id)
    if task_result.state == 'PENDING':
        response = {'state': task_result.state, 'progress': 0}
    elif task_result.state != 'FAILURE':
        response = {'state': task_result.state, 'progress': task_result.info.get('current', 0), 'total': task_result.info.get('total', 1)}
    else:
        response = {'state': task_result.state, 'progress': 100, 'status': str(task_result.info)}
    return JsonResponse(response)


class DatasetPagination(PageNumberPagination):
    page_size = 50  # Display 50 rows per page
@api_view(['GET'])
def dataset_view(request):
    queryset = DatasetModel.objects.all()  # or wherever the processed data is stored
    paginator = DatasetPagination()
    result_page = paginator.paginate_queryset(queryset, request)
    return paginator.get_paginated_response(result_page)