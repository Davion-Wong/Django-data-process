from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import pandas as pd
from backend.infer_data_types import infer_data_types  # Ensure proper import of infer_data_types function
import os

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

    # Process the uploaded file using the infer_data_types function
    inferred_dtypes_series = infer_data_types(file_path)

    # Ensure the result is a pandas Series or DataFrame
    if isinstance(inferred_dtypes_series, pd.Series):
        inferred_types = inferred_dtypes_series.astype(str).to_dict()

        # Clean up the temp file
        os.remove(file_path)

        return Response({'inferred_types': inferred_types}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Data processing error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
