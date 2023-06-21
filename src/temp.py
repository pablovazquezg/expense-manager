import pandas as pd
from typing import Dict, Union, Optional

async def process_file(file_path: str) -> Dict[str, Union[str, Optional[pd.DataFrame]]]:
    """
    Process the input file by reading, cleaning, standardizing, and categorizing the transactions.

    Args:
        file_path (str): Path to the input file.

    Returns:
        Dict[str, Union[str, Optional[pd.DataFrame]]]: A dictionary containing the result and optional DataFrame.
    """  

    result: Dict[str, Union[str, Optional[pd.DataFrame]]] = {'error': ''}
    try:
        tx_list = pd.read_csv(file_path, index_col=False)
        tx_list.attrs['file_path'] = file_path

        # Read file into standardized tx format: source, date, type, category, description, amount 
        tx_list = standardize_tx_format(tx_list)

        # Categorize transactions
        output = await categorize_tx_list(tx_list)
        if output is not None:
            result['output'] = output
    except Exception as e:
        result['error'] = str(e)

    return result
