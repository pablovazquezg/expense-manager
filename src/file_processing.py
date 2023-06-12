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
from src.inspect_file import inspect_file
from src.categorize_tx_list import categorize_tx_list

from src.config import (
    TX_STAGE_FOLDER,
    TX_OUTPUT_FILE,
    REF_STAGE_FOLDER,
    REF_OUTPUT_FILE,
    DATA_CHECKS_STAGE_FOLDER,
    DATA_CHECKS_OUTPUT_FILE
)


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
        file.write(f"{file_name}: Total amount in: {total_amount_in}, Total amount out: {total_amount_out}, Total count in: {total_count_in}, Total count out: {total_count_out}\n\n")
    

    # Save file to interim folder; all files will be merged at the end (see merge_interim_results() below)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    file_name = f"{timestamp}_tx_stage.csv"
    file_path = os.path.join(TX_STAGE_FOLDER, file_name)
    categorized_tx_list.to_csv(file_path, index=False, header=False)


def read_file(file_path: str) -> pd.DataFrame:
    
    tx_list = pd.read_csv(file_path)
    file_sample = tx_list.head(10).to_string(index=False)

    split_credits_debits = inspect_file(file_sample, templates.CHECK_SPLIT_CREDITS_DEBITS)

    # If C/D on different columns, consolidate (melt) them under a 'Type' column; keep  amounts in new column
    if split_credits_debits:
        # Identify the columns to pass as id_vars to melt
        all_columns = tx_list.columns.tolist()
        id_vars = [col for col in all_columns if col not in split_credits_debits]
        tx_list = tx_list.melt(id_vars=id_vars, value_vars=split_credits_debits, var_name='Type', value_name='Amount')
        tx_list.dropna(subset=['Amount'], inplace=True)

    # Locate relevant columns (Date, Description, Amount, Type)
    relevant_cols = inspect_file(file_sample, templates.RELEVANT_COLS_TEMPLATE)

    # Create array of desired column names
    standard_cols = ['Date', 'Description', 'Amount']
    if len(relevant_cols) == 4:
        standard_cols.append('Type')

    # Keep relevant columns and rename them to standard names (across all files to be processed)
    tx_list = tx_list.loc[:,relevant_cols].rename(columns=dict(zip(relevant_cols, standard_cols)))

    # If input file contains tx type (debit/credit), take it from there; otherwise, infer it from the amount
    if "Type" in tx_list.columns:
        # if there is a type, make debit/credit values consistent: negative for debits, positive for credits
        tx_list['Type'] = tx_list['Type'].map({'Debit': 'D', 'Credit': 'C', 'DEBIT': 'D', 'CREDIT': 'C'})
        tx_list.loc[tx_list["Type"] == "D", "Amount"] = -abs(tx_list["Amount"])
        tx_list.loc[tx_list["Type"] == "C", "Amount"] = abs(tx_list["Amount"])
    else:
        # add a column for the transaction type
        tx_list.insert(1, "Type", "")

        # If positive amounts are more, negate the sign for all transactions (assumption is there are more debits than credits)
        positive_count = (tx_list["Amount"] > 0).sum()
        negative_count = (tx_list["Amount"] < 0).sum()
        if positive_count > negative_count:
            tx_list.loc[:,"Amount"] = -tx_list.loc[:,"Amount"]

        # Update the 'Type' column
        tx_list.loc[tx_list["Amount"] < 0, "Type"] = "D"
        tx_list.loc[tx_list["Amount"] >= 0, "Type"] = "C"

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

        # TODO: Name columns
        # Append results to output file
        write_header = False
        if out_file == TX_OUTPUT_FILE:
            write_header = not os.path.exists(out_file)
            df.columns = ["Date", "Type", "Amount", "Description", "Category"]
            df.loc[:, "Date"] = pd.to_datetime(df.loc[:, "Date"]).dt.date
        elif out_file == DATA_CHECKS_OUTPUT_FILE:
            write_header = True
            df.columns = ["File", "Amount In", "Amount Out", "Records In", "Records Out"]

        df.to_csv(out_file, mode="a", index=False, header=write_header)


def archive_files(in_folder: str, out_folder: str) -> None:
    # Get a list of all CSV files in the input folder
    files = glob.glob(os.path.join(in_folder, "*.csv"))

    # Move all files to output folder
    for file in files:
        shutil.move(file, out_folder)
