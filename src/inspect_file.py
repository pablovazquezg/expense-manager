import ast
import pandas as pd
from typing import Any, List

def find_cr_db_columns(data_sample: pd.DataFrame) -> list[int]:
    # Convert the column names of the DataFrame to a list
    columns = data_sample.columns.tolist()

    # Find the position of the column containing 'credit' in its name (case-insensitive)
    credit_column_position = next((i for i, col in enumerate(columns) if 'credit' in col.lower()), None)

    # Find the position of the column containing 'debit' in its name (case-insensitive)
    debit_column_position = next((i for i, col in enumerate(columns) if 'debit' in col.lower()), None)

    # Check if both credit and debit columns are found
    if credit_column_position is not None and debit_column_position is not None:
        # Return the names of the credit and debit columns
        return [credit_column_position, debit_column_position]

    # Return an empty list if either the credit or debit column is not found
    return []

def find_relevant_columns(data_sample: pd.DataFrame) -> list:
    columns = data_sample.columns.tolist()

    # Define the (sub) keywords we're looking for in English and Spanish
    date_keywords = ['date', 'fecha'] # 'fecha' is Spanish for 'date'
    description_keywords = ['desc', 'concept'] # 'desc', 'concept' capture both English and Spanish for 'description' (descripcion)
    amount_keywords = ['amount', 'importe', 'cantidad', 'monto', 'valor'] # 'importe', 'cantidad', 'monto', 'valor' are Spanish for 'amount'

    # Find the first column that contains any date keyword (first date is often the transaction date)
    date_position = next((i for i, col in enumerate(columns) if any(keyword in col.lower() for keyword in date_keywords)), None)

    # If the column contains any date keywords, it should not be considered for description or amount
    description_position = next((i for i, col in enumerate(columns) if any(keyword in col.lower() for keyword in description_keywords) and not any(keyword in col.lower() for keyword in date_keywords)), None)
    amount_position = next((i for i, col in enumerate(columns) if any(keyword in col.lower() for keyword in amount_keywords) and not any(keyword in col.lower() for keyword in date_keywords)), None)

    # Return the positions of the found columns
    return [date_position, description_position, amount_position]




