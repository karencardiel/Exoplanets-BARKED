
import pandas as pd
import numpy as np

# Load the filtered dataset
try:
    df = pd.read_csv('filtered_sample.csv')
    print("--- Data Quality Check for filtered_sample.csv ---")
    print("\nSuccessfully loaded 'filtered_sample.csv'.\n")

    # 1. Check for Null (Missing) Values
    print("--- 1. Checking for Null Values ---")
    null_counts = df.isnull().sum()
    null_columns = null_counts[null_counts > 0]

    if not null_columns.empty:
        print("Found null values in the following columns:")
        print(null_columns)
    else:
        print("No null values found in any column.")
    print("-" * 35)

    # 2. Check for Potential Misspellings in Categorical Columns
    print("\n--- 2. Checking Categorical Data for Inconsistencies ---")
    categorical_cols = ['koi_disposition', 'koi_pdisposition']
    for col in categorical_cols:
        unique_values = df[col].unique()
        print(f"Unique values in '{col}': {unique_values}")
    print("-" * 35)

    # 3. Check Data Types
    print("\n--- 3. Checking Data Types ---")
    print("Data types of each column:")
    print(df.dtypes)
    print("-" * 35)
    
    # 4. Check for Infinite values
    print("\n--- 4. Checking for Infinite Values ---")
    infinite_values = df.isin([np.inf, -np.inf]).sum()
    infinite_columns = infinite_values[infinite_values > 0]
    if not infinite_columns.empty:
        print("Found infinite values in the following columns:")
        print(infinite_columns)
    else:
        print("No infinite values found.")
    print("-" * 35)


except FileNotFoundError:
    print("Error: 'filtered_sample.csv' not found. Please ensure the file exists in the correct directory.")

except Exception as e:
    print(f"An error occurred: {e}")
