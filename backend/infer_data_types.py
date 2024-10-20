import pandas as pd


def infer_data_types(file_path):
    # Read the file into a DataFrame
    df = pd.read_csv(file_path)

    # Print the first few rows to inspect the data
    print("Sample Data:")
    print(df.head())

    # Try to convert object types to more specific types
    for column in df.columns:
        if df[column].dtype == 'object':
            # If the column contains mostly strings, skip conversion
            if df[column].str.isnumeric().sum() == 0 and not is_date_column(df[column]):
                continue  # Skip non-numeric and non-date columns like Name and Grade

            # Check if the column could be a date
            if is_date_column(df[column]):
                df[column] = pd.to_datetime(df[column], errors='coerce')
            # Otherwise, try to convert to numeric
            else:
                df[column] = pd.to_numeric(df[column], errors='coerce')

    # Print the inferred data types after conversion attempts
    inferred_types = df.dtypes
    print("Inferred Data Types after conversion attempts:")
    print(inferred_types)

    # Return the DataFrame with inferred types
    return df


def is_date_column(column):
    """Checks if a column can be inferred as a date."""
    try:
        pd.to_datetime(column, errors='raise')
        return True
    except (ValueError, TypeError):
        return False


if __name__ == "__main__":
    file_path = "C:/Users/User/PycharmProjects/Django-data-process/backend/sample_data.csv"
    df = infer_data_types(file_path)
