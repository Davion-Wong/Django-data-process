from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
from backend.infer_data_types import infer_data_types  # Import your inference function
import os

def upload_file(request):
    if request.method == 'POST' and request.FILES['file']:
        # Save the uploaded file temporarily
        uploaded_file = request.FILES['file']
        file_path = os.path.join('temp', uploaded_file.name)
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        # Process the uploaded file using the infer_data_types script
        df = infer_data_types(file_path)

        # Get the inferred data types and display them
        inferred_types = df.dtypes.to_dict()
        return HttpResponse(f"Inferred Data Types: {inferred_types}")

    return render(request, 'upload.html')
