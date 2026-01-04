import pytest
from textaicheck.config_loader import load_config
from pathlib import Path
from unittest.mock import patch, mock_open
import yaml
from unittest.mock import MagicMock

def test_load_config_prompt_success():
    """Test successful loading of prompt configuration"""
    mock_config = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Please correct the following text"}
    ]

    with patch("builtins.open", mock_open(read_data=yaml.dump(mock_config))):
        with patch("pathlib.Path.exists", return_value=True):
            result = load_config("prompt")
            assert result == mock_config

def test_load_config_llm_success():
    """Test successful loading of LLM configuration"""
    mock_config = {
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "max_tokens": 1000
    }

    with patch("builtins.open", mock_open(read_data=yaml.dump(mock_config))):
        with patch("pathlib.Path.exists", return_value=True):
            result = load_config("llm")
            assert result == mock_config

def test_load_config_prompt_file_not_exists():
    """Test when prompt config file does not exist"""
    with patch("pathlib.Path.exists", return_value=False):
        with pytest.raises(ValueError, match="❌ Failed to load LLM prompt: {e}"):
            load_config("prompt")



def test_load_config_llm_file_not_exists():
    """Test when LLM config file does not exist"""
    with patch("pathlib.Path.exists", return_value=False):
        with pytest.raises(ValueError, match="❌ Failed to load LLM configuration parameters: {e}"):
            load_config("llm")

