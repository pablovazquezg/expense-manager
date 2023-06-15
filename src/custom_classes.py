"""
This module defines Pydantic models that are used for validating the structure and content
of certain data structures in the application.
"""

# Standard library imports
from typing import List, Tuple

# Third-party library imports
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


class Desc_Categ_Pair(BaseModel):
    """
    A Pydantic model that represents a list of description-category pairs (2-tuple of strings).
    """

    output: List[Tuple[str, str]] = Field(description="Description-Category pairs")