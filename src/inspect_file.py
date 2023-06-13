import os
import ast
import json
import pandas as pd
from typing import Any, List
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
from src.custom_classes import ShortList


def inspect_data(data_sample: str, template: str) -> List[str]:
    prompt = PromptTemplate.from_template(template)
    llm = ChatOpenAI(temperature=0, client=Any)
    prompt = PromptTemplate.from_template(template)    
    chain = LLMChain(llm=llm, prompt=prompt)
    raw_result = chain.run(input_data=data_sample.strip())

    parser = OutputFixingParser.from_llm(llm=llm, parser=PydanticOutputParser(pydantic_object=ShortList))
    
    try:
        parsed_result = parser.parse(json.dumps({"output": raw_result}))
    except Exception as e:
        print(f"Parsing Error: {e}\n")
        print(f"Raw Result: {raw_result}")
        parsed_result = {"output": ['PARSING ERROR']}

    return parsed_result.output  # type: ignore
