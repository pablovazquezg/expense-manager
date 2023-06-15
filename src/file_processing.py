import os
import glob
import shutil
import asyncio
import dateparser
import src.templates as templates
import pandas as pd
from datetime import datetime
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain

import src.templates as templates
from src.inspect_file import find_relevant_columns, find_cr_db_columns
from src.categorize_tx_list import categorize_tx_list

from src.config import (
    TX_STAGE_FOLDER,
    TX_OUTPUT_FILE,
    REF_STAGE_FOLDER,
    REF_OUTPUT_FILE,
    DATA_CHECKS_STAGE_FOLDER,
    DATA_CHECKS_OUTPUT_FILE
)

#TODO: Clean all TODOs in this file
#TODO: Add docstrings to all functions
#TODO: Add type hints to all functions
#TODO: Add tracing
#TODO: Create script to empty folders (all, or specific ones)
#TODO: Git not to upload data files
#TODO: Use concat instead of append for df
# read file and process it (e.g. categorize transactions)
async def process_file(input_file_path: str) -> None:
    # Read file (includes data cleaning and standardization)
    tx_list = read_prep_data(input_file_path)

    # Extract total amount and number of transactions for data validation purposes
    total_amount_in = tx_list["Amount"].sum()
    total_count_in = len(tx_list.index)

    # Categorize transactions
    categorized_tx_list = await categorize_tx_list(tx_list)

    # Save data checks to log file; all files will be merged at the end (see merge_interim_results() below)
    total_amount_out = categorized_tx_list["Amount"].sum()
    total_count_out = len(categorized_tx_list.index)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    new_file_name = f"{timestamp}_{os.path.basename(input_file_path)}"
    new_file_path = os.path.join(DATA_CHECKS_STAGE_FOLDER, new_file_name)
    with open(new_file_path, "w", encoding="utf-8") as file:
        file.write(f"{new_file_name}, {total_amount_in}, {total_amount_out}, {total_count_in}, {total_count_out}\n\n")
    

    # Save file to interim folder; all files will be merged at the end (see merge_interim_results() below)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    new_file_name = f"{timestamp}_{os.path.basename(input_file_path)}"
    new_file_path = os.path.join(TX_STAGE_FOLDER, new_file_name)
    categorized_tx_list.to_csv(new_file_path, index=False, header=False)


def read_prep_data(file_path: str) -> pd.DataFrame:
    tx_list = pd.read_csv(file_path, index_col=False)
    data_sample = tx_list.head(10)
    split_credits_debits = find_cr_db_columns(data_sample)

    # If C/D on different columns, consolidate (melt) them under a 'Type' column; keep  amounts in new column
    if split_credits_debits:
        all_columns = tx_list.columns.tolist()

        # Create a list of indices for columns not in split_credits_debits
        id_vars = [i for i in range(len(all_columns)) if i not in split_credits_debits]

        # Get the column names corresponding to the positions in id_vars and split_credits_debits
        id_var_names = [all_columns[i] for i in id_vars]
        value_var_names = [all_columns[i] for i in split_credits_debits]

        # Melt the DataFrame using id_var_names and value_var_names as the column names
        tx_list = tx_list.melt(id_vars=id_var_names, value_vars=value_var_names, var_name='Type', value_name='Amount')

        # Drop rows with missing values in the 'Amount' column
        tx_list.dropna(subset=['Amount'], inplace=True)
        # Refresh the data sample since the structure has changed
        data_sample = tx_list.head(10)
    
    # Locate relevant columns (Date, Description, Amount, Type)
    relevant_cols = find_relevant_columns(data_sample)

    # Keep relevant columns and rename them to standard names (across all files to be processed)
    tx_list = tx_list.iloc[:,relevant_cols]
    tx_list.columns = ['Date', 'Description', 'Amount']

    tx_list['Amount'] = standardize_amounts(tx_list['Amount'])
    
    # Insert a Category column to the DataFrame and fill it up with nulls
    tx_list["Category"] = None

    return tx_list


def standardize_amounts(amounts: pd.Series) -> pd.Series:
    # Sample a single entry to determine amount format (US vs European)
    sample_entry = amounts.iloc[0]

    # Determine format based on the sample entry
    period_count = str(sample_entry).count('.')
    comma_count = str(sample_entry).count(',')

    # If there are more commas than periods, assume European format
    if comma_count > period_count:
        # Replace the thousand separator and change the decimal separator
        amounts = amounts.astype(str).str.replace('.', '', regex=False).str.replace(',', '.')
    else:
        # Remove the thousand separator
        amounts = amounts.astype(str).str.replace(',', '', regex=False)
    
    amounts = amounts.astype(float)
    # Standardize Credits and Debits signs (assumes more Debits than Credits)
    positive_count = (amounts > 0).sum()
    negative_count = (amounts < 0).sum()
    if positive_count > negative_count:
        amounts = -amounts

    return amounts

def merge_files(in_folder: str, out_file: str) -> None:
    # Get a list of all CSV files in the input folder
    files = glob.glob(os.path.join(in_folder, "*.CSV")) + glob.glob(os.path.join(in_folder, "*.csv"))

    if files:  # Merge all interim results (if there are any)
        df = pd.concat(
            [pd.read_csv(file, header=None) for file in files], ignore_index=True
        )

        # Write contents to output file (based on file type)
        if out_file == TX_OUTPUT_FILE:
            df.columns = ["Date", "Description", "Amount", "Category"]
            df.loc[:, 'Date'] = df['Date'].apply(lambda x: dateparser.parse(x).strftime('%Y/%m/%d'))
            df.to_csv(out_file, mode="a", index=False, header=not os.path.exists(out_file))
        elif out_file == DATA_CHECKS_OUTPUT_FILE:
            df.columns = ["File", "Amount In", "Amount Out", "Records In", "Records Out"]
            df.to_csv(out_file, mode="a", index=False, header=True)
        elif out_file == REF_OUTPUT_FILE:     
            df.columns = ["Description", "Category"]       
            # Add master file to interim results
            previous_master = pd.read_csv(REF_OUTPUT_FILE, names=["Description", "Category"], header=0)
            df = df.append(previous_master, ignore_index=True)         
            
            # Drop duplicates, sort, and write to output file            
            df.drop_duplicates().sort_values(by=["Description"]).to_csv(out_file, mode="w", index=False, header=True)


def archive_files(in_folder: str, out_folder: str) -> None:
    # Get a list of all CSV files in the input folder
    files = glob.glob(os.path.join(in_folder, "*.CSV")) + glob.glob(os.path.join(in_folder, "*.csv"))

    # Move all files to output folder
    for file in files:
        shutil.move(file, out_folder)
