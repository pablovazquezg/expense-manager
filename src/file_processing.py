import os
import glob
import shutil
import asyncio
import src.templates as templates
import pandas as pd
from datetime import datetime
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain

import src.templates as templates
from src.inspect_file import inspect_data
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
# read file and process it (e.g. categorize transactions)
async def process_file(file_path: str) -> None:
    # Read file (includes data cleaning and standardization)
    tx_list = read_file(file_path)

    # Extract total amount and number of transactions for data validation purposes
    total_amount_in = tx_list["Amount"].sum()
    total_count_in = len(tx_list.index)

    # Categorize transactions
    categorized_tx_list = await categorize_tx_list(tx_list)

    # Save data checks to log file; all files will be merged at the end (see merge_interim_results() below)
    total_amount_out = categorized_tx_list["Amount"].sum()
    total_count_out = len(categorized_tx_list.index)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    file_name = f"data_checks_{timestamp}.csv"
    file_path = os.path.join(DATA_CHECKS_STAGE_FOLDER, file_name)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(f"{file_name}, {total_amount_in}, {total_amount_out}, {total_count_in}, {total_count_out}\n\n")
    

    # Save file to interim folder; all files will be merged at the end (see merge_interim_results() below)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    file_name = f"{timestamp}_tx_stage.csv"
    file_path = os.path.join(TX_STAGE_FOLDER, file_name)
    categorized_tx_list.to_csv(file_path, index=False, header=False)


def read_file(file_path: str) -> pd.DataFrame:
    
    tx_list = pd.read_csv(file_path)
    data_sample = tx_list.head(10).to_string(index=False)
    split_credits_debits = inspect_data(data_sample, templates.CHECK_SPLIT_CREDITS_DEBITS)

    # If C/D on different columns, consolidate (melt) them under a 'Type' column; keep  amounts in new column
    if split_credits_debits:
        # Identify the columns to pass as id_vars to melt
        all_columns = tx_list.columns.tolist()
        id_vars = [col for col in all_columns if col not in split_credits_debits]
        tx_list = tx_list.melt(id_vars=id_vars, value_vars=split_credits_debits, var_name='Type', value_name='Amount')
        tx_list.dropna(subset=['Amount'], inplace=True)

    # Locate relevant columns (Date, Description, Amount, Type)
    data_sample = tx_list.head(0).to_string(index=False)
    relevant_cols = inspect_data(data_sample, templates.RELEVANT_COLS_TEMPLATE)

    # Create array of desired column names
    standard_cols = ['Date', 'Description', 'Amount']

    # Keep relevant columns and rename them to standard names (across all files to be processed)
    tx_list = tx_list.loc[:,relevant_cols].rename(columns=dict(zip(relevant_cols, standard_cols)))

    # Standardize Credits and Debits signs (assumes more Debits than Credits)
    positive_count = (tx_list["Amount"] > 0).sum()
    negative_count = (tx_list["Amount"] < 0).sum()
    if positive_count > negative_count:
        tx_list.loc[:,"Amount"] = -tx_list.loc[:,"Amount"]

    # Insert a Category column to the DataFrame and fill it up with nulls
    tx_list["Category"] = None

    return tx_list


def merge_files(in_folder: str, out_file: str) -> None:
    # Get a list of all CSV files in the input folder
    files = glob.glob(os.path.join(in_folder, "*.csv"))

    if files:  # Merge all interim results (if there are any)
        df = pd.concat(
            [pd.read_csv(file, header=None) for file in files], ignore_index=True
        )

        # Write contents to output file (based on file type)
        if out_file == TX_OUTPUT_FILE:
            df.columns = ["Date", "Description", "Amount", "Category"]
            df.loc[:, "Date"] = pd.to_datetime(df.loc[:, "Date"]).dt.date
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
    files = glob.glob(os.path.join(in_folder, "*.csv"))

    # Move all files to output folder
    for file in files:
        shutil.move(file, out_folder)
