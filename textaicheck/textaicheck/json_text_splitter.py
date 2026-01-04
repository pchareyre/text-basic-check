import re
from typing import List, Tuple
import unicodedata
from .input_output_data_types import InputTextEntry


def is_single_word(text: str) -> bool:
    """Check if text contains exactly one word, ignoring all non-alphabetic characters."""
    # Extract only alphabetic characters
    letters_only = re.sub(r'[^A-Za-zÀ-ÖØ-öø-ÿ]', ' ', text)

    # Split by whitespace and filter empty strings
    words = [word for word in letters_only.split() if word]

    # Check if exactly one word
    return len(words) == 1


def has_two_letters(text: str) -> bool:
    """Check if text contains at least two consecutive alphabetic letters."""
    return bool(re.search(r'[A-Za-zÀ-ÖØ-öø-ÿ]{2,}', text))



def process_json(data: List[InputTextEntry], clean: bool=True) \
        -> Tuple[List[InputTextEntry], List[InputTextEntry], List[InputTextEntry]]:
    """
    Process a JSON object containing a list of dictionaries with (at least) the attributes:
    text, text_id, correction_type.

    Steps performed:
    1. Remove all dictionaries where the 'text' attribute does NOT contain at least two alphabetic letters.
    2. Identify dictionaries where 'text' contains exactly one word (using regex).
    3. For those single-word dictionaries, replace 'correction_type' with ["orthography"].
    4. Split the remaining dictionaries into three lists:
        - One containing all dictionaries with correction_type = ["orthography"].
        - Another containing all dictionaries containing "reformulation"
        - Another containing all other dictionaries for syntax correction (excluding removed ones).

    Args:
    data (InputTextEntry): list of dictionaries containing the data to correct/reformulate.
    clean_text: True by default. It cleans \xa0 like codes.

    Returns:
    Tuple[List[InputTextEntry], List[InputTextEntry]]:
        - A list of dictionaries containing single-word elements or phrases that only
            require orthographic correction
        - A list of dictionaries containing phrases that require orthography and syntax
            corrections
        - A list of dictionaries containing phrases that require orthography and syntax
            corrections as well as reformulation
    """

    # Step 1: Remove dictionaries whose text does not contain at least two letters
    filtered_data = [item for item in data if has_two_letters(item.get("text", ""))]

    orthography_list = []
    syntax_list = []
    reformulation_list = []
    # Steps 2-3 and 4
    for item in filtered_data:
        text = item.get("text", "")
        # clean text
        if clean:
            text = clean_text(text)
        if is_single_word(text):
            # Step 3: Replace correction_type with ["orthography"]
            item["correction_type"] = ["orthography"]
            orthography_list.append(item)
        elif len(item["correction_type"]) == 1 and item["correction_type"][0] == "orthography":
            orthography_list.append(item)
        elif "reformulation" in item['correction_type']:
            reformulation_list.append(item)
        else:
            syntax_list.append(item)

    return orthography_list, syntax_list, reformulation_list


def clean_text(text: str) -> str:
    """
    Cleans text by:
    - Replacing curly quotes/apostrophes with straight ones
    - Removing non-breaking spaces (\xa0)
    - Replacing new line \n with a space
    - Replacing new table \t with space
    - Normalizing Unicode characters
    - Collapsing multiple spaces
    - Removing invisible control characters
    """
    if not isinstance(text, str):
        return text

    # Replace curly quotes and apostrophes
    replacements = {
        '‘': "'",  # left single quote
        '’': "'",  # right single quote
        '“': '"',  # left double quote
        '”': '"',  # right double quote
        '\xa0': ' ',  # non-breaking space
        '\n': ' ',  # non-breaking space
        '\t': ' ',  # non-breaking space
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)

    # Normalize Unicode (NFKC handles compatibility characters)
    text = unicodedata.normalize("NFKC", text)

    # Remove invisible control characters (except newline)
    text = re.sub(r'[\u200b-\u200f\u202a-\u202e\u2060-\u206f]', '', text)

    # Collapse multiple spaces
    text = re.sub(r'\s+', ' ', text)

    # Strip leading/trailing whitespace
    return text.strip()
