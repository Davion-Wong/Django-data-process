from celery import shared_task, current_task
import pandas as pd
import logging
import os

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def infer_data_types(self, file_path, chunksize=10000):
    logger.info(f"Starting infer_data_types task with file_path: {file_path}")
    total_rows = sum(1 for row in open(file_path))  # Estimate for progress
    rows_processed = 0

    processed_data = []  # Accumulate chunks here

    try:
        for chunk in pd.read_csv(file_path, chunksize=chunksize):
            rows_processed += len(chunk)
            processed_data.append(chunk)  # Collect chunks
            progress = (rows_processed / total_rows) * 100
            self.update_state(state="PROGRESS", meta={"progress": progress})

        # After all chunks are processed, concatenate and save to CSV
        processed_df = pd.concat(processed_data, ignore_index=True)
        processed_dataset_path = os.path.join('temp', 'processed_dataset.csv')
        processed_df.to_csv(processed_dataset_path, index=False)
        logger.info(f"Data saved to {processed_dataset_path}")

        logger.info("Task processing complete and file saved.")
    except Exception as e:
        logger.exception(f"Error in infer_data_types: {e}")
        raise

    return {"status": "Task completed!", "progress": 100}
