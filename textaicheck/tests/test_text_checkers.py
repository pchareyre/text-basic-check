from textaicheck.prompt_generator import _generate_system_prompt, generate_prompt
from textaicheck.text_checkers import BasicTextChecker, AdvancedTextChecker
from textaicheck.input_output_data_types import InputTextEntry, OutputChangedResult, InputTextEntryMinimal
from unittest.mock import MagicMock,  patch
import pytest
from langchain_core.messages import HumanMessage, SystemMessage

class TestBasicTextChecker:
    """Test suite for BasicTextChecker class"""

    def test_basic_text_checker_init(self):
        """Test BasicTextChecker initialization"""
        checker = BasicTextChecker()
        assert checker is not None

    @patch('textaicheck.text_checkers.spellcheck_entries')
    def test_correct_method(self, mock_spellcheck):
        """Test BasicTextChecker correct method"""
        # Setup mock
        mock_spellcheck.return_value = [
            OutputChangedResult(text_id="1", modified_text="test text")
        ]
        # Test data
        input_data = [
            {"text_id": "1", "text": "test texti", "correction_type": ["orthography"]}
        ]
        checker = BasicTextChecker()
        result = checker.correct(input_data, detect_language=True, language="English")
        # Expected result
        expected_result = [OutputChangedResult(text_id="1", modified_text="test text")]
        # Assertions
        assert result == expected_result
        mock_spellcheck.assert_called_once_with(input_data, True, "English")

    def test_invalid_input(self):
        """Test BasicTextChecker with invalid input"""
        checker = BasicTextChecker()
        with pytest.raises(TypeError):
            checker.correct("invalid_input")  # This should raise an error

    def test_empty_data(self):
        """Test BasicTextChecker with empty data"""
        checker = BasicTextChecker()
        result = checker.correct([])  # Should return an empty list
        assert result == []

class TestAdvancedTextChecker:
    """Test suite for AdvancedTextChecker class"""

    def test_advanced_text_checker_init(self):
        """Test AdvancedTextChecker initialization"""
        checker = AdvancedTextChecker(language="English")
        assert checker is not None

    def test_estimate_tokens(self):
        """Test token estimation"""
        checker = AdvancedTextChecker(language="English")
        data = [["1", "First text"], ["2", "Second text"]]
        task = "syntax"
        checker._estimate_tokens(data, task)
        assert checker.tokens is not None

    def test_generate_system_prompt(self):
        """Test system prompt generation"""
        checker = AdvancedTextChecker(language="English")
        data = [["1", "First text"], ["2", "Second text"]]
        result = generate_prompt(data, task="syntax", language="English", prompt_task_message="")
        assert len(result) == 2
        assert result[0].type == "system"
        assert result[1].type == "human"


