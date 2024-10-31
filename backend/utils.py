from datetime import datetime
import pandas as pd
import re


def infer_column_type(series):
    date_count = 0
    numeric_count = 0
    sample_size = min(len(series), 100)

    for value in series.dropna().sample(sample_size):
        str_value = str(value)
        if re.match(r"^\d{1,2}/\d{1,2}/\d{2,4}$", str_value) or re.match(r"^\d{4}-\d{2}-\d{2}$", str_value):
            date_count += 1
        elif str_value.isnumeric():
            numeric_count += 1

    if date_count > 0.7 * sample_size:
        return "Date"

    if pd.api.types.is_datetime64_any_dtype(series):
        return "Date"

    if numeric_count > 0.9 * sample_size:
        return "Numeric"

    try:
        parsed_dates = pd.to_datetime(series, errors='coerce')
        if parsed_dates.notna().sum() > 0.9 * len(series):  # More than 90% valid dates
            return "Date"
    except Exception as e:
        print(f"Date inference failed: {e}")

    if pd.api.types.is_numeric_dtype(series):
        if series.nunique() < 20:
            return "Category"
        return "Numeric"

    if series.nunique() < 20:
        return "Category"

    if pd.api.types.is_string_dtype(series):
        if is_name_column(series):
            return "Name"
        return "Text"

    return "Unknown"


def is_name_column(series):
    sample_size = min(len(series), 100)
    name_count = 0

    for value in series.dropna().sample(sample_size):
        if isinstance(value, str) and all(word.istitle() for word in value.split()):
            name_count += 1

    return name_count > 0.7 * sample_size
