import os
import ast
import json
import pandas as pd
from typing import Any, List
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser, RetryWithErrorOutputParser
from src.custom_classes import ShortList


def inspect_file(file_sample: str, question: str) -> List[str]:
    # Create LLM chain and parser to be used (RetryWithErrorOutputParser)
    parser = PydanticOutputParser(pydantic_object=ShortList)
    prompt = PromptTemplate.from_template(template=question)
    llm = ChatOpenAI(temperature=1, client=Any, model="gpt-3.5-turbo")
    chain = LLMChain(llm=llm, prompt=prompt)

    fixing_parser = RetryWithErrorOutputParser.from_llm(
        llm=llm, parser=parser, prompt=prompt
    )

    input = prompt.format_prompt(tx_list=file_sample)

    raw_result = chain.run(input.to_string())
    result = json.dumps({"output": ast.literal_eval(raw_result)})

    # leverage ShortList pydantic model to validate output
    try:
        result = parser.parse(result)
    except Exception as e:
        print(
            f"Error inspecting file\nError: {e}\nQuestion: {question}\nFailed with Output: {result}"
        )
        raise (e)

    return result.output  # type: ignore
