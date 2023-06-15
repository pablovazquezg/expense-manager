from dataclasses import dataclass

@dataclass
class DataFolders:
    REF_STAGE_FOLDER = "data/ref_data/interim/"
    REF_OUTPUT_FILE = "data/ref_data/output/ref_master_data.csv"
    REF_ARCHIVE_FOLDER = "data/ref_data/archive/"

    DATA_CHECKS_STAGE_FOLDER = "data/checks/interim/"
    DATA_CHECKS_OUTPUT_FILE = "data/checks/output/checks_master_data.csv"
    DATA_CHECKS_ARCHIVE_FOLDER = "data/checks/archive/"

    TX_INPUT_FOLDER = "data/tx_data/input/"
    TX_STAGE_FOLDER = "data/tx_data/interim/"
    TX_OUTPUT_FILE = "data/tx_data/output/tx_master_data.csv"
    TX_ARCHIVE_FOLDER = "data/tx_data/archive/"
