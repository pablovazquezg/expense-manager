# Standard library imports
import os
from datetime import datetime

# Third-party library imports
import pandas as pd

# Local application/library specific imports
from src.config import REF_OUTPUT_FILE, REF_STAGE_FOLDER
from src.categorize_tx import llm_tx_categorization, fuzzy_tx_categorization


async def categorize_tx_list(tx_list: pd.DataFrame) -> pd.DataFrame:
    """
    Asynchronously categorizes a list of transactions.
    
    New transaction descriptions are looked up in the reference file (combination 
    of user input and previous executions) to minimize the number of API calls. Any
    uncategorized transactions are sent to the llm, and new description-category pairs
    are added to the reference file.

    Parameters:
    tx_list (pd.DataFrame): The list of transactions to categorize.

    Returns:
    pd.DataFrame: The original dataframe with an additional column for the category.
    """

    if os.path.exists(REF_OUTPUT_FILE):
        # Read description-category pairs reference file
        description_category_pairs = pd.read_csv(
            REF_OUTPUT_FILE, header=None, names=["Description", "Category"]
        )

        # Extract only descriptions for faster matching
        descriptions = description_category_pairs["Description"].values

        # Use fuzzy matching to find similar descriptions and assign the category
        tx_list["Category"] = tx_list["Description"].apply(
            fuzzy_tx_categorization,
            args=(
                descriptions,
                description_category_pairs,
            ),
        )

    # Look for uncategorized transactions; deduplicate and sort by description
    uncategorized_descriptions = (
        tx_list[tx_list["Category"].isnull()]
        .drop_duplicates(subset=["Description"])
        .sort_values(by=["Description"])
    )

    # Ask llm to categorize remaining descriptions
    if len(uncategorized_descriptions) > 0:
        categorized_descriptions = await llm_tx_categorization(
            uncategorized_descriptions[["Description", "Category"]]
        )

        categorized_descriptions.dropna(inplace=True)

        # Save timestamped file to interim folder; all files will be merged at the end
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        file_name = f"{timestamp}_ref_stage.csv"
        file_path = os.path.join(REF_STAGE_FOLDER, file_name)
        categorized_descriptions.to_csv(file_path, index=False, header=False)

        # Add new description-category pairs to the tx_list
        tx_list["Category"] = tx_list["Category"].fillna(
            tx_list["Description"].map(
                categorized_descriptions.set_index("Description")["Category"]
            )
        )
        
        # Fill remaining NaN values in "Category" with 'Other'
        tx_list["Category"] = tx_list["Category"].fillna('Other')

    return tx_list
