import pandas as pd
import numpy as np
from openpyxl import Workbook

# Number of rows and columns for the large dataset
num_rows = 10_000_000  # 10 million rows
rows_per_sheet = 1_000_000  # Max rows per sheet for Excel
num_columns = 5  # Number of columns

# Generate random data
data = {
    'Name': np.random.choice(['Alice', 'Bob', 'Charlie', 'David', 'Eve'], size=num_rows),
    'Birthdate': pd.date_range(start='1990-01-01', periods=num_rows, freq='min'),
    'Score': np.random.randint(50, 100, size=num_rows),
    'Grade': np.random.choice(['A', 'B', 'C', 'D', 'F'], size=num_rows),
    'Comments': np.random.choice(['Good', 'Average', 'Poor', 'Excellent', 'Needs Improvement'], size=num_rows)
}

# Create DataFrame
df = pd.DataFrame(data)

# Create an Excel workbook
wb = Workbook()

# Split the DataFrame into chunks and write each chunk to a new sheet
for i in range(0, num_rows, rows_per_sheet):
    # Define the sheet name
    sheet_name = f'Sheet_{i // rows_per_sheet + 1}'

    # Create a new worksheet
    ws = wb.create_sheet(title=sheet_name)

    # Get the current chunk of data
    chunk = df[i:i + rows_per_sheet]

    # Write the header
    ws.append(list(chunk.columns))

    # Write data row by row to the Excel sheet
    for row in chunk.itertuples(index=False, name=None):
        ws.append(row)

# Save the workbook to an Excel file
wb.save('large_test_file.xlsx')

print(f'Large Excel file with {num_rows} rows created successfully across multiple sheets!')
