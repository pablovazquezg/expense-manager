# Standard library imports
import os
import glob
import logging
import pandas as pd
import concurrent.futures

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
    LOG_FILE,
    LOG_LEVEL
)

from src.file_processing import delete_stage_files, merge_files, process_file
#TODO: Async. first, async for all files. then consider multiprocessing for multiple files at once.
#TODO: Add account
#TODO: Add Debit / Credit
#TODO: More sophisticated on the amounts

def main():
    # Set up runnning environment
    load_dotenv()
    langchain.debug = True
    logging.basicConfig(filename=LOG_FILE, level=LOG_LEVEL, format='%(asctime)s %(levelname)s %(name)s %(message)s')
    logger = logging.getLogger(__name__)
    
    # Get all CSV files in the input folder
    file_paths = glob.glob(os.path.join(TX_INPUT_FOLDER, "*.CSV")) + glob.glob(os.path.join(TX_INPUT_FOLDER, "*.csv"))

    for file in file_paths:
        process_file(file)    
    
    # Merge all interim results; append results to output files
    merge_files(DATA_CHECKS_STAGE_FOLDER, DATA_CHECKS_OUTPUT_FILE)
    merge_files(REF_STAGE_FOLDER, REF_OUTPUT_FILE)
    merge_files(TX_STAGE_FOLDER, TX_OUTPUT_FILE)

    # Archive interim files
    delete_stage_files()


if __name__ == "__main__":
    main()