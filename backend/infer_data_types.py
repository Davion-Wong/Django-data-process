from celery import shared_task, current_task
import pandas as pd


@shared_task(bind=True)
def infer_data_types(self, file_path, chunksize=10000):
    total_rows = sum(1 for row in open(file_path))  # Estimate for progress
    rows_processed = 0

    for chunk in pd.read_csv(file_path, chunksize=chunksize):
        rows_processed += len(chunk)
        progress = (rows_processed / total_rows) * 100
        self.update_state(state="PROGRESS", meta={"progress": progress})

        # Processing logic on the chunk (as needed)

    return {"status": "Task completed!", "progress": 100}
