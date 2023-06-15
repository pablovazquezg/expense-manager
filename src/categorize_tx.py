# Standard library imports
import ast
import json
from typing import Any, List, Tuple, Optional

# Third-party library imports
import asyncio
import numpy as np
import pandas as pd
from pydantic import ValidationError
from rapidfuzz import process
from tenacity import retry, wait_random_exponential, stop_after_attempt

# Local application/library specific imports
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
from langchain.prompts import PromptTemplate
import src.templates as templates
from src.custom_classes import Desc_Categ_Pair
from src.config import REF_OUTPUT_FILE, REF_STAGE_FOLDER


def fuzzy_tx_categorization(
    description: str,
    descriptions: np.ndarray,
    description_category_pairs: pd.DataFrame,
    threshold: int = 90,
) -> Optional[str]:
    """Find a fuzzy match for the transaction description and return its category.
    
    Args:
        description (str): The transaction description to categorize.
        descriptions (np.ndarray): The array of descriptions to match against.
        description_category_pairs (pd.DataFrame): DataFrame containing description-category pairs.
        threshold (int): The matching score threshold.

    Returns:
        str or None: The category of the matched description, or None if no match found.
    """

    # Fuzzy-match this description against the reference descriptions
    match_results = process.extractOne(description, descriptions, score_cutoff=threshold)

    # If a match is found, return the category of the matched description
    if match_results:
        return description_category_pairs.at[match_results[2], "Category"]
    
    return None



@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
async def categorize_tx_batch(
    chain: LLMChain,
    tx_descriptions: str,
    parser: OutputFixingParser,
    prompt: PromptTemplate,
) -> List[Tuple]:
    """Categorize a batch of transactions using a LLM
    
    Args:
        chain (LLMChain): The LLMChain object to use for running the chain.
        tx_descriptions (str): A string containing the transaction descriptions to categorize.
        parser (OutputFixingParser): The parser to use for parsing the LLM output.
        prompt (PromptTemplate): The prompt to use for running the LLM chain.

    Returns:
        List[Tuple]: A list of tuples containing the categorized transaction descriptions.
    """

    # Trim and remove newlines from tx_descriptions
    raw_result = chain.run(input_data=tx_descriptions.strip())
    
    try:
        # Try to parse raw results; manage exceptions if they occur
        json_result = json.dumps({"output": ast.literal_eval(raw_result)})
        parsed_result = parser.parse(json_result)
    except ValidationError as validation_error:
        print(f"Validation Error: {validation_error}\nRaw Result: {raw_result}\n")
        parsed_result = Desc_Categ_Pair(output=[("LLM ERROR DESC", "LLM ERROR CAT")])
    return parsed_result.output

async def llm_tx_categorization(tx_list: pd.DataFrame) -> pd.DataFrame:
    """Categorize a list of transactions using a language model.
    
    Args:
        tx_list (pd.DataFrame): The list of transactions to categorize.

    Returns:
        pd.DataFrame: The original dataframe with an additional column for the category.
    """
    
    # Create base llm model and validation parser
    llm = ChatOpenAI(temperature=0, client=Any)
    fixer_parser = OutputFixingParser.from_llm(parser=PydanticOutputParser(pydantic_object=Desc_Categ_Pair), llm=llm)

    # Create categorization prompt and chain
    prompt = PromptTemplate.from_template(template=templates.EXPENSE_CAT_TEMPLATE)    
    chain = LLMChain(llm=llm, prompt=prompt)

    # Iterate over the DataFrame in batches of 10 rows
    chunksize = 10
    tasks = [categorize_tx_batch(chain=chain, tx_descriptions="\n".join(chunk["Description"]), parser=fixer_parser, prompt=prompt) 
        for chunk in np.array_split(tx_list, tx_list.shape[0]//chunksize + 1)]

    results_list = await asyncio.gather(*tasks)

    # unpack the list of results; each result being a list of tuples (description-category pairs)
    categorized_descriptions = pd.DataFrame(
        [desc_cat_pair for result in results_list for desc_cat_pair in result],
        columns=["Description", "Category"],
    )

    return categorized_descriptions
