import os
import asyncio
import time
import numpy as np
import pandas as pd
from typing import Any
from datetime import datetime
from src.config import REF_OUTPUT_FILE, REF_STAGE_FOLDER
from src.categorize_tx import llm_tx_categorization, fuzzy_tx_categorization
from src.desc_similarity_search import find_similar_description


async def categorize_tx_list(tx_list: pd.DataFrame, n_cores: int = 6) -> pd.DataFrame:

    if os.path.exists(REF_OUTPUT_FILE):
        # read the historical description-category pairs
        description_category_pairs = pd.read_csv(
            REF_OUTPUT_FILE, header=None, names=["Description", "Category"]
        )
        descriptions = description_category_pairs["Description"].values

        # use fuzzy matching to find similar descriptions and assign the category
        tx_list["Category"] = tx_list.apply(
            fuzzy_tx_categorization,
            args=(
                descriptions,
                description_category_pairs,
            ),
            axis=1,
        )  # type: ignore

    # look for uncategorized transactions; if there are any, deduplicate and sort by description
    uncategorized_descriptions = (
        tx_list[tx_list["Category"].isnull()]
        .drop_duplicates(subset=["Description"])
            .sort_values(by=["Description"])
    )

    # ask the llm to categorize the remaining descriptions
    if len(uncategorized_descriptions) > 0:
        categorized_descriptions = await llm_tx_categorization(
            uncategorized_descriptions[["Description", "Category"]]
        )

        # TODO: Manage nas
        categorized_descriptions.dropna(inplace=True)

        # Save timestamped file to interim folder; all files will be merged at the end
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        file_name = f"{timestamp}_ref_stage.csv"
        file_path = os.path.join(REF_STAGE_FOLDER, file_name)
        categorized_descriptions.to_csv(file_path, index=False, header=False)

        # Add the new description-category pairs to the tx_list
        tx_list["Category"] = tx_list["Category"].fillna(
            tx_list["Description"].map(
                categorized_descriptions.set_index("Description")["Category"]
            )
        )
        # Fill the remaining NaN values in "Category" with 'Other'
        tx_list["Category"] = tx_list["Category"].fillna('Other')

    return tx_list
