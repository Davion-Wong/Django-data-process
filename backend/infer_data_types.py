from celery import shared_task
import pandas as pd
import logging
import os

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def infer_data_types(self, file_path, chunksize=10000):
    logger.info(f"Starting infer_data_types task with file_path: {file_path}")
    total_rows = sum(1 for row in open(file_path))
    rows_processed = 0
    processed_data = []

    inferred_types = {}

    try:
        # Process the file in chunks and concatenate them into a single DataFrame
        for chunk in pd.read_csv(file_path, chunksize=chunksize):
            rows_processed += len(chunk)
            processed_data.append(chunk)
            progress = (rows_processed / total_rows) * 100
            self.update_state(state="PROGRESS", meta={"progress": progress})

        processed_df = pd.concat(processed_data, ignore_index=True)

        # Type inference logic
        for column in processed_df.columns:
            col_data = processed_df[column]

            # Check if the column can be parsed as datetime
            if pd.api.types.is_datetime64_any_dtype(col_data) or pd.to_datetime(col_data, errors='coerce').notna().all():
                inferred_types[column] = 'Date'
            # Check if the column is numeric (integer or float)
            elif pd.api.types.is_numeric_dtype(col_data):
                inferred_types[column] = 'Numeric'
            # Check if the column has few unique values and can be considered categorical
            elif col_data.nunique() < 20:
                inferred_types[column] = 'Category'
            # Otherwise, categorize as Text
            else:
                inferred_types[column] = 'Text'

        # Save processed dataset and return inferred types
        processed_dataset_path = os.path.join('temp', 'processed_dataset.csv')
        processed_df.to_csv(processed_dataset_path, index=False)
        logger.info(f"Data saved to {processed_dataset_path}")

        return {"status": "Task completed!", "progress": 100, "inferred_types": inferred_types}

    except Exception as e:
        logger.exception(f"Error in infer_data_types: {e}")
        raise

