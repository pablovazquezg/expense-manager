import csv
import ast
import json
import asyncio
import timeit
from io import StringIO
from typing import Any, List, Tuple
from tenacity import retry, wait_random_exponential, stop_after_attempt
import pandas as pd
import numpy as np
from rapidfuzz import process
from src.config import TX_OUTPUT_FILE
import src.templates as templates
from src.custom_classes import CatDesc

from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
from pydantic import ValidationError


def fuzzy_tx_categorization(
    row: pd.Series,
    descriptions: np.ndarray,
    description_category_pairs: pd.DataFrame,
    threshold: int = 90,
) -> Any:  # str or None
    match_results = process.extractOne(
        row["Description"], descriptions, score_cutoff=threshold
    )

    if match_results:
        return description_category_pairs.at[
            match_results[2], "Category"
        ]  # match_results[2] is the index of the matched description
    else:
        return None


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
async def categorize_tx_batch(
    chain: LLMChain,
    tx_descriptions: str,
    parser: OutputFixingParser,
    prompt: PromptTemplate,
) -> List[List]:
    """
    Run the LLM chain asynchronously on a batch of transaction descriptions.

    Args:
        chain (LLMChain): The LLMChain object to use for running the chain.
        tx_descriptions (str): A string containing the transaction descriptions to categorize.
        parser (PydanticOutputParser): The parser to use for parsing the LLM output.
        prompt (PromptTemplate): The prompt to use for running the LLM chain.

    Returns:
        List[List]: A list of lists containing the categorized transaction descriptions.
    """
    # Trim and remove newlines from tx_descriptions
    raw_result = chain.run(input_data=tx_descriptions.strip())  # result is a string
    try:
        # Try to parse raw results; manage exceptions if they occur
        json_result = json.dumps(
            {"output": ast.literal_eval(raw_result)}
        )
        parsed_result = parser.parse(json_result)
    except ValidationError as validation_error:
        print(
            f"Validation Error: {validation_error}\nRaw Result: {raw_result}\n"
        )
        parsed_result = CatDesc(output=[["LLM ERROR DESC", "LLM ERROR CAT"]])
    return parsed_result.output  # type: ignore


async def llm_tx_categorization(tx_list: pd.DataFrame) -> pd.DataFrame:
    # Create base llm model and validation parser
    llm = ChatOpenAI(temperature=0, client=Any)
    fixer_parser = OutputFixingParser.from_llm(
        parser=PydanticOutputParser(pydantic_object=CatDesc),
        llm=llm
    )

    # Create categorization prompt and chain
    prompt = PromptTemplate.from_template(template=templates.EXPENSE_CAT_TEMPLATE)    
    chain = LLMChain(llm=llm, prompt=prompt)

    # Iterate over the DataFrame in batches of 10 rows
    tasks = []
    chunksize = 10
    for i in range(0, tx_list.shape[0], chunksize):
        chunk = tx_list.iloc[i : i + chunksize]
        tx_descriptions = "\n".join(chunk["Description"])
        task = categorize_tx_batch(chain=chain, tx_descriptions=tx_descriptions, parser=fixer_parser, prompt=prompt)  # type: ignore
        tasks.append(task)

    results_list = await asyncio.gather(*tasks)

    # unpack the list of results; each result is a CatDesc object which contains a list of tuples (description-category pairs)
    categorized_descriptions = pd.DataFrame(
        [desc_cat_pair for result in results_list for desc_cat_pair in result],
        columns=["Description", "Category"],
    )

    return categorized_descriptions
