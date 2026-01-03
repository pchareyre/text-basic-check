"""
text-basic-check: A basic spell-checking and syntax correction library.

This library provides simple spell-checking functionality without using generative AI.
It uses PySpellChecker as the core spell-checking engine.
"""

__version__ = "0.1.0"

from .spell_checker import SpellChecker

__all__ = ["SpellChecker"]
