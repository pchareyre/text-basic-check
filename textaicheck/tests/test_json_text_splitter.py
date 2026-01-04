import importlib
import sys
from textaicheck.json_text_splitter import (
    is_single_word,
    has_two_letters,
    process_json,
    clean_text
)


class TestIsSingleWord:
    """Test cases for is_single_word function."""
    @classmethod
    def setup_class(cls):
        """Force reload the module before running tests."""
        if 'textaicheck.json_text_splitter' in sys.modules:
            importlib.reload(sys.modules['textaicheck.json_text_splitter'])

    def test_single_word_basic(self):
        """Test basic single word detection."""
        assert is_single_word("hello") is True
        assert is_single_word("world") is True

    def test_single_word_with_punctuation(self):
        """Test basic single word detection."""
        assert is_single_word("hello!") is True
        assert is_single_word("world.") is True

    def test_single_word_with_whitespace(self):
        """Test single word with leading/trailing whitespace."""
        assert is_single_word("  hello  ") is True
        assert is_single_word("\thello\n") is True

    def test_multiple_words(self):
        """Test that multiple words return False."""
        assert is_single_word("hello world") is False
        assert is_single_word("two words") is False

    def test_empty_string(self):
        """Test empty string."""
        assert is_single_word("") is False
        assert is_single_word("   ") is False

    def test_single_word_with_accents(self):
        """Test single word with accented characters."""
        assert is_single_word("café") is True
        assert is_single_word("naïve") is True
        assert is_single_word("résumé") is True


class TestHasTwoLetters:
    """Test cases for has_two_letters function."""

    def test_two_letters_basic(self):
        """Test basic two letter detection."""
        assert has_two_letters("ab") is True
        assert has_two_letters("hello") is True

    def test_one_letter(self):
        """Test single letter returns False."""
        assert has_two_letters("a") is False
        assert has_two_letters("x") is False

    def test_no_letters(self):
        """Test no letters returns False."""
        assert has_two_letters("123") is False
        assert has_two_letters("!!!") is False
        assert has_two_letters("") is False

    def test_letters_with_numbers(self):
        """Test letters mixed with numbers."""
        assert has_two_letters("a1b2") is False
        assert has_two_letters("123ab") is True

    def test_letters_with_special_chars(self):
        """Test letters mixed with special characters."""
        assert has_two_letters("a!b@") is False
        assert has_two_letters("!@#ab") is True

    def test_accented_letters(self):
        """Test accented characters count as letters."""
        assert has_two_letters("àé") is True
        assert has_two_letters("café") is True
        assert has_two_letters("ñ") is False


class TestCleanText:
    """Test cases for clean_text function."""

    def test_curly_quotes_replacement(self):
        """Test curly quotes are replaced with straight quotes."""
        assert clean_text("'hello'") == "'hello'"

    def test_non_breaking_space_removal(self):
        """Test non-breaking spaces are replaced with regular spaces."""
        assert clean_text("hello\xa0world") == "hello world"

    def test_newline_replacement(self):
        """Test newlines are replaced with spaces."""
        assert clean_text("hello\nworld") == "hello world"
        assert clean_text("line1\nline2\nline3") == "line1 line2 line3"

    def test_tab_replacement(self):
        """Test tabs are replaced with spaces."""
        assert clean_text("hello\tworld") == "hello world"

    def test_multiple_spaces_collapsed(self):
        """Test multiple spaces are collapsed to single space."""
        assert clean_text("hello    world") == "hello world"
        assert clean_text("a  b   c    d") == "a b c d"

    def test_leading_trailing_whitespace_removed(self):
        """Test leading and trailing whitespace is removed."""
        assert clean_text("  hello  ") == "hello"
        assert clean_text("\n\thello\t\n") == "hello"

    def test_unicode_normalization(self):
        """Test Unicode normalization."""
        # NFKC normalization example
        text = "ﬁ"  # ligature fi
        result = clean_text(text)
        assert result == "fi"

    def test_invisible_characters_removed(self):
        """Test invisible control characters are removed."""
        text = "hello\u200b world"  # zero-width space
        assert clean_text(text) == "hello world"

    def test_combined_cleaning(self):
        """Test multiple cleaning operations together."""
        text = "  'hello'\xa0\nworld\t\t  "
        assert clean_text(text) == "'hello' world"

    def test_non_string_input(self):
        """Test non-string input is returned as-is."""
        assert clean_text(123) == 123
        assert clean_text(None) is None
        assert clean_text([]) == []

    def test_empty_string(self):
        """Test empty string."""
        assert clean_text("") == ""
        assert clean_text("   ") == ""


