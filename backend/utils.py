from datetime import datetime
import pandas as pd
import re


def infer_column_type(series):
    date_count = 0
    numeric_count = 0
    sample_size = min(len(series), 100)

    # Sample to determine if the column contains date-like values
    for value in series.dropna().sample(sample_size):
        str_value = str(value)
        # Count date-like values using regex to avoid numeric misinterpretation
        if re.match(r"^\d{1,2}/\d{1,2}/\d{2,4}$", str_value) or re.match(r"^\d{4}-\d{2}-\d{2}$", str_value):
            date_count += 1
        elif str_value.isnumeric():
            numeric_count += 1

    # Determine if majority of the sample values are dates
    if date_count > 0.7 * sample_size:
        return "Date"

    # Check for datetime dtype if column is already parsed as datetime
    if pd.api.types.is_datetime64_any_dtype(series):
        return "Date"

    # Additional check: If the column has many numeric-like entries, it is likely numeric
    if numeric_count > 0.9 * sample_size:
        return "Numeric"

    try:
        # Final attempt to convert column to datetime with 'coerce' to catch non-date values as NaT
        parsed_dates = pd.to_datetime(series, errors='coerce')
        if parsed_dates.notna().sum() > 0.9 * len(series):  # More than 90% valid dates
            return "Date"
    except Exception as e:
        print(f"Date inference failed: {e}")

    # Standard check for numeric type
    if pd.api.types.is_numeric_dtype(series):
        if series.nunique() < 20:
            return "Category"
        return "Numeric"

    # Check for categorical columns with fewer unique values
    if series.nunique() < 20:
        return "Category"

    # Check for names and text columns
    if pd.api.types.is_string_dtype(series):
        if is_name_column(series):
            return "Name"
        return "Text"

    # If no type matches
    return "Unknown"


def is_name_column(series):
    sample_size = min(len(series), 100)
    name_count = 0

    for value in series.dropna().sample(sample_size):
        if isinstance(value, str) and all(word.istitle() for word in value.split()):
            name_count += 1

    return name_count > 0.7 * sample_size
