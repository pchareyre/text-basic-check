import yaml
from pathlib import Path


def load_config(config_purpose: str) -> list:
    """
    Function to load YAML configurations for LLM prompt or configuration.
    Parameters:
    type (str): The type of configuration to load, either "prompt" or "llm".
    Returns:
    list: The loaded configuration as a list.
    Raises:
    ValueError: If the type is invalid or if the config file cannot be loaded."""
    if config_purpose == "prompt":
        try:
            config_file_path = Path(__file__).parent / "config/prompt_instructions.yaml"
            if config_file_path.exists():
                with open(config_file_path, "r") as f:
                    return yaml.safe_load(f)
            else:
                raise ValueError("❌ Configuration file does not exist at {config_file_path}.")
        except Exception as e:
            raise ValueError("❌ Failed to load LLM prompt: {e}")
    elif config_purpose == "llm":
        try:
            config_file_path = Path(__file__).parent / "config/llm_config.yaml"
            if config_file_path.exists():
                with open(config_file_path, "r") as f:
                    return yaml.safe_load(f)
            else:
                raise ValueError("❌ Configuration file does not exist at {config_file_path}.")
        except Exception as e:
            raise ValueError("❌ Failed to load LLM configuration parameters: {e}")
    else:
        raise ValueError("❌ Invalid configuration type")

