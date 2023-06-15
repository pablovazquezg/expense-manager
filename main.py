# Standard library imports
import asyncio
import glob
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# Third-party library imports
import langchain
import pandas as pd
from dotenv import load_dotenv

# Local application/library specific imports
from src.config import (
    DATA_CHECKS_ARCHIVE_FOLDER,
    DATA_CHECKS_OUTPUT_FILE,
    DATA_CHECKS_STAGE_FOLDER,
    REF_ARCHIVE_FOLDER,
    REF_OUTPUT_FILE,
    REF_STAGE_FOLDER,
    TX_ARCHIVE_FOLDER,
    TX_INPUT_FOLDER,
    TX_OUTPUT_FILE,
    TX_STAGE_FOLDER,
)

from src.file_processing import delete_stage_files, merge_files, process_file


async def main():
    # Load environment variables from .env file
    load_dotenv()

    # Get all CSV files in the input folder
    file_paths = glob.glob(os.path.join(TX_INPUT_FOLDER, "*.CSV")) + glob.glob(os.path.join(TX_INPUT_FOLDER, "*.csv"))

    # Enable debug mode for langchain
    langchain.debug = True

    # Create tasks for processing each file asynchronously
    tasks = [process_file(file_path) for file_path in file_paths]
    await asyncio.gather(*tasks)

    # Merge all interim results; append results to output files
    merge_files(DATA_CHECKS_STAGE_FOLDER, DATA_CHECKS_OUTPUT_FILE)
    merge_files(REF_STAGE_FOLDER, REF_OUTPUT_FILE)
    merge_files(TX_STAGE_FOLDER, TX_OUTPUT_FILE)

    # Archive interim files
    delete_stage_files()


if __name__ == "__main__":
    asyncio.run(main())