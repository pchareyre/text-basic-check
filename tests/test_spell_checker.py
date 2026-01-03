"""Tests for the spell checker module."""

import unittest
from text_basic_check import SpellChecker


class TestSpellChecker(unittest.TestCase):
    """Test cases for the SpellChecker class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.checker = SpellChecker(language='en')
    
    def test_check_word_correct(self):
        """Test checking a correctly spelled word."""
        self.assertTrue(self.checker.check_word('hello'))
        self.assertTrue(self.checker.check_word('world'))
    
    def test_check_word_incorrect(self):
        """Test checking an incorrectly spelled word."""
        self.assertFalse(self.checker.check_word('helo'))
        self.assertFalse(self.checker.check_word('wrld'))
    
    def test_find_errors(self):
        """Test finding errors in text."""
        text = "This is a smple text with erors"
        errors = self.checker.find_errors(text)
        self.assertIn('smple', errors)
        self.assertIn('erors', errors)
        self.assertNotIn('This', errors)
        self.assertNotIn('text', errors)
    
    def test_get_suggestions(self):
        """Test getting suggestions for misspelled words."""
        suggestions = self.checker.get_suggestions('helo')
        self.assertIsInstance(suggestions, list)
        # Check that we get some reasonable suggestions
        self.assertGreater(len(suggestions), 0)
        # Any of these are valid corrections for 'helo'
        self.assertTrue(any(word in suggestions for word in ['hello', 'help', 'hero', 'held']))
    
    def test_correct_word(self):
        """Test correcting a single word."""
        corrected = self.checker.correct_word('helo')
        # The correction could be 'hello' or 'help' - both are valid
        self.assertIn(corrected, ['hello', 'help'])
        
        # Test that correct words remain unchanged
        corrected = self.checker.correct_word('hello')
        self.assertEqual(corrected, 'hello')
    
    def test_correct_text(self):
        """Test correcting text with multiple words."""
        text = "This is a smple text"
        corrected = self.checker.correct_text(text)
        self.assertIn('simple', corrected)
        self.assertNotIn('smple', corrected)
    
    def test_analyze(self):
        """Test analyzing text."""
        text = "This is a smple text with erors"
        result = self.checker.analyze(text)
        
        self.assertIn('errors', result)
        self.assertIn('corrections', result)
        self.assertIn('error_count', result)
        
        self.assertGreater(result['error_count'], 0)
        self.assertIsInstance(result['errors'], list)
        self.assertIsInstance(result['corrections'], dict)
    
    def test_empty_text(self):
        """Test handling empty text."""
        errors = self.checker.find_errors('')
        self.assertEqual(errors, [])
        
        result = self.checker.analyze('')
        self.assertEqual(result['error_count'], 0)
    
    def test_punctuation_handling(self):
        """Test that punctuation is handled correctly."""
        text = "Hello, world! How are you?"
        errors = self.checker.find_errors(text)
        # Should not flag correct words with punctuation as errors
        self.assertNotIn('Hello,', errors)
        self.assertNotIn('world!', errors)
        self.assertNotIn('you?', errors)
        
        # Test correction preserves punctuation
        text_with_error = "Helo, wrld!"
        corrected = self.checker.correct_text(text_with_error)
        # Should have punctuation preserved
        self.assertIn(',', corrected)
        self.assertIn('!', corrected)


if __name__ == '__main__':
    unittest.main()
