from typing import List
from .config_loader import load_config
from langchain_core.messages import HumanMessage, SystemMessage


def _generate_system_prompt(task: str, language: str = "English", prompt_task_message: str="") -> str:
    """
    Generate a system prompt based on the task.

    Args:
        task (str): The purpose of the prompt. Options: 'syntax', 'reformulation', 'translation'.
        text (str): The text to process.
        language (str): Target language for translation (default: 'fr').

    Returns:
        str: A system message
    """
    # Load configuration settings for the LLM
    config = load_config(config_purpose="prompt")
    if language == "English":
        initial_sys_message = config.get("INITIAL_SYSTEM_MESSAGE_EN", "")
        output_format = config.get("OUTPUT_FORMAT_EN", "")
        if task == "syntax":
            task_reference = config.get("TASK_SYNTAX_EN", "")
        elif task == "reformulation":
            task_reference = config.get("TASK_REFORMULATION_EN", "")
        elif task == "translation":
            task_reference = config.get("TASK_TRANSLATION_EN", "")
        else:
            raise ValueError("Invalid task. Use 'syntax', 'reformulation' or 'translation'.")
    elif language == "French":
        initial_sys_message = config.get("INITIAL_SYSTEM_MESSAGE_FR", "")
        output_format = config.get("OUTPUT_FORMAT_FR", "")
        if task == "syntax":
            task_reference = config.get("TASK_SYNTAX_FR", "")
        elif task == "reformulation":
            task_reference = config.get("TASK_REFORMULATION_FR", "")
        elif task == "translation":
            task_reference = config.get("TASK_TRANSLATION_FR", "")
        else:
            raise ValueError("Invalid task. Use 'syntax', 'reformulation' or 'translation'.")
    else:
        raise ValueError("Invalid Language. Use English or French.")
    system_message = (
        initial_sys_message + task_reference + output_format + prompt_task_message
    )

    return system_message


def generate_prompt(data: List[List], task: str,  prompt_task_message: str, language: str = "English"):
    """
    Generate a system prompt based on the task.

    Args:
        data (List[List]): input dictionary entries containing text to perform task on
        task (str): The purpose of the prompt. Options: 'syntax', 'reformulation', 'translation'.
        language(str):
    Returns:
        List :  with 'system' and 'user' messages.
    """
    system_message = _generate_system_prompt(task, language, prompt_task_message)
    messages = [
        SystemMessage(content=system_message),
        HumanMessage(content=str(data)),
    ]
    return messages
