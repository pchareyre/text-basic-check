"""
Simple spell checker module using PySpellChecker.

This module provides basic spell-checking functionality including:
- Finding misspelled words
- Suggesting corrections
- Correcting text
"""

import re
from typing import List, Dict, Optional, Any
from spellchecker import SpellChecker as PySpellChecker


class SpellChecker:
    """
    A simple spell checker that wraps PySpellChecker.
    
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
        self._spell = PySpellChecker(language=language)
    
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
        return word in self._spell
    
    def find_errors(self, text: str) -> List[str]:
        """
        Find all misspelled words in the text.
        
        Args:
            text: The text to check
            
        Returns:
            A list of misspelled words
        """
        words = self._tokenize(text)
        misspelled = self._spell.unknown(words)
        return list(misspelled)
    
    def get_suggestions(self, word: str, max_suggestions: int = 5) -> List[str]:
        """
        Get spelling suggestions for a word.
        
        Args:
            word: The word to get suggestions for
            max_suggestions: Maximum number of suggestions to return
            
        Returns:
            A list of suggested corrections
        """
        candidates = self._spell.candidates(word)
        if candidates is None:
            return []
        return list(candidates)[:max_suggestions]
    
    def correct_word(self, word: str) -> str:
        """
        Get the most likely correction for a word.
        
        Args:
            word: The word to correct
            
        Returns:
            The corrected word, or the original if no correction is found
        """
        correction = self._spell.correction(word)
        return correction if correction else word
    
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
