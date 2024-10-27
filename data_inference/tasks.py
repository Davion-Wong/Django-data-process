from celery import shared_task
from backend/infer_data_types import infer_data_types

@shared_task
def process_large_file(file_path):
    # Call the function that processes large files
    return infer_data_types(file_path)
