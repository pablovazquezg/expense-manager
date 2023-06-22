# Standard library imports
import logging
from typing import List

# Third-party library imports
import pandas as pd
import pandas.api.types as pdt

# Local application/library specific imports
from src.config import (
    TX_OUTPUT_FILE, 
    AMOUNT_VARIATIONS,
    TYPE_NAME_VARIATIONS,
    TYPE_VALUE_VARIATIONS,
    CR_VARIATIONS,
    DB_VARIATIONS,
    DESC_VARIATIONS,
    DATE_VARIATIONS,
)


def extract_tx_data(tx_list: pd.DataFrame) -> tuple:
    """
    Analyzes the transaction DataFrame and determines the format and column positions.

    Args:
        tx_list (pd.DataFrame): The transaction DataFrame to analyze.

    Returns:
        tuple: A tuple containing the format string and the column positions dictionary.

    Raises:
        ValueError: If the DataFrame does not match any known format.
    """
    
    logger = logging.getLogger(__name__)

    columns = tx_list.columns

    # Find the first column that contains any date keyword (first date is often the transaction date)
    date_col = next((col for col in columns if any(alias in col for alias in DATE_VARIATIONS)), None)
    if not date_col:
        logger.error(f"No date column found in file: {tx_list.attrs['file_name']}")
        raise ValueError("No date column found in the input data")

    # Columns containing date keywords not to be considered as description or amount columns (fixes edge cases detected)
    desc_col = next((col for col in columns if any(alias in col for alias in DESC_VARIATIONS) and not any(alias in col for alias in DATE_VARIATIONS)), None)
    if not desc_col:
        logger.error(f"No description column found in file: {tx_list.attrs['file_name']}")
        raise ValueError("No description column found in the input data")
    
    amount_col = next((col for col in columns if any(alias in col for alias in AMOUNT_VARIATIONS) and not any(alias in col for alias in DATE_VARIATIONS)), None)
        
    # Find position of the type column; if a candidate is found, check values to confirm
    type_col = None
    for col in columns:
        if any(alias in col for alias in TYPE_NAME_VARIATIONS):
            type_column_values = set(tx_list[col].str.lower().unique())
            if type_column_values.issubset(set(TYPE_VALUE_VARIATIONS)):
                type_col = col
                break    

    # Try to determine format based on type and amount columns
    if amount_col and type_col:
        # Credits/debits determined by 'type' column; all amounts are positive
        tx_list = tx_list.loc[:, [date_col, type_col, desc_col, amount_col]]
        tx_list.columns = ['date', 'type','description', 'amount']
        return tx_list, 'TYPE_AMOUNTS'
    elif amount_col:
        # Credits/debits determined by sign of 'amount' column
        tx_list = tx_list.loc[:, [date_col, desc_col, amount_col]]
        tx_list.columns = ['date', 'description', 'amount']
        return tx_list, 'ONLY_AMOUNTS'

    # No amount found; look for credit/debit columns
    cr_pos = next((col for col in tx_list.columns if col.lower() in CR_VARIATIONS), None)
    db_pos = next((col for col in tx_list.columns if col.lower() in DB_VARIATIONS), None)

    if cr_pos and db_pos:
        # Credits/debits in separate columns; all amounts are positive
        tx_list = tx_list.loc[:, [date_col, desc_col, cr_pos, db_pos]]
        tx_list.columns = ['date', 'description', 'credit', 'debit']
        return tx_list, 'CR_DB_AMOUNTS'
    else:
        logging.log(logging.ERROR, f"| File: {tx_list.attrs['file_name']} | Input file does not match any known format")
        raise ValueError("Input file does not match any known format")