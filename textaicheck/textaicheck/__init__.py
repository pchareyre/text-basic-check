"""
Text AI Check Library
--------------------------------
A python library to perform basic and advanced text correction.
"""

from .text_checkers import AdvancedTextChecker
from .input_output_data_types import (
    InputTextEntry,
    InputTextEntryMinimal,
    OutputChangedResult,
    OutputCompareResult
)

__all__ = [
    "AdvancedTextChecker",
    "InputTextEntry",
    "InputTextEntryMinimal",
    "OutputChangedResult",
    "OutputCompareResult"
]
__version__ = "0.1.0"
