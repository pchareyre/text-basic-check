"""
Simple spell checker module using SymSpell.

This module provides basic spell-checking functionality including:
- Finding misspelled words
- Suggesting corrections
- Correcting text
"""

import re
from typing import List, Dict, Optional, Any
from symspellpy import SymSpell, Verbosity
import pkg_resources


class SpellChecker:
    """
    A simple spell checker that wraps SymSpell.
    
    Attributes:
        language: The language to use for spell checking (default: 'en')
    """
    
    def __init__(self, language: str = 'en'):
        """
        Initialize the spell checker.
        
        Args:
            language: The language code (e.g., 'en', 'fr', 'es')
        """
        self.language = language
        self._spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
        
        # Load dictionary based on language
        if language == 'en':
            dictionary_path = pkg_resources.resource_filename(
                "symspellpy", "frequency_dictionary_en_82_765.txt"
            )
            self._spell.load_dictionary(dictionary_path, term_index=0, count_index=1)
        else:
            # For now, only English is supported - could be extended
            raise ValueError(f"Language '{language}' is not supported yet. Only 'en' is available.")
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words, removing punctuation.
        
        Args:
            text: The text to tokenize
            
        Returns:
            A list of words without punctuation
        """
        # Split on whitespace and remove punctuation from each word
        words = []
        for token in text.split():
            # Remove leading and trailing punctuation but keep apostrophes
            word = re.sub(r'^[^\w\']+|[^\w\']+$', '', token)
            if word:  # Only add non-empty words
                words.append(word)
        return words
    
    def check_word(self, word: str) -> bool:
        """
        Check if a single word is spelled correctly.
        
        Args:
            word: The word to check
            
        Returns:
            True if the word is spelled correctly, False otherwise
        """
        # SymSpell lookup returns empty list if word is correct
        # Normalize to lowercase since dictionary is lowercase
        suggestions = self._spell.lookup(word.lower(), Verbosity.TOP, max_edit_distance=2)
        # If the top suggestion is the same word with distance 0, it's correct
        return len(suggestions) > 0 and suggestions[0].term.lower() == word.lower() and suggestions[0].distance == 0
    
    def find_errors(self, text: str) -> List[str]:
        """
        Find all misspelled words in the text.
        
        Args:
            text: The text to check
            
        Returns:
            A list of misspelled words
        """
        words = self._tokenize(text)
        misspelled = []
        for word in words:
            if not self.check_word(word):
                misspelled.append(word)
        return misspelled
    
    def get_suggestions(self, word: str, max_suggestions: int = 5) -> List[str]:
        """
        Get spelling suggestions for a word.
        
        Args:
            word: The word to get suggestions for
            max_suggestions: Maximum number of suggestions to return
            
        Returns:
            A list of suggested corrections
        """
        suggestions = self._spell.lookup(word.lower(), Verbosity.ALL, max_edit_distance=2)
        return [s.term for s in suggestions[:max_suggestions]]
    
    def correct_word(self, word: str) -> str:
        """
        Get the most likely correction for a word.
        
        Args:
            word: The word to correct
            
        Returns:
            The corrected word, or the original if no correction is found
        """
        # Preserve original case if word starts with capital
        is_capitalized = word and word[0].isupper()
        suggestions = self._spell.lookup(word.lower(), Verbosity.TOP, max_edit_distance=2)
        if suggestions and len(suggestions) > 0:
            corrected = suggestions[0].term
            # Preserve capitalization
            if is_capitalized:
                corrected = corrected.capitalize()
            return corrected
        return word
    
    def correct_text(self, text: str) -> str:
        """
        Correct all misspelled words in the text.
        
        Args:
            text: The text to correct
            
        Returns:
            The corrected text
        """
        # Tokenize preserving spaces and punctuation structure
        result = []
        for token in text.split():
            # Extract punctuation
            match = re.match(r'^([^\w\']*)(.+?)([^\w\']*)$', token)
            if match and match.group(2):  # Ensure there's a word part
                prefix, word, suffix = match.groups()
                corrected_word = self.correct_word(word)
                result.append(f"{prefix}{corrected_word}{suffix}")
            else:
                # Keep tokens that are only punctuation or whitespace as-is
                result.append(token)
        return ' '.join(result)
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze text and return detailed information about errors.
        
        Args:
            text: The text to analyze
            
        Returns:
            A dictionary containing:
                - errors: list of misspelled words
                - corrections: dict mapping errors to suggested corrections
                - error_count: number of errors found
        """
        errors = self.find_errors(text)
        corrections = {error: self.get_suggestions(error) for error in errors}
        
        return {
            'errors': errors,
            'corrections': corrections,
            'error_count': len(errors)
        }
