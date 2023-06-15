"""
This module defines Pydantic models that are used for validating the structure and content
of certain data structures in the application.
"""

# pylint: disable=no-name-in-module
from typing import List

from pydantic import BaseModel, Field, validator


class ShortList(BaseModel):
    """
    A Pydantic model that represents a list of strings with a maximum length of 4.
    """

    MAX_LENGTH: int = 4

    output: List[str] = Field(description="List of strings")

    @validator("output")
    def check_length(cls, v):  # pylint: disable=no-self-argument
        """
        Checks that the 'output' field does not exceed the maximum length.
        """
        if len(v) > cls.MAX_LENGTH:
            raise ValueError(
                f"Expected no more than {cls.MAX_LENGTH} elements, got {len(v)}"
            )
        return v


class CatDesc(BaseModel):
    """
    A Pydantic model that represents a list of description-category pairs (2-tuple of strings).
    """

    LEN_TUPLE: int = 2

    output: List[List[str]] = Field(description="Description-Category pairs")

    @validator("output")
    def check_length(cls, v):  # pylint: disable=no-self-argument
        """
        Checks that every tuple in 'output' has exactly two elements.
        """
        for item in v:
            if len(item) != cls.LEN_TUPLE:
                raise ValueError(
                    f"Every tuple in output should have length {cls.LEN_TUPLE}, "
                    f"got {item} with length {len(item)}"
                )
        return v