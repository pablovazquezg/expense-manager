# Standard library imports
import os
import glob
import shutil
import logging
import warnings
from typing import Optional, Union, Dict, List
from datetime import datetime

# Third-party library imports
import pandas as pd
from dateparser import parse

# Local application/library specific imports
from src.extract_tx_data import extract_tx_data
from src.categorize_tx_list import categorize_tx_list
from src.config import (
    REF_OUTPUT_FILE, 
    TX_OUTPUT_FILE, 
    TX_INPUT_FOLDER,
    TX_ARCHIVE_FOLDER,
    CR_VARIATIONS,
    DB_VARIATIONS)


#TODO: Clean all TODOs in this file
# Read file and process it (e.g. categorize transactions)
async def process_file(file_path: str) -> Dict[str, Union[str, pd.DataFrame]]:
    """
    Process the input file by reading, cleaning, standardizing, and categorizing the transactions.

    Args:
        file_path (str): Path to the input file.

    Returns:
        Dict[str, Union[str, pd.DataFrame]]: Dictionary containing the file name, processed output, and error information if any
    """  

    logger = logging.getLogger(__name__)
    file_name = os.path.basename(file_path)
    result= {'file_name': file_name, 'output': pd.DataFrame(), 'error': ''}
    try:
        # Read file into standardized tx format: source, date, type, category, description, amount 
        tx_list = standardize_tx_format(file_path)

        # Categorize transactions
        result['output'] = await categorize_tx_list(tx_list)
        print(f'File processed sucessfully: {file_name}')

    except Exception as e:
        # Return an error indicator and exception info
        logging.log(logging.ERROR, f"| File: {file_name} | Unexpected Error: {e}")
        print(f'ERROR processing file {file_name}: {e}')
        result['error'] = str(e)
    
    return result



def standardize_tx_format(file_path: str) -> pd.DataFrame:
    """
    Read and prepare the data from the input file.

    Args:
        file_path (str): Path to the input file.

    Returns:
        pd.DataFrame: Prepared transaction data.
    """

    tx_list = pd.read_csv(file_path, index_col=False)    
    tx_list.attrs['file_name'] = file_path
    tx_list.columns = tx_list.columns.str.lower().str.strip()

    # Extract relevant columns and determine data format
    # See 'extract_tx_data' function for more details on data formats
    tx_list, data_format = extract_tx_data(tx_list)

    # Standardize dates to YYYY/MM/DD format (ignoring non-actionable warnings)
    warnings.filterwarnings('ignore', 'Parsing dates', category=UserWarning)
    tx_list['date'] = pd.to_datetime(tx_list['date']).dt.strftime('%Y/%m/%d')
    
    # Check if credits and debits are in separate columns
    if (data_format == "CR_DB_AMOUNTS"):
        # Consolidate (melt) C/D columns under a new 'type' column; move amounts to new 'amount' column
        tx_list = tx_list.melt(id_vars=['date', 'description'], value_vars=['credit', 'debit'], var_name='type', value_name='amount')
        # Drop empty amounts and update structure to "TYPE_AMOUNTS"
        tx_list = tx_list.dropna(subset=['amount'])
        data_format = "TYPE_AMOUNTS"

    # Convert amounts to floats    
    tx_list.loc[:,'amount'] = tx_list.loc[:,'amount'].apply(
        lambda x: float(x.replace('.', '').replace(',', '.')) # European format (e.g. 1.234,56)
            if isinstance(x, str) and ',' in x and (('.' not in x) or (x.rfind('.') < x.rfind(','))) # European format (e.g. 1.234,56)
            else float(x.replace(',', '')) if isinstance(x, str) # US format (e.g. 1,234.56)
            else x
        )

    # Standardize types values and amount signs based on data format
    if (data_format == "TYPE_AMOUNTS"):
        # Standardize type to 'C' and 'D' (i.e. credits and debits)
        tx_list.loc[:,'type'] = tx_list.loc[:,'type'].apply(lambda x: 'C' if x.lower() in CR_VARIATIONS else 'D' if x.lower() in DB_VARIATIONS else None)
        # Make amount signs consistent with type (i.e. credits are positive, debits are negative)
        tx_list.loc[:, 'amount'] = tx_list.apply(lambda x: abs(x['amount']) if x['type'] == 'C' else -abs(x['amount']), axis=1)
    else: 
        # Data format is ONLY_AMOUNTS (i.e. no type or Cr/Db columns; type is determined by amount sign)
        # Standardize amounts (assuming more debits than debits, so if more positive than negatives, invert all amounts)
        count_pos = len(tx_list[tx_list['amount'] > 0])
        count_neg = len(tx_list[tx_list['amount'] < 0])
        if count_pos > count_neg:
            tx_list.loc[:, 'amount'] = -tx_list.loc[:, 'amount']

        # Standardize type based on amounts (i.e. positive amounts are credits, negative amounts are debits)
        tx_list.loc[:, 'type'] = tx_list.apply(lambda x: 'C' if x['amount'] >= 0 else 'D', axis=1)

    # Add source and reindex to desired tx format; category column is new and therefore empty
    tx_list.loc[:, 'source'] = os.path.basename(file_path)
    tx_list = tx_list.reindex(columns=['source', 'date', 'type', 'category', 'description', 'amount'])

    return tx_list


def save_results(results: List) -> None:
    """
    Merge all interim results in the input folder and write the merged results to the output file.

    Args:
        in_folder (str): Path to the input folder containing interim results.
        out_file (str): Path to the output file.

    Returns:
        None
    """

    # Concatenate all (valid) results into a single DataFrame
    # Print errors to console
    ok_files = []
    ko_files = []
    error_messages = []

    col_list = ['Source', 'Date', 'Type', 'Category', 'Description', 'Amount']
    tx_list = pd.DataFrame(columns=col_list)
    for result in results:
        if not result['error']:
            ok_files.append(result['file_name'])
            result_df = result['output']
            result_df.columns = col_list
            tx_list = pd.concat([tx_list, result_df], ignore_index=True)
        else:
            ko_files.append(result['file_name'])
            error_messages.append(f"{result['file_name']}: {result['error']}")  

    # Write contents to output file (based on file type)
    tx_list.to_csv(TX_OUTPUT_FILE, mode="a", index=False, header=not os.path.exists(TX_OUTPUT_FILE))

    new_ref_data = tx_list[['Description', 'Category']]
    if os.path.exists(REF_OUTPUT_FILE):
        # If it exists, add master file to interim results
        old_ref_data = pd.read_csv(REF_OUTPUT_FILE, names=['Description', 'Category'], header=0)
        new_ref_data = pd.concat([old_ref_data, new_ref_data], ignore_index=True)
        
    # Drop duplicates, sort, and write to create new Master File
    new_ref_data.drop_duplicates(subset=['Description']).sort_values(by=['Description']).to_csv(REF_OUTPUT_FILE, mode="w", index=False, header=True)

    # Summarize results
    print(f"\nProcessed {len(results)} files: {len(ok_files)} successful, {len(ko_files)} with errors\n")
    if len(ko_files):
        print(f"Errors in the following files:")
        for message in error_messages:
            print(f"  {message}")
        print('\n')


def archive_files() -> None:
    
    for file_name in os.listdir(TX_INPUT_FOLDER):
        source_path = os.path.join(TX_INPUT_FOLDER, file_name)
        destination_path = os.path.join(TX_ARCHIVE_FOLDER, file_name)
        shutil.move(source_path, destination_path)