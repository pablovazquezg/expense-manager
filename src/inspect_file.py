# Standard library imports
from typing import List

# Third-party library imports
import pandas as pd

def find_cr_db_columns(data_sample: pd.DataFrame) -> List[int]:
    """
    Find the positions of the credit and debit columns in the DataFrame.

    Args:
        data_sample (pd.DataFrame): Sample data to search for credit and debit columns.

    Returns:
        List[int]: Positions of the credit and debit columns (or an empty list if not found).
    """

    # Convert the column names of the DataFrame to lowercase
    columns = [col.lower() for col in data_sample.columns]

    # Find the position of the column containing 'credit' in its name (case-insensitive)
    credit_column_position = next((i for i, col in enumerate(columns) if 'credit' in col), None)

    # Find the position of the column containing 'debit' in its name (case-insensitive)
    debit_column_position = next((i for i, col in enumerate(columns) if 'debit' in col), None)

    # Return credit and debit columns (or an empty list if not found)
    if credit_column_position is not None and debit_column_position is not None:
        return [credit_column_position, debit_column_position] 
    else:
        return []



def find_relevant_columns(data_sample: pd.DataFrame) -> List[int]:
    """
    Find the positions of the relevant columns (date, description, amount) in the DataFrame.

    Args:
        data_sample (pd.DataFrame): Sample data to search for relevant columns.

    Returns:
        List[int]: Positions of the relevant columns.
    """
    
    # Convert the column names of the DataFrame to lowercase
    columns = [col.lower() for col in data_sample.columns]

    # Define the (sub) keywords we're looking for in English and Spanish
    date_keywords = ['date', 'fecha']  # 'fecha' is Spanish for 'date'
    description_keywords = ['desc', 'concept']  # 'desc', 'concept' capture both English and Spanish for 'description' (descripcion)
    amount_keywords = ['amount', 'importe', 'cantidad', 'monto', 'valor']  # 'importe', 'cantidad', 'monto', 'valor' are Spanish for 'amount'

    # Find the first column that contains any date keyword (first date is often the transaction date)
    date_position = next((i for i, col in enumerate(columns) if any(keyword in col for keyword in date_keywords)), None)

    # If the column contains any date keywords, it should not be considered for description or amount
    description_position = next((i for i, col in enumerate(columns) if any(keyword in col for keyword in description_keywords) and not any(keyword in col for keyword in date_keywords)), None)
    amount_position = next((i for i, col in enumerate(columns) if any(keyword in col for keyword in amount_keywords) and not any(keyword in col for keyword in date_keywords)), None)

    # Raise exception if either field is not found; they are all necessary
    if date_position is None or description_position is None or amount_position is None:
        raise Exception('Could not find all relevant columns (date, description, amount)')
    
    # Return the positions of the found columns
    return [date_position, description_position, amount_position]