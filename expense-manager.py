#!/usr/bin/env python3

# Standard library imports
import os
import sys
import glob
import logging
import asyncio
import warnings

# Third-party library imports
from dotenv import load_dotenv
import langchain

# Local application/library specific imports
from src.file_processing import manage_processed_files, save_results, process_file
from src.config import (
    TX_ARCHIVE_FOLDER,
    TX_INPUT_FOLDER,
    TX_OUTPUT_FILE,
    LOG_FILE,
    LOG_LEVEL
)

def read_args(args: list) -> bool:
    n_flag = False
    d_flag = False
    
    if args:
        for arg in args:
            if arg == '-n': # Delete previous output file and create a new one
                n_flag = True
            elif arg == '-d': # Deletes all processed files at the end of the program
                d_flag = True
            elif arg == '-nd': # Combined effects of -n and -d flags
                n_flag = True
                d_flag = True
            else:
                print(f'Invalid argument: {arg}')
                sys.exit(1)
        
    return n_flag, d_flag


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
    
    # -n flag: deletes previous output file and creates a new one
    # -d flag: deletes all processed files at the end of the program
    n_flag, d_flag = read_args(sys.argv[1:])
    if n_flag and os.path.isfile(TX_OUTPUT_FILE):
        os.remove(TX_OUTPUT_FILE)
    
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
    manage_processed_files(d_flag)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        logging.shutdown()