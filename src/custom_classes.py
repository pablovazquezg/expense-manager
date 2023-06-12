# pylint: disable=no-name-in-module
from pydantic import BaseModel, Field, validator
from typing import List

LEN_TUPLE = 2
SHORT_LIST_MAX_LENGTH = 4


class ShortList(BaseModel):
    output: List[str] = Field(description="List of strings")
    max_length: int = 4

    @validator("output")
    def check_length(cls, v): # pylint: disable=no-self-argument
        if len(v) > SHORT_LIST_MAX_LENGTH:
            raise ValueError(f"Expected no more than {SHORT_LIST_MAX_LENGTH} elements, got {len(v)}")
        return v


class CatDesc(BaseModel):
    output: List[List[str]] = Field(description="Description-Category pairs")

    @validator("output")
    def check_length(cls, v): # pylint: disable=no-self-argument
        for item in v:
            if len(item) != LEN_TUPLE:
                raise ValueError(
                    f"Every tuple in output should have length 2, got {item} with length {len(item)}"
                )
        return v
