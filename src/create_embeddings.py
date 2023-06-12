import os
import dotenv
import pandas as pd

from get_embedding import get_embedding


# TODO: Remove unused files
# TODO: create new embeddings with str.lower() applied to the description
def create_embeddings(
    input_file_path: str, output_file_path: str, relevant_cols: list[int]
) -> None:
    pf_in = pd.read_csv(input_file_path)
    pf_in = pf_in[relevant_cols]

    # create embeddings
    pf_out = pd.DataFrame(
        {
            "Description": pf_in["Description"],
            "Description Embeddings": pf_in["Description"].apply(get_embedding),
            "Category": pf_in["Category"],
        }
    )

    # save to file
    pf_out.to_pickle(output_file_path)
