import pandas as pd
import numpy as np

# Number of rows and columns for the large dataset
num_rows = 10_000_000  # 10 million rows
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

# Save the DataFrame to a CSV file
df.to_csv('large_test_file.csv', index=False)

print(f'Large CSV file with {num_rows} rows created successfully!')
