import os
import glob
import asyncio
import pandas as pd
import langchain
from aiomultiprocess import Pool
from dotenv import load_dotenv
from multiprocessing import Process
from src.file_processing import process_file, merge_files, archive_files
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.config import (
    DATA_CHECKS_OUTPUT_FILE,
    DATA_CHECKS_STAGE_FOLDER,
    DATA_CHECKS_ARCHIVE_FOLDER,
    REF_OUTPUT_FILE,
    REF_STAGE_FOLDER,
    REF_ARCHIVE_FOLDER,
    TX_OUTPUT_FILE,
    TX_STAGE_FOLDER,
    TX_ARCHIVE_FOLDER,
    TX_INPUT_FOLDER,
)


async def main():
    load_dotenv()
    langchain.debug = True

    # Get all CSV files in the input folder
    csv_files = glob.glob(os.path.join(TX_INPUT_FOLDER, "*.csv"))
    CSV_files = glob.glob(os.path.join(TX_INPUT_FOLDER, "*.CSV"))
    file_paths = csv_files + CSV_files

    for f in file_paths:
        await process_file(f)
    # For each file, create a new process and start it
    # async with Pool() as pool:
    #     results = await pool.map(process_file, file_paths)

    # Merge all interim results; append results to output files
    merge_files(DATA_CHECKS_STAGE_FOLDER, DATA_CHECKS_OUTPUT_FILE)
    merge_files(REF_STAGE_FOLDER, REF_OUTPUT_FILE)
    merge_files(TX_STAGE_FOLDER, TX_OUTPUT_FILE)

    # TODO: Deduplicate and sort reference master data file
    # Archive interim files
    archive_files(DATA_CHECKS_STAGE_FOLDER, DATA_CHECKS_ARCHIVE_FOLDER)
    archive_files(REF_STAGE_FOLDER, REF_ARCHIVE_FOLDER)
    archive_files(TX_STAGE_FOLDER, TX_ARCHIVE_FOLDER)


if __name__ == "__main__":
    asyncio.run(main())
