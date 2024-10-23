import pandas as pd
import os

def infer_data_types(file_path, chunksize=10000):
    # Determine if the file is CSV or Excel
    file_extension = os.path.splitext(file_path)[1].lower()

    combined_dtypes = {}

    if file_extension == '.xlsx':
        # Read Excel file in chunks (note: pd.read_excel doesn't have chunksize, so we read the full file)
        chunks = pd.read_excel(file_path, sheet_name=None)
        for sheet_name, chunk in chunks.items():
            # If the Excel file has multiple sheets, process each sheet separately
            print(f"Processing sheet: {sheet_name}")
            for column in chunk.columns:
                if column.lower().startswith('birthdate'):
                    chunk[column] = pd.to_datetime(chunk[column], errors='coerce')

            chunk_dtypes = chunk.dtypes

            # Merge inferred types with combined_dtypes
            for column, dtype in chunk_dtypes.items():
                if column not in combined_dtypes:
                    combined_dtypes[column] = dtype
                else:
                    if combined_dtypes[column] != dtype:
                        combined_dtypes[column] = 'object'
    else:
        # Process CSV file in chunks
        for chunk in pd.read_csv(file_path, chunksize=chunksize):
            for column in chunk.columns:
                if column.lower().startswith('birthdate'):
                    chunk[column] = pd.to_datetime(chunk[column], errors='coerce')

            chunk_dtypes = chunk.dtypes

            for column, dtype in chunk_dtypes.items():
                if column not in combined_dtypes:
                    combined_dtypes[column] = dtype
                else:
                    if combined_dtypes[column] != dtype:
                        combined_dtypes[column] = 'object'

    # Return a pandas Series of the inferred data types
    return pd.Series(combined_dtypes)
