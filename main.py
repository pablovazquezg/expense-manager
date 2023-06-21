# Standard library imports
import os
import glob
import logging
import pandas as pd
import concurrent.futures

# Third-party library imports
import asyncio
import langchain
import pandas as pd
from dotenv import load_dotenv

# Local application/library specific imports
from src.config import (
    REF_OUTPUT_FILE,
    TX_ARCHIVE_FOLDER,
    TX_INPUT_FOLDER,
    TX_OUTPUT_FILE,
    LOG_FILE,
    LOG_LEVEL
)

from src.file_processing import archive_files, save_results, process_file
#TODO: Bring back data checks and alert user when there are issues
async def main():
    # Set up runnning environment
    load_dotenv()
    langchain.debug = False
    logging.basicConfig(filename=LOG_FILE, level=LOG_LEVEL, format='%(asctime)s %(levelname)s %(name)s %(message)s')
    logger = logging.getLogger(__name__)

    # Get all CSV files in the input folder
    file_paths = glob.glob(os.path.join(TX_INPUT_FOLDER, "*.CSV")) + glob.glob(os.path.join(TX_INPUT_FOLDER, "*.csv"))

    tasks = []
    for file_path in file_paths:
        tasks.append(process_file(file_path))

    # Run all tasks concurrently
    print('\nProcessing files...')
    results = await asyncio.gather(*tasks)

    # Save results to file
    save_results(results)

    #TODO: Uncomment when data checks are implemented
    # Archive input files
    # archive_files()


if __name__ == "__main__":
    asyncio.run(main())