class TestProcessJson:
    """Test cases for process_json function."""

    def test_filter_by_two_letters(self):
        """Test filtering items without at least two letters."""
        data = [
            {"text": "ab", "text_id": 1, "correction_type": ["orthography"]},
            {"text": "a", "text_id": 2, "correction_type": ["orthography"]},
            {"text": "123", "text_id": 3, "correction_type": ["orthography"]},
        ]
        ortho, syntax, reform = process_json(data, clean=False)

        # Only first item should remain
        assert len(ortho) == 1
        assert ortho[0]["text_id"] == 1

    def test_single_word_becomes_orthography(self):
        """Test single words are classified as orthography."""
        data = [
            {"text": "hello", "text_id": 1, "correction_type": ["syntax"]},
        ]
        ortho, syntax, reform = process_json(data, clean=False)

        assert len(ortho) == 1
        assert ortho[0]["correction_type"] == ["orthography"]
        assert len(syntax) == 0

    def test_orthography_classification(self):
        """Test items with orthography correction type."""
        data = [
            {"text": "hello world", "text_id": 1, "correction_type": ["orthography"]},
        ]
        ortho, syntax, reform = process_json(data, clean=False)

        assert len(ortho) == 1
        assert len(syntax) == 0
        assert len(reform) == 0

    def test_syntax_classification(self):
        """Test items with syntax correction type."""
        data = [
            {"text": "hello world", "text_id": 1, "correction_type": ["syntax"]},
        ]
        ortho, syntax, reform = process_json(data, clean=False)

        assert len(ortho) == 0
        assert len(syntax) == 1
        assert len(reform) == 0

    def test_reformulation_classification(self):
        """Test items with reformulation correction type."""
        data = [
            {"text": "hello world", "text_id": 1, "correction_type": ["reformulation"]},
            {"text": "test phrase", "text_id": 2, "correction_type": ["syntax", "reformulation"]},
        ]
        ortho, syntax, reform = process_json(data, clean=False)

        assert len(ortho) == 0
        assert len(syntax) == 0
        assert len(reform) == 2

    def test_mixed_data(self):
        """Test processing mixed data types."""
        data = [
            {"text": "hello", "text_id": 1, "correction_type": ["syntax"]},  # Single word -> ortho
            {"text": "world test", "text_id": 2, "correction_type": ["orthography"]},  # Ortho
            {"text": "syntax error", "text_id": 3, "correction_type": ["syntax"]},  # Syntax
            {"text": "reform this", "text_id": 4, "correction_type": ["reformulation"]},  # Reform
            {"text": "a", "text_id": 5, "correction_type": ["orthography"]},  # Filtered out
        ]
        ortho, syntax, reform = process_json(data, clean=False)

        assert len(ortho) == 2  # Single word + orthography
        assert len(syntax) == 1
        assert len(reform) == 1

    def test_clean_text_enabled(self):
        """Test that clean parameter works."""
        data = [
            {"text": "hello\xa0world", "text_id": 1, "correction_type": ["syntax"]},
        ]
        ortho, syntax, reform = process_json(data, clean=True)

        # Should be classified as syntax (two words after cleaning)
        assert len(syntax) == 1

    def test_clean_text_disabled(self):
        """Test processing without text cleaning."""
        data = [
            {"text": "  hello  ", "text_id": 1, "correction_type": ["syntax"]},
        ]
        ortho, syntax, reform = process_json(data, clean=False)

        # With whitespace, might be treated differently
        assert len(ortho) + len(syntax) + len(reform) == 1

    def test_empty_data(self):
        """Test processing empty data list."""
        data = []
        ortho, syntax, reform = process_json(data, clean=False)

        assert len(ortho) == 0
        assert len(syntax) == 0
        assert len(reform) == 0

    def test_missing_text_field(self):
        """Test handling items with missing text field."""
        data = [
            {"text_id": 1, "correction_type": ["orthography"]},
        ]
        ortho, syntax, reform = process_json(data, clean=False)

        # Should be filtered out (no text = no letters)
        assert len(ortho) == 0

    def test_return_types(self):
        """Test that function returns three lists."""
        data = [
            {"text": "hello", "text_id": 1, "correction_type": ["orthography"]},
        ]
        result = process_json(data, clean=False)

        assert isinstance(result, tuple)
        assert len(result) == 3
        assert all(isinstance(lst, list) for lst in result)


class TestProcessJsonEdgeCases:
    """Edge case tests for process_json function."""

    def test_special_characters_in_text(self):
        """Test handling special characters."""
        data = [
            {"text": "café", "text_id": 1, "correction_type": ["orthography"]},
            {"text": "naïve", "text_id": 2, "correction_type": ["syntax"]},
        ]
        ortho, syntax, reform = process_json(data, clean=False)

        assert len(ortho) == 2  # Both single words

    def test_multiple_correction_types(self):
        """Test items with multiple correction types."""
        data = [
            {"text": "hello world", "text_id": 1, "correction_type": ["orthography", "syntax"]},
        ]
        ortho, syntax, reform = process_json(data, clean=False)

        # Should go to syntax (not single orthography)
        assert len(syntax) == 1

    def test_punctuation_only(self):
        """Test text with only punctuation."""
        data = [
            {"text": "!!!", "text_id": 1, "correction_type": ["orthography"]},
        ]
        ortho, syntax, reform = process_json(data, clean=False)

        # Should be filtered out (no letters)
        assert len(ortho) == 0
