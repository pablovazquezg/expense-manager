# Standard library imports
import os
from datetime import datetime

# Third-party library imports
import pandas as pd

# Local application/library specific imports
from src.config import REF_OUTPUT_FILE
from src.categorize_tx import llm_list_categorizer, fuzzy_match_list_categorizer


async def categorize_tx_list(tx_list: pd.DataFrame) -> pd.DataFrame:
    """Asynchronously categorize a list of transactions.

    This function categorizes a list of transactions using a combination of fuzzy matching
    and a language model. It looks up new transaction descriptions in the reference file
    (a combination of user input and previous executions) to minimize API calls.
    Any uncategorized transactions are sent to the language model, and new description-category
    pairs are added to the reference file.

    Args:
        tx_list (pd.DataFrame): The list of transactions to categorize.

    Returns:
        pd.DataFrame: The original DataFrame with an additional column for the category.
    """

    if os.path.exists(REF_OUTPUT_FILE):
        # Read description-category pairs from the reference file
        description_category_pairs = pd.read_csv(
            REF_OUTPUT_FILE, header=None, names=['description', 'category']
        )

        # Extract only descriptions for faster matching
        descriptions = description_category_pairs['description'].values

        # Use fuzzy matching to find similar descriptions and assign the category
        tx_list['category'] = tx_list['description'].apply(
            fuzzy_match_list_categorizer,
            args=(descriptions, description_category_pairs),
        )

    # Filter out uncategorized transactions, deduplicate, and sort by description
    uncategorized_descriptions = (
        tx_list[tx_list['category'].isnull()]
        .drop_duplicates(subset=['description'])
        .sort_values(by=['description'])
    )

    # Ask the language model to categorize the remaining descriptions
    if not uncategorized_descriptions.empty:
        categorized_descriptions = await llm_list_categorizer(
            uncategorized_descriptions[['description', 'category']]
        )

        categorized_descriptions.dropna(inplace=True)

        # Update the category for uncategorized transactions based on the language model results
        if not categorized_descriptions.empty:
            tx_list['category'] = tx_list['category'].fillna(
                tx_list['description'].map(
                    categorized_descriptions.set_index('description')['category']
                )
            )
        
        # Fill remaining NaN values in 'category' with 'Other'
        tx_list['category'] = tx_list['category'].fillna('Other')

    return tx_list
