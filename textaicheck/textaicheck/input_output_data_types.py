from typing import TypedDict, List
from pydantic import BaseModel


class InputTextEntry(TypedDict):
    """All your text entries should have these attributes and conform to this schema."""
    text: str
    text_id: str
    correction_type: List[str]  # Will become ["orthography"] for some entries

class InputTextEntryMinimal(TypedDict):
    """All your text entries with a predefined task should have these attributes and conform to this schema."""
    text: str
    text_id: str

class OutputChangedResult(BaseModel):
    """Your output should have these attributes and conform to this schema."""
    text_id: str
    modified_text: str

class OutputCompareResult(BaseModel):
    """In the case of correct_and_compare the output should have these attributes and conform to this schema."""
    text_id: str
    modified_text: str
    original_text: str
