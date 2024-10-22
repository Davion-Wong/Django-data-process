from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import pandas as pd
from backend.infer_data_types import infer_data_types  # Your inference function
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

    # Process the uploaded file using the infer_data_types script
    df = infer_data_types(file_path)

    # Get the inferred data types and return them as a JSON response
    inferred_types = df.dtypes.astype(str).to_dict()

    # Remove the temp file after processing
    os.remove(file_path)

    return Response({'inferred_types': inferred_types}, status=status.HTTP_200_OK)
