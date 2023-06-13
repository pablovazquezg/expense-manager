import os
import ast
import json
import pandas as pd
from pandasai import PandasAI
from typing import Any, List
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
from src.custom_classes import ShortList


def inspect_data(tx_list: pd.DataFrame, prompt: str) -> List[str]:
    from pandasai.llm.openai import OpenAI
    pandas_ai = PandasAI(OpenAI())

    raw_result = pandas_ai(tx_list.head(), prompt=prompt)
    result = json.dumps({"output": raw_result})
    parser = PydanticOutputParser(pydantic_object=ShortList)
    fixing_parser = OutputFixingParser.from_llm(
        parser=parser, llm=ChatOpenAI()
    )
    # leverage ShortList pydantic model to validate output
    try:
        result = parser.parse(result)
    except Exception as e:
        print(
            f"Error inspecting file\nError: {e}\nQuestion: {prompt}\nFailed with Output: {result}"
        )
        raise (e)

    return result.output  # type: ignore
