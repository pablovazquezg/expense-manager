# Standard library imports
import os
import glob
import shutil
import asyncio
from typing import Tuple
from datetime import datetime

# Third-party library imports
import pandas as pd
from dateparser import parse

# Local application/library specific imports
from src.inspect_file import extract_tx_data
from src.categorize_tx_list import categorize_tx_list
from src.config import (
    DATA_CHECKS_STAGE_FOLDER,
    DATA_CHECKS_OUTPUT_FILE,
    REF_OUTPUT_FILE,
    TX_STAGE_FOLDER, 
    TX_OUTPUT_FILE, 
    REF_STAGE_FOLDER,
    CR_VARIATIONS,
    DB_VARIATIONS)


#TODO: Clean all TODOs in this file
#TODO: Git not to upload data files
#TODO: Dates and amount signs, divisa management
#TODO: Remove all print statements and amounts

# Read file and process it (e.g. categorize transactions)
async def process_file(input_file_path: str) -> Tuple[str, bool, str]:
    """
    Process the input file by reading, cleaning, standardizing, and categorizing the transactions.

    Args:
        input_file_path (str): Path to the input file.

    Returns:
        None
    """
    # TODO: Update this if not using return values
    try:
        # Read file into standardized tx format: source, date, type, category, description, amount 
        tx_list = standardize_tx_format(input_file_path)

        # Categorize transactions
        categorized_tx_list = await categorize_tx_list(tx_list)

        # Save output file to interim folder
        save_interim_results(input_file_path, categorized_tx_list)
    except Exception as e:
        # Return an error indicator and exception info
        return (input_file_path, False, str(e))
    
    return (input_file_path, True, "Success")



def standardize_tx_format(file_path: str) -> pd.DataFrame:
    """
    Read and prepare the data from the input file.

    Args:
        file_path (str): Path to the input file.

    Returns:
        pd.DataFrame: Prepared transaction data.
    """
    
    tx_list = pd.read_csv(file_path, index_col=False)
    tx_list.columns = tx_list.columns.str.lower().str.strip()

    # Extract relevant columns and determine data format
    # See 'extract_tx_data' function for more details on data formats
    tx_list, data_format = extract_tx_data(tx_list)

    # Standardize dates to YYYY/MM/DD format
    tx_list['date'] = pd.to_datetime(tx_list['date'], infer_datetime_format=True).dt.strftime('%Y/%m/%d')
    
    # Check if credits and debits are in separate columns
    if (data_format == "CR_DB_AMOUNTS"):
        # Consolidate (melt) C/D columns under a new 'type' column; move amounts to new 'amount' column
        tx_list = tx_list.melt(id_vars=['date', 'description'], value_vars=['credit', 'debit'], var_name='type', value_name='amount')
        # Drop empty amounts and update structure to "TYPE_AMOUNTS"
        tx_list = tx_list.dropna(subset=['amount'])
        data_format = "TYPE_AMOUNTS"

    # Convert amounts to floats    
    tx_list.loc[:,'amount'] = tx_list.loc[:,'amount'].apply(
        lambda x: float(x.replace('.', '').replace(',', '.')) 
            if isinstance(x, str) and ',' in x and (('.' not in x) or (x.rfind('.') < x.rfind(',')))
            else float(x.replace(',', '')) if isinstance(x, str) 
            else x
        )

    # Standardize types values and amount signs based on data format
    if (data_format == "TYPE_AMOUNTS"):
        # Standardize types
        tx_list.loc[:,'type'] = tx_list.loc[:,'type'].apply(lambda x: 'C' if x.lower() in CR_VARIATIONS else 'D' if x.lower() in DB_VARIATIONS else None)
        # Standardize amounts based on type
        tx_list.loc[:, 'amount'] = tx_list.apply(lambda x: abs(x['amount']) if x['type'] == 'C' else -abs(x['amount']), axis=1)
    else: 
        # Data format is ONLY_AMOUNTS (i.e. no type or Cr/Db columns; type is determined by amount sign)
        # Standardize amounts (assuming more debits than debits, so if more positive than negatives, invert all amounts)
        count_pos = len(tx_list[tx_list['amount'] > 0])
        count_neg = len(tx_list[tx_list['amount'] < 0])
        if count_pos > count_neg:
            tx_list.loc[:, 'amount'] = -tx_list.loc[:, 'amount']

        # Standardize types based on amounts
        tx_list.loc[:, 'type'] = tx_list.apply(lambda x: 'C' if x['amount'] >= 0 else 'D', axis=1)

    # Add source and reindex to desired tx format; category column is new and therefore empty
    tx_list.loc[:, 'source'] = os.path.basename(file_path)
    tx_list = tx_list.reindex(columns=['source', 'date', 'type', 'category', 'description', 'amount'])

    return tx_list


def save_interim_results(processed_file: str, categorized_tx_list: pd.DataFrame) -> None:
    """
    Save interim results to the appropriate folders.

    Args:
        input_file_path (str): Path to the input file.
        data_checks (list): Data checks results.
        categorized_tx_list (pd.DataFrame): Categorized transaction list.

    Returns:
        None
    """
    #TODO: Remove TODOs
    #TODO: Update docstrings
    # Save file with categorized transactions to interim folder
    # All interim files will be merged at the end to create the final output file
    # See 'merge_files' function for more details
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = os.path.basename(processed_file)
    file_path = os.path.join(TX_STAGE_FOLDER, f"{timestamp}_{file_name}")
    categorized_tx_list.to_csv(file_path, index=False, header=False)


def merge_files(in_folder: str, out_file: str) -> None:
    """
    Merge all interim results in the input folder and write the merged results to the output file.

    Args:
        in_folder (str): Path to the input folder containing interim results.
        out_file (str): Path to the output file.

    Returns:
        None
    """

    # Get a list of all CSV files in the input folder
    files = glob.glob(os.path.join(in_folder, "*.CSV")) + glob.glob(os.path.join(in_folder, "*.csv"))

    if files:  # Merge all interim results (if there are any)
        df = pd.concat(
            [pd.read_csv(file, header=None) for file in files], ignore_index=True
        )

        # Write contents to output file (based on file type)
        if out_file == TX_OUTPUT_FILE:
            df.columns = ['Source', 'Date', 'Type', 'Category', 'Description', 'Amount']            
            df.to_csv(out_file, mode="a", index=False, header=not os.path.exists(out_file))
        elif out_file == REF_OUTPUT_FILE:
            df.columns = ['Description', 'Category']
            # Add master file to interim results
            previous_master = pd.read_csv(REF_OUTPUT_FILE, names=['Description', 'Category'], header=0)
            df = pd.concat([df, previous_master], ignore_index=True)
            # Drop duplicates, sort, and write to create new Master File
            df.drop_duplicates(subset=['Description']).sort_values(by=['Description']).to_csv(out_file, mode="w", index=False, header=True)
        else:
            raise ValueError("Invalid output file type.")


def delete_stage_files() -> None:
    """
    Delete all files in the input folder.

    Args:
        in_folder (str): Path to the input folder containing the files to be deleted.

    Returns:
        None
    """

    for folder in [DATA_CHECKS_STAGE_FOLDER, REF_STAGE_FOLDER, TX_STAGE_FOLDER]:
        files = glob.glob(os.path.join(folder, "*.CSV")) + glob.glob(os.path.join(folder, "*.csv"))
        for file in files:
            os.remove(file)