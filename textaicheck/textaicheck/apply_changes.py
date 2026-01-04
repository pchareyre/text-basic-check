from typing import List
from .input_output_data_types import InputTextEntryMinimal, OutputChangedResult


def apply_changes(
        data: List[InputTextEntryMinimal],
        modified_list: List[List[str]], id_index=0, value_index=1) -> List[OutputChangedResult]:
    """
    The function updates data (a list of dictionaries) by replacing the text value in each dictionary with a modified
    version from a corresponding sublist (in modified_list), matching entries by text_id.

    Args:
        data (List[InputTextEntryMinimal]): A dictionary with at least the keys:
            'text_id', 'text'.
        modified_list (List[List[str,str]]): Each sublist has at least two elements:
            [text_id, value_to_replace]
        id_index (int): Index of the text_id in each sublist (default: 0).
        value_index (int): Index to modified dict['text'] (default: 1).

    Returns:
        data_modified (List[OutputChangedResult]) : list containing dictionaries with the
        original text modified by the second entry in sublist
    """
    # Basic validations
    if not isinstance(data, list):
        raise TypeError("data must be a list of dict.")
    if not isinstance(modified_list, list):
        raise TypeError("modified_list must be a list.")

    # Build a lookup from text_id -> new_text_value for quick access
    lookup = {sublist[id_index]: sublist[value_index]
              for sublist in modified_list
              if isinstance(sublist, list) and len(sublist) > max(id_index, value_index)}

    # Update each record if its text_id is in lookup
    data_modified = []
    for entry in data:
        if not isinstance(entry, dict):
            continue
        text_id = entry.get("text_id")
        if text_id in lookup:
            if isinstance(lookup[text_id], str):
                modified_entry = OutputChangedResult(
                    text_id=text_id,
                    modified_text=lookup[text_id]
                )
                data_modified.append(modified_entry)

    return data_modified
