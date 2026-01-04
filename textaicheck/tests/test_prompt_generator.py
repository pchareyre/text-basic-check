import pytest
from unittest.mock import patch
from textaicheck.prompt_generator import _generate_system_prompt, generate_prompt
from langchain_core.messages import HumanMessage, SystemMessage


class TestGenerateSystemPrompt:
    """Test suite for _generate_system_prompt function"""

    @patch("textaicheck.prompt_generator.load_config")
    def test_generate_system_prompt_syntax_english(self, mock_load_config):
        """Test system prompt generation for syntax task in English"""
        mock_config = {
            "INITIAL_SYSTEM_MESSAGE_EN": "You are a text correction assistant. ",
            "TASK_SYNTAX_EN": "Correct spelling and syntax. ",
            "OUTPUT_FORMAT_EN": "Return a list of lists. ",
        }
        mock_load_config.return_value = mock_config

        result = _generate_system_prompt(task="syntax", language="English", prompt_task_message="")

        expected = "You are a text correction assistant. Correct spelling and syntax. Return a list of lists. "
        assert result == expected
        mock_load_config.assert_called_once_with(config_purpose="prompt")

    @patch("textaicheck.prompt_generator.load_config")
    def test_generate_system_prompt_reformulation_english(self, mock_load_config):
        """Test system prompt generation for reformulation task in English"""
        mock_config = {
            "INITIAL_SYSTEM_MESSAGE_EN": "You are a text correction assistant. ",
            "TASK_REFORMULATION_EN": "Reformulate for clarity. ",
            "OUTPUT_FORMAT_EN": "Return a list of lists. ",
        }
        mock_load_config.return_value = mock_config

        result = _generate_system_prompt(task="reformulation", language="English", prompt_task_message="")

        expected = "You are a text correction assistant. Reformulate for clarity. Return a list of lists. "
        assert result == expected

    @patch("textaicheck.prompt_generator.load_config")
    def test_generate_system_prompt_translation_english(self, mock_load_config):
        """Test system prompt generation for translation task in English"""
        mock_config = {
            "INITIAL_SYSTEM_MESSAGE_EN": "You are a text correction assistant. ",
            "TASK_TRANSLATION_EN": "Translate the text. ",
            "OUTPUT_FORMAT_EN": "Return a list of lists. ",
        }
        mock_load_config.return_value = mock_config

        result = _generate_system_prompt(task="translation", language="English", prompt_task_message="")

        expected = "You are a text correction assistant. Translate the text. Return a list of lists. "
        assert result == expected

    @patch("textaicheck.prompt_generator.load_config")
    def test_generate_system_prompt_syntax_french(self, mock_load_config):
        """Test system prompt generation for syntax task in French"""
        mock_config = {
            "INITIAL_SYSTEM_MESSAGE_FR": "Vous êtes un assistant. ",
            "TASK_SYNTAX_FR": "Corriger l'orthographe. ",
            "OUTPUT_FORMAT_FR": "Retourner une liste. ",
        }
        mock_load_config.return_value = mock_config

        result = _generate_system_prompt(task="syntax", language="French", prompt_task_message="")

        expected = "Vous êtes un assistant. Corriger l'orthographe. Retourner une liste. "
        assert result == expected

    @patch("textaicheck.prompt_generator.load_config")
    def test_generate_system_prompt_reformulation_french(self, mock_load_config):
        """Test system prompt generation for reformulation task in French"""
        mock_config = {
            "INITIAL_SYSTEM_MESSAGE_FR": "Vous êtes un assistant. ",
            "TASK_REFORMULATION_FR": "Reformuler le texte. ",
            "OUTPUT_FORMAT_FR": "Retourner une liste. ",
        }
        mock_load_config.return_value = mock_config

        result = _generate_system_prompt(task="reformulation", language="French", prompt_task_message="")

        expected = "Vous êtes un assistant. Reformuler le texte. Retourner une liste. "
        assert result == expected

    @patch("textaicheck.prompt_generator.load_config")
    def test_generate_system_prompt_translation_french(self, mock_load_config):
        """Test system prompt generation for translation task in French"""
        mock_config = {
            "INITIAL_SYSTEM_MESSAGE_FR": "Vous êtes un assistant. ",
            "TASK_TRANSLATION_FR": "Traduire le texte. ",
            "OUTPUT_FORMAT_FR": "Retourner une liste. ",
        }
        mock_load_config.return_value = mock_config

        result = _generate_system_prompt(task="translation", language="French", prompt_task_message="")

        expected = "Vous êtes un assistant. Traduire le texte. Retourner une liste. "
        assert result == expected

    @patch("textaicheck.prompt_generator.load_config")
    def test_generate_system_prompt_with_custom_message(self, mock_load_config):
        """Test system prompt generation with custom task message"""
        mock_config = {
            "INITIAL_SYSTEM_MESSAGE_EN": "Initial. ",
            "TASK_SYNTAX_EN": "Task. ",
            "OUTPUT_FORMAT_EN": "Format. ",
        }
        mock_load_config.return_value = mock_config

        result = _generate_system_prompt(
            task="syntax",
            language="English",
            prompt_task_message="Custom instructions. "
        )

        expected = "Initial. Task. Format. Custom instructions. "
        assert result == expected

    @patch("textaicheck.prompt_generator.load_config")
    def test_generate_system_prompt_invalid_task_english(self, mock_load_config):
        """Test that invalid task raises ValueError for English"""
        mock_config = {
            "INITIAL_SYSTEM_MESSAGE_EN": "Initial. ",
            "OUTPUT_FORMAT_EN": "Format. ",
        }
        mock_load_config.return_value = mock_config

        with pytest.raises(ValueError, match="Invalid task"):
            _generate_system_prompt(task="invalid_task", language="English", prompt_task_message="")

    @patch("textaicheck.prompt_generator.load_config")
    def test_generate_system_prompt_invalid_task_french(self, mock_load_config):
        """Test that invalid task raises ValueError for French"""
        mock_config = {
            "INITIAL_SYSTEM_MESSAGE_FR": "Initial. ",
            "OUTPUT_FORMAT_FR": "Format. ",
        }
        mock_load_config.return_value = mock_config

        with pytest.raises(ValueError, match="Invalid task"):
            _generate_system_prompt(task="invalid_task", language="French", prompt_task_message="")

    @patch("textaicheck.prompt_generator.load_config")
    def test_generate_system_prompt_invalid_language(self, mock_load_config):
        """Test that invalid language raises ValueError"""
        mock_load_config.return_value = {}

        with pytest.raises(ValueError, match="Invalid Language"):
            _generate_system_prompt(task="syntax", language="Spanish", prompt_task_message="")


