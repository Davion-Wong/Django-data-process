from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
import pandas as pd
import os

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
