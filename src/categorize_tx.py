# Standard library imports
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

# Local application/library specific imports
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
from langchain.prompts import PromptTemplate
import src.templates as templates
from src.custom_classes import Desc_Categ_Pair
from src.config import REF_OUTPUT_FILE, REF_STAGE_FOLDER, TX_PER_LLM_RUN


def fuzzy_match_list_categorizer(
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
        return description_category_pairs.at[match_results[2], 'category']
    
    return None


async def llm_list_categorizer(tx_list: pd.DataFrame) -> pd.DataFrame:
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

    # Iterate over the DataFrame in batches
    tasks = []
    for chunk in np.array_split(tx_list, tx_list.shape[0] // TX_PER_LLM_RUN + 1):
        tasks.append(llm_sublist_categorizer(chain=chain, tx_descriptions="\n".join(chunk['description']).strip(), parser=fixer_parser, prompt=prompt))

    # Gather results and extract description-category pairs 
    results = await asyncio.gather(*tasks)

    successful_results = []
    for result in results:
        if result['success']:
            successful_results.extend(result['output'])
        else:
            # If not successful, log the error
            logging.error(result['output'])

    # Convert the list of successful description-category pairs into a DataFrame
    categorized_descriptions = pd.DataFrame(successful_results, columns=['description', 'category'])

    return categorized_descriptions


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
async def llm_sublist_categorizer(
    chain: LLMChain,
    tx_descriptions: str,
    parser: OutputFixingParser,
    prompt: PromptTemplate,
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

    raw_result = chain.run(input_data=tx_descriptions)
    #TODO: Manage all exceptions
    #TODO: Convert from strings; do I even need to do this?
    #TODO: Reduce number of tx; struggling past 50

    logger = logging.getLogger(__name__)
    call = {'success': True, 'output': []}
    try:
        # Create JSON string and parse it to ensure output is valid
        json_result = json.dumps({"output": ast.literal_eval(raw_result)})
        parsed_result = parser.parse(json_result)
        call['output'] = parsed_result.output
    except (SyntaxError, ValueError, TypeError) as e:
        logging.log(logging.ERROR, f"Parsing Error: {e}\nRaw Result: {raw_result}\n")
        call['success'] = False
    except Exception as e:
        logging.log(logging.ERROR, f"Unexpected Error: {e}\nRaw Result: {raw_result}\n")
        call['success'] = False
    return call