class TestGeneratePrompt:
    """Test suite for generate_prompt function"""

    @patch("textaicheck.prompt_generator._generate_system_prompt")
    def test_generate_prompt_basic(self, mock_generate_system):
        """Test basic prompt generation with data"""
        mock_generate_system.return_value = "System message content"
        data = [["1", "First text"], ["2", "Second text"]]

        result = generate_prompt(
            data=data,
            task="syntax",
            prompt_task_message="",
            language="English"
        )

        assert len(result) == 2
        assert isinstance(result[0], SystemMessage)
        assert isinstance(result[1], HumanMessage)
        assert result[0].content == "System message content"
        assert result[1].content == str(data)
        mock_generate_system.assert_called_once_with("syntax", "English", "")

    @patch("textaicheck.prompt_generator._generate_system_prompt")
    def test_generate_prompt_with_custom_message(self, mock_generate_system):
        """Test prompt generation with custom task message"""
        mock_generate_system.return_value = "Custom system message"
        data = [["id1", "text1"]]
        custom_message = "Please be extra careful with grammar."

        result = generate_prompt(
            data=data,
            task="reformulation",
            prompt_task_message=custom_message,
            language="French"
        )

        assert len(result) == 2
        assert result[0].content == "Custom system message"
        mock_generate_system.assert_called_once_with("reformulation", "French", custom_message)

    @patch("textaicheck.prompt_generator._generate_system_prompt")
    def test_generate_prompt_empty_data(self, mock_generate_system):
        """Test prompt generation with empty data list"""
        mock_generate_system.return_value = "System message"
        data = []

        result = generate_prompt(
            data=data,
            task="syntax",
            prompt_task_message="",
            language="English"
        )

        assert len(result) == 2
        assert isinstance(result[0], SystemMessage)
        assert isinstance(result[1], HumanMessage)
        assert result[1].content == "[]"

    @patch("textaicheck.prompt_generator._generate_system_prompt")
    def test_generate_prompt_single_entry(self, mock_generate_system):
        """Test prompt generation with single data entry"""
        mock_generate_system.return_value = "System message"
        data = [["123", "Single text entry"]]

        result = generate_prompt(
            data=data,
            task="translation",
            prompt_task_message="",
            language="English"
        )

        assert len(result) == 2
        assert result[1].content == "[['123', 'Single text entry']]"

    @patch("textaicheck.prompt_generator._generate_system_prompt")
    def test_generate_prompt_special_characters_in_data(self, mock_generate_system):
        """Test prompt generation with special characters in data"""
        mock_generate_system.return_value = "System message"
        data = [['1', 'Text with\nnewlines'], ["2", "Special: @#$%"]]

        result = generate_prompt(
            data=data,
            task="syntax",
            prompt_task_message="",
            language="English"
        )

        assert len(result) == 2
        assert "Text with\\nnewlines" in result[1].content
        assert "Special: @#$%" in result[1].content

    @patch("textaicheck.prompt_generator._generate_system_prompt")
    def test_generate_prompt_default_language(self, mock_generate_system):
        """Test that default language is English"""
        mock_generate_system.return_value = "System message"
        data = [["1", "text"]]

        result = generate_prompt(
            data=data,
            task="syntax",
            prompt_task_message=""
        )

        # Verify English was used as default
        mock_generate_system.assert_called_once_with("syntax", "English", "")

    @patch("textaicheck.prompt_generator._generate_system_prompt")
    def test_generate_prompt_propagates_exceptions(self, mock_generate_system):
        """Test that exceptions from _generate_system_prompt are propagated"""
        mock_generate_system.side_effect = ValueError("Invalid task")
        data = [["1", "text"]]

        with pytest.raises(ValueError, match="Invalid task"):
            generate_prompt(
                data=data,
                task="invalid",
                prompt_task_message="",
                language="English"
            )
