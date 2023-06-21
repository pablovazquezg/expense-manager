# DATA FOLDERS
REF_OUTPUT_FILE = 'data/ref_data/ref_master_data.csv'
TX_INPUT_FOLDER = 'data/tx_data/input/'
TX_OUTPUT_FILE = 'data/tx_data/output/tx_master_data.csv'
TX_ARCHIVE_FOLDER = 'data/tx_data/archive/'

# STRING VARIATIONS
CR_VARIATIONS = frozenset(['credit', 'cr', 'cr.', 'c'])
DB_VARIATIONS = frozenset(['debit', 'dr', 'dr.', 'd'])
AMOUNT_VARIATIONS = frozenset(['amount', 'cantidad', 'monto', 'importe', 'valor'])
TYPE_NAME_VARIATIONS = frozenset(['type', 'tipo'])
TYPE_VALUE_VARIATIONS = frozenset(['credit', 'cr', 'cr.', 'c', 'debit', 'dr', 'dr.', 'd'])
DATE_VARIATIONS = frozenset(['date', 'fecha'])
DESC_VARIATIONS = frozenset(['desc', 'desc.', 'description', 'descripción', 'concepto'])

# LLM CONFIG
TX_PER_LLM_RUN = 10 # Tx to process per LLM run; higher values tend to result in output errors

# LOG CONFIG
LOG_FILE = 'logs/app.log'
LOG_LEVEL = 'ERROR'
