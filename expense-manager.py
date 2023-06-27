#!/usr/bin/env python3

# Standard library imports
import os
import glob
import logging
import asyncio
import warnings

# Third-party library imports
from dotenv import load_dotenv
import langchain

# Local application/library specific imports
from src.file_processing import archive_files, save_results, process_file
from src.config import (
    TX_ARCHIVE_FOLDER,
    TX_INPUT_FOLDER,
    LOG_FILE,
    LOG_LEVEL
)


async def main():
    """
    Main function to initialize environment, process CSV files, 
    save the results, and archive the processed files.
    """
    # Filter out UserWarnings related to DateTime parsing; these are expected since date format is inferred
    warnings.filterwarnings("ignore", category=UserWarning, message='^Could not infer format*')

    load_dotenv()
    
    # Set langchain's debug level
    langchain.debug = False
    
    # Configure logging with file, level, and format
    logging.basicConfig(filename=LOG_FILE, level=LOG_LEVEL, format='%(asctime)s %(levelname)s %(name)s %(message)s')
    logger = logging.getLogger(__name__)

    # Create and run an asyncio task to process each file
    file_paths = glob.glob(os.path.join(TX_INPUT_FOLDER, "*.csv"), recursive=True) + glob.glob(os.path.join(TX_INPUT_FOLDER, "*.CSV"), recursive=True)    
    tasks = [process_file(file_path) for file_path in file_paths]

    print('\nProcessing files...')    
    results = await asyncio.gather(*tasks)

    # Save results to output file and archive input files
    save_results(results)
    archive_files()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        logging.shutdown()