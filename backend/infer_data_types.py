from celery import shared_task, current_task
import pandas as pd
import logging
logger = logging.getLogger(__name__)


@shared_task(bind=True)
def infer_data_types(self, file_path, chunksize=10000):
    logger.info(f"Starting infer_data_types task with file_path: {file_path}")
    total_rows = sum(1 for row in open(file_path))
    rows_processed = 0

    inferred_types = {}  # Dictionary to hold column types

    try:
        for chunk in pd.read_csv(file_path, chunksize=chunksize):
            rows_processed += len(chunk)
            progress = (rows_processed / total_rows) * 100
            self.update_state(state="PROGRESS", meta={"progress": progress})

            # Infer data types from chunk and update inferred_types
            for col, dtype in chunk.dtypes.items():
                inferred_types[col] = str(dtype)

        logger.info("Task processing complete.")
    except Exception as e:
        logger.exception(f"Error in infer_data_types: {e}")
        raise
    return inferred_types  # Return inferred types dictionary

