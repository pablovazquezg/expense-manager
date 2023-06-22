# Standard library imports
import re
import ast
import json
import logging
from typing import Any, List, Tuple, Optional, Dict, Union

# Third-party library imports
import numpy as np
import pandas as pd
import asyncio
from rapidfuzz import process
from tenacity import retry, wait_random_exponential, stop_after_attempt
from pydantic import ValidationError

# Local application/library specific imports
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
from langchain.prompts import PromptTemplate
import src.templates as templates
from src.config import REF_OUTPUT_FILE, TX_PER_LLM_RUN


def fuzzy_match_list_categorizer(
    description: str,
    descriptions: np.ndarray,
    description_category_pairs: pd.DataFrame,
    threshold: int = 75,
) -> Optional[str]:
    """Find the most similar transaction description and return its category.

    This function uses fuzzy string matching to compare the input description
    against a list of known descriptions. If a sufficient match is found,
    the function returns the category associated with the matched description.

    Args:
        description (str): The transaction description to categorize.
        descriptions (np.ndarray): Known descriptions to compare against.
        description_category_pairs (pd.DataFrame): DataFrame mapping descriptions to categories.
        threshold (int): Minimum similarity score to consider a match.

    Returns:
        str or None: Category of the matched description, or None if no match found.
    """

    # Fuzzy-match this description against the reference descriptions
    match_results = process.extractOne(description, descriptions, score_cutoff=threshold)

    # If a match is found, return the category of the matched description
    if match_results:
        return description_category_pairs.at[match_results[2], 'category']
    
    return None


async def llm_list_categorizer(tx_list: pd.DataFrame) -> pd.DataFrame:
    """Categorize a list of transactions using a language model.

    This function uses a Language Model (LLM) to categorize a list of transaction descriptions.
    It splits the input DataFrame into chunks and processes each chunk asynchronously to improve performance.

    Args:
        tx_list (pd.DataFrame): DataFrame containing the transaction descriptions to categorize.

    Returns:
        pd.DataFrame: DataFrame mapping transaction descriptions to their inferred categories.
    """

    # Initialize language model and prompt
    llm = ChatOpenAI(temperature=0, client=Any)
    prompt = PromptTemplate.from_template(template=templates.EXPENSE_CAT_TEMPLATE)    
    chain = LLMChain(llm=llm, prompt=prompt)

    # Iterate over the DataFrame in batches of TX_PER_LLM_RUN transactions
    tasks = [llm_sublist_categorizer(tx_list.attrs['file_name'], chain=chain, tx_descriptions="\n".join(chunk['description']).strip())
             for chunk in np.array_split(tx_list, tx_list.shape[0] // TX_PER_LLM_RUN + 1)]

    # Gather results and extract (valid) outputs
    # The results variable is a list of 'results', each 'result' being the output of a single LLM run
    results = await asyncio.gather(*tasks)

    # Extract valid results (each valid result is a list of description-category pairs)
    valid_results = [result['output'] for result in results if result['valid']]

    # Flatten the list of valid results to obtain a single list of description-category pairs
    valid_outputs = [output for valid_result in valid_results for output in valid_result]

    # Return a DataFrame with the valid outputs
    return pd.DataFrame(valid_outputs, columns=['description', 'category'])


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
async def llm_sublist_categorizer(
    file_name: str,
    chain: LLMChain,
    tx_descriptions: str,
) -> Dict[str, Union[bool, List[Tuple[str, str]]]]:
    """Categorize a batch of transactions using a language model.

    This function takes a batch of transaction descriptions and passes them to a language model
    for categorization. The function retries on failure, with an exponential backoff.

    Args:
        file_name (str): Name of the file the transaction descriptions were extracted from.
        chain (LLMChain): Language model chain to use for categorization.
        tx_descriptions (str): Concatenated transaction descriptions to categorize.

    Returns:
        dict: Dictionary containing a 'valid' flag and a list of categorized descriptions.
    """

    raw_result = await chain.arun(input_data=tx_descriptions)

    logger = logging.getLogger(__name__)
    result = {'valid': True, 'output': []}
    try:
        # Create a pattern to match a list Description-Category pairs (List[Tuple[str, str]])
        pattern = r"\['([^']+)', '([^']+)'\]"
        
        # Use it to extract all the correctly formatted pairs from the raw result
        matches = re.findall(pattern, raw_result.replace("\\'", "'"))

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
        logging.log(logging.ERROR, f"| File: {file_name} | Unexpected Error: {e}\nRaw Result: {raw_result}")
        result['valid'] = False
    
    return result
