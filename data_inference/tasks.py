from celery import shared_task
from backend/infer_data_types import infer_data_types
import time

@shared_task(bind=True)
def long_running_task(self):
    total_steps = 5
    for step in range(total_steps):
        time.sleep(2)  # Simulate a long-running task
        self.update_state(state='PROGRESS', meta={'current': step + 1, 'total': total_steps})
    return {'status': 'Task completed!', 'progress': 100}

@shared_task
def process_large_file(file_path):
    # Call the function that processes large files
    return infer_data_types(file_path)
