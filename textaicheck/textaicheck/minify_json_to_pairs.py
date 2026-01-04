from typing import List
from .input_output_data_types import InputTextEntryMinimal


def minify_json(input_list: List[InputTextEntryMinimal]) -> List[List]:
    """
    Transforms a list of dictionaries into a list of lists with the minimal information;
    containing text_id and the text itself

    Each output list contains:
    [text_id, text]
    """
    result = []
    for item in input_list:
        text_id = item.get("text_id")
        text = item.get("text")
        # If both entries are empty strings skip it
        if text_id!="" or text!="":
            result.append([text_id, text])

    return result
