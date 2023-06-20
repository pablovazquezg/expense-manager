# Standard library imports
import re
import ast
import json
import logging
from typing import Any, List, Tuple, Optional, Dict, Union

# Third-party library imports
import asyncio
import numpy as np
import pandas as pd
from pydantic import ValidationError
from rapidfuzz import process
from tenacity import retry, wait_random_exponential, stop_after_attempt
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
from langchain.prompts import PromptTemplate

# Local application/library specific imports
import src.templates as templates
from src.config import REF_OUTPUT_FILE, REF_STAGE_FOLDER, TX_PER_LLM_RUN


def fuzzy_match_list_categorizer(
    description: str,
    descriptions: np.ndarray,
    description_category_pairs: pd.DataFrame,
    threshold: int = 75,
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
        return description_category_pairs.at[match_results[2], 'category']
    
    return None


async def llm_list_categorizer(tx_list: pd.DataFrame) -> pd.DataFrame:
    """Categorize a list of transactions using a language model.
    
    Args:
        tx_list (pd.DataFrame): The list of transactions to categorize.

    Returns:
        pd.DataFrame: The original dataframe with an additional column for the category.
    """
    
    # Create LLM Chain to be used for categorization
    llm = ChatOpenAI(temperature=0, client=Any)
    prompt = PromptTemplate.from_template(template=templates.EXPENSE_CAT_TEMPLATE)    
    chain = LLMChain(llm=llm, prompt=prompt)

    # Iterate over the DataFrame in batches
    tasks = []
    for chunk in np.array_split(tx_list, tx_list.shape[0] // TX_PER_LLM_RUN + 1):
        tasks.append(llm_sublist_categorizer(chain=chain, tx_descriptions="\n".join(chunk['description']).strip()))

    # Gather results and extract (valid) outputs
    results = await asyncio.gather(*tasks)

    valid_outputs = [result['output'] for result in results if result['valid']]
    categorized_descriptions = pd.DataFrame(valid_outputs, columns=['description', 'category'])

    return categorized_descriptions


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
async def llm_sublist_categorizer(
    chain: LLMChain,
    tx_descriptions: str,
) -> Dict[str, Union[bool, List[Tuple[str, str]]]]:
    """Categorize a batch of transactions using a LLM
    
    Args:
        chain (LLMChain): The LLMChain object to use for running the chain.
        tx_descriptions (str): A string containing the transaction descriptions to categorize.
        parser (OutputFixingParser): The parser to use for parsing the LLM output.
        prompt (PromptTemplate): The prompt to use for running the LLM chain.

    Returns:
        List[Tuple]: A list of tuples containing the categorized transaction descriptions.
    """

    print(f'Running LLM chain with {len(tx_descriptions.splitlines())} transactions')
    raw_result = chain.run(input_data=tx_descriptions)

    logger = logging.getLogger(__name__)
    result = {'valid': True, 'output': []}
    try:
        # Create a pattern to match a list Description-Category pairs (List[Tuple[str, str]])
        pattern = r"\['([^']+)', '([^']+)'\]"
        
        # Use it to extract all the correctly formatted pairs from the raw result
        matches = re.findall(pattern, raw_result)
        
        # Loop over the matches, and try to parse them to ensure the content is valid
        valid_outputs = []
        for match in matches:
            try:
                parsed_pair = ast.literal_eval(str(list(match)))
                valid_outputs.append(parsed_pair)
            except Exception as e:
                logger.log(logging.ERROR, f"Parsing Error: {e}\nMatch: {match}\n")
                result['valid'] = False

        result['output'] = valid_outputs
        
    except Exception as e:
        logging.log(logging.ERROR, f"Unexpected Error: {e}\nRaw Result: {raw_result}\n")
        result['valid'] = False
    
    print(f'IN: {len(tx_descriptions.splitlines())} OUT: {len(result["output"])}')
    return result
