# Standard library imports
from typing import List

# Third-party library imports
import pandas as pd
import pandas.api.types as pdt

# Local application/library specific imports
from src.config import (
    DATA_CHECKS_STAGE_FOLDER,
    DATA_CHECKS_OUTPUT_FILE,
    TX_STAGE_FOLDER, 
    TX_OUTPUT_FILE, 
    REF_STAGE_FOLDER,
    AMOUNT_VARIATIONS,
    TYPE_NAME_VARIATIONS,
    TYPE_VALUE_VARIATIONS,
    CR_VARIATIONS,
    DB_VARIATIONS,
    DESC_VARIATIONS,
    DATE_VARIATIONS,
)


#TODO: Refactor all code
def determine_tx_format(tx_list: pd.DataFrame) -> tuple:
    """
    Analyzes the transaction DataFrame and determines the format and column positions.

    Args:
        tx_list (pd.DataFrame): The transaction DataFrame to analyze.

    Returns:
        tuple: A tuple containing the format string and the column positions dictionary.

    Raises:
        ValueError: If the DataFrame does not match any known format.
    """
    columns = tx_list.columns

    # Find the first column that contains any date keyword (first date is often the transaction date)
    date_pos = next((col for col in columns if col in DATE_VARIATIONS), None)

    # Columns containing date keywords not to be considered for description or amount (fixes edge cases detected)
    desc_pos = next((col for col in columns if (col in DESCRIPTION_VARIATIONS and not col in DATE_VARIATIONS)), None)
    amount_position = next((i for i, col in enumerate(columns) if any(keyword in col for keyword in AMOUNT_VARIATIONS) and not any(keyword in col for keyword in DATE_VARIATIONS)), None)

    # Find position of the amount column (if any)
    col_positions['amount'] = next(, None)

    # Find position of the type column; if a candidate is found, check if it contains valid values.
    type_col = next((col for col in tx_list.columns if col.lower() in TYPE_VARIATIONS), None)
    if type_col:
        type_column_values = set(tx_list[type_col].str.lower().unique())
        if type_column_values.issubset(set(CR_VARIATIONS + DB_VARIATIONS)):
            col_positions['type'] = type_col
    

    # Try to determine format based on type and amount columns
    if 'amount' in col_positions and 'type' in col_positions:
        return 'TYPE_AMOUNTS', col_positions
    elif 'amount' in col_positions:
        return 'ONLY_AMOUNTS', col_positions

    # No amount found; look for credit and debit columns
    col_positions['credit'] = next((col for col in tx_list.columns if col.lower() in CR_VARIATIONS), None)
    col_positions['debit'] = next((col for col in tx_list.columns if col.lower() in DB_VARIATIONS), None)

    if col_positions['credit'] and col_positions['debit']:
        return 'CR_DB_AMOUNTS', col_positions

    raise ValueError("The DataFrame does not match any known format")



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



    # Raise exception if either field is not found; they are all necessary
    if date_position is None or description_position is None or amount_position is None:
        raise Exception('Could not find all relevant columns (date, description, amount)')
    
    # Return the positions of the found columns
    return [date_position, description_position, amount_position]