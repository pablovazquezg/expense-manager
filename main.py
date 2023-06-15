import os
import glob
import asyncio
import pandas as pd
import langchain
from dotenv import load_dotenv
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
    os.environ['PYDEVD_DISABLE_FILE_VALIDATION'] = '1'
    load_dotenv()
    langchain.debug = True

    # Get all CSV files in the input folder

    file_paths = glob.glob(os.path.join(TX_INPUT_FOLDER, "*.CSV")) + glob.glob(os.path.join(TX_INPUT_FOLDER, "*.csv"))


    # For each file, create a new process and start it
    # for f in file_paths:
    #     await process_file(f)
    
    tasks = [process_file(file_path) for file_path in file_paths]
    await asyncio.gather(*tasks)

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
