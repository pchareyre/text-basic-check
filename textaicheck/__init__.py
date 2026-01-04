"""
Text AI Check Package
-----------------
This package corrects (checks spell, corrects syntax and reformulates) the text provided
through a json object.
"""
from .textaicheck import (
    text_checkers, spell_checker, json_text_splitter,
    minify_json_to_pairs, prompt_generator, LinguisticCheck, input_output_data_types,
    config_loader, apply_changes
)


__all__ = []
__version__ = "0.1.0"