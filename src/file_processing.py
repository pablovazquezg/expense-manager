# Standard library imports
import os
import glob
import shutil
import asyncio
from datetime import datetime

# Third-party library imports
import pandas as pd
from dateparser import parse

# Local application/library specific imports
from src.inspect_file import find_relevant_columns, extract_tx_data
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
async def process_file(input_file_path: str) -> None:
    """
    Process the input file by reading, cleaning, standardizing, and categorizing the transactions.

    Args:
        input_file_path (str): Path to the input file.

    Returns:
        None
    """
    # Read, clean, and standardize data
    tx_list = standardize_data(input_file_path)

    # Extract input amount and number of transactions for data validation purposes
    data_checks = [tx_list['amount'].sum(), len(tx_list.index)]

    # Categorize transactions
    categorized_tx_list = await categorize_tx_list(tx_list)

    # Extract output amount and number of transactions for data validation purposes
    data_checks.extend([categorized_tx_list['amount'].sum(), len(categorized_tx_list.index)])

    # Save output and data validation files to interim folder
    save_interim_results(input_file_path, data_checks, categorized_tx_list)



def standardize_data(file_path: str, data_format: str) -> pd.DataFrame:
    """
    Read and prepare the data from the input file.

    Args:
        file_path (str): Path to the input file.

    Returns:
        pd.DataFrame: Prepared transaction data.
    """
    
    tx_list = pd.read_csv(file_path, index_col=None)
    tx_list.columns = tx_list.columns.str.lower().str.strip()

    # Extract relevant columns and determine data format
    tx_list, data_format = extract_tx_data(tx_list)

    # Standardize dates to YYYY/MM/DD formatd
    tx_list['date'] = pd.to_datetime(tx_list['date']).dt.strftime('%Y/%m/%d')
    
    # Standardize types and amounts based on data format
    tx_list = pd.read_csv(file_path, index_col=False)
    tx_list.columns = tx_list.columns.str.lower().str.strip()
    file_format, col_positions = extract_tx_data(tx_list)

    if (file_format == "CR_DB_AMOUNTS"):
        # Consolidate (melt) C/D columns under a new 'type' column; move amounts to new 'amount' column
        tx_list = tx_list.melt(id_vars=['date', 'description'], value_vars=['credit', 'debit'], var_name='type', value_name='amount')
        # Drop empty amounts and update structure to "TYPE_AMOUNTS"
        tx_list.dropna(subset=['amount'], inplace=True)
        file_format = "TYPE_AMOUNTS"

    if (file_format == "TYPE_AMOUNTS"):
        # Standardize types
        tx_list.loc[:,'type'] = tx_list.loc[:,'type'].apply(lambda x: 'C' if x in CR_VARIATIONS else 'D' if x in DB_VARIATIONS else None)
        # Standardize amounts based on type
        tx_list.loc[:, 'amount'] = tx_list.apply(lambda x: abs(x['amount']) if x['type'] == 'C' else -abs(x['amount']), axis=1)
    else: 
        # File format is ONLY_AMOUNTS (i.e. no type or Cr/Db columns; type is determined by amount sign)
        # Standardize amounts (assuming more debits than debits, so if more positive than negatives, invert all amounts)
        count_pos = len(tx_list[tx_list['amount'] > 0])
        count_neg = len(tx_list[tx_list['amount'] < 0])
        if count_pos > count_neg:
            tx_list.loc[:, 'amount'] = -tx_list.loc[:, 'amount']

        # Standardize types based on amounts
        tx_list.loc[:, 'type'] = tx_list.apply(lambda x: 'C' if x['amount'] >= 0 else 'D', axis=1)

    # Insert Source and Category columns and reindex df to desired order
    tx_list.insert('source', os.path.basename(file_path))
    tx_list.insert('category', None)
    tx_list = tx_list.reindex(columns=['source', 'date', 'type', 'category', 'description', 'amount'])

    return tx_list


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
        elif out_file == DATA_CHECKS_OUTPUT_FILE:
            df.columns = ["File", "Amount In", "Amount Out", "Records In", "Records Out"]
            df.to_csv(out_file, mode="a", index=False, header=True)
        elif out_file == REF_OUTPUT_FILE:
            df.columns = ['Description', 'Category']
            # Add master file to interim results
            previous_master = pd.read_csv(REF_OUTPUT_FILE, names=['Description', 'Category'], header=0)
            df = pd.concat([df, previous_master], ignore_index=True)
            # Drop duplicates, sort, and write to create new Master File
            df.drop_duplicates().sort_values(by=['description']).to_csv(out_file, mode="w", index=False, header=True)



def save_interim_results(input_file_path: str, data_checks: list, categorized_tx_list: pd.DataFrame) -> None:
    """
    Save interim results to the appropriate folders.

    Args:
        input_file_path (str): Path to the input file.
        data_checks (list): Data checks results.
        categorized_tx_list (pd.DataFrame): Categorized transaction list.

    Returns:
        None
    """

    # Save data checks file to interim folder. All files will be merged at the end (see merge_interim_results() below).
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = os.path.basename(input_file_path)
    file_path = os.path.join(DATA_CHECKS_STAGE_FOLDER, f"{timestamp}_{file_name}")
    amount_in, amount_out, cunt_in, count_out = data_checks
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(f"{file_name}, {amount_in}, {amount_out}, {cunt_in}, {count_out}\n\n")

    # Save output file (with categorized transactions) to interim folder. All files will be merged at the end (see merge_interim_results() below).
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = os.path.basename(input_file_path)
    file_path = os.path.join(TX_STAGE_FOLDER, f"{timestamp}_{file_name}")
    categorized_tx_list.insert(loc=0, column='Source', value=file_name)
    categorized_tx_list.to_csv(file_path, index=False, header=False)



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