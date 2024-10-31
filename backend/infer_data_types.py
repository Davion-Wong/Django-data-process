from celery import shared_task
import pandas as pd
import logging
import os
from backend.utils import infer_column_type

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def infer_data_types(self, file_path, chunksize=5000):
    total_rows = sum(1 for row in open(file_path))
    rows_processed = 0
    processed_data = []

    try:
        for chunk in pd.read_csv(file_path, chunksize=chunksize):
            rows_processed += len(chunk)
            processed_data.append(chunk)
            progress = (rows_processed / total_rows) * 100
            self.update_state(state="PROGRESS", meta={"progress": progress})

        processed_df = pd.concat(processed_data, ignore_index=True)

        inferred_types = {col: infer_column_type(processed_df[col]) for col in processed_df.columns}

        processed_dataset_path = os.path.join('temp', 'processed_dataset.csv')
        processed_df.to_csv(processed_dataset_path, index=False)

        return {"status": "Task completed!", "progress": 100, "inferred_types": inferred_types}

    except Exception as e:
        logger.exception(f"Error in infer_data_types: {e}")
        raise
