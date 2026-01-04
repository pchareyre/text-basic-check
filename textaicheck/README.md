# TextAICheck 
[![Python Version](https://img.shields.io/badge/python-3.12|3.13-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Internal-red.svg)](LICENSE)

## Overview
This Python library provides advanced text correction capabilities, including:
- **Spell Check** using `pyspellchecker` (lightweight and efficient)
- **Syntax Correction** using either a Small Language Model (SLM) or a  Large Language Model (LLM)
- **Text Reformulation** using SLM or LLM for improved clarity and style
- **Text Translation** using SLM or LLM

The library is designed to process an input JSON object containing text that needs correction/reformulation/translation. It transforms the input in the most minimal way possible before sending requests to an SLM/LLM for syntax correction, reformulation or translation. It generates the corresponding efficient prompt in each case.

## Features
- **Orthographic Correction**: Performed locally using `pyspellchecker` for efficiency.
- **Syntax & Reformulation**: If requested in the input JSON, the library calls an SLM/LLM (via LangChain/OpenAI API or WebSocket).
- **Generation of prompt message for the LLM**: If no particular rules to follow are requested by the user a default prompt is used.
- **Minimal Transformation**: Input JSON is processed and prepared for SLM/LLM requests with minimal changes.
- **Formatted Output**: After processing, the output is structured and formatted according to a predefined schema.

## Architecture Overview

The library is organized into one unique module.
```
textaicheck/
├── textaicheck/  
│       ├──config/
│           ├── llm_config.yaml             # llm default input configuration 
│           ├── prompt_instructions.yaml    # hard-coded prompt instructions
│   ├── __init__.py                         # Module initialization and exports
│   ├── apply_changes.py                    # Applies LLM changes to input data
│   ├── config_loader.py                    # loads LLM config parameters
│   ├── input_output_data_types.py          # Typed Dictionaries to define input/output data objects
│   ├── json_text_splitter.py               # Split input data into orthography/syntax and reformulation tasks
│   ├── LinguisticCheck.py                  # Spell checking
│   ├── minify_json_to_pairs.py             # Functions to transform the data into minimal version
│   ├── prompt_generator.py                 # Generates prompt message for LLM
│   ├── spell_checker.py                    # Orthography checking functions
│   └── text_checkers.py                    # AdvancedTextCheck and BasicTextCheck class definitions and task functions
│
├── tests/                                  # Comprehensive Test Suite
│   ├── __init__.py
│   ├── test_apply_changes.py
│   ├── test_config_loader.py
│   └── test_json_text_splitter.py        
├── .env                                    # API_KEY information
├── __init__.py
├── poetry.lock                             # Poetry project configuration
├── pyproject.toml                          # Poetry project configuration
└── README.md                               # Project documentation
```



## Workflow
1. **Input**: A JSON object specifying text and correction options (spell check, syntax correction, reformulation).
2. **Processing**:
   - Spell check is applied using `pyspellchecker`.
   - If syntax correction or reformulation is requested, the text transformed into its minimal version, a prompt is generated and is sent to an SLM/LLM.
3. **Output**: The corrected and reformulated text is returned in a structured format.

## Installation
### User Installation
```bash
git clone https://gitlab.engine.capgemini.com/software-engineering/france/internal/computer-vision-practice/genaids/genaids.git
cd genaids/
git checkout -b release/DocSentinel release/DocSentinel
cd libs/textaicheck
```

### Dependencies
 - spacy (==3.8.7), 
 - langchain-openai (>=1.1.0,<2.0.0), 
 - pyspellchecker (>=0.8.3,<0.9.0)", 
 - spacy-langdetect (>=0.1.2,<0.2.0)", 
 - dotenv (>=0.9.9,<0.10.0)

Install dependencies
```
poetry install
```

## Usage
For basic orthographic correction using pyspellchecker
```
checker = BasicTextChecker()
corrected_data = checker.correct(data)
```
For advanced correction of text in data through LLM or SLM use AdvancedTextChecker(). Note that AdvancedTextChecker() 
can perform several tasks.
- *correct;* The correct() method takes as input different data segments. Each segment is a dictionary with keys text_id, 
text, and correction_type. This allows each segment to have a specific task (i.e., correct orthography, correct syntax 
or reformulate, ) performed on it.
- *correct_syntax;* The correct_syntax() method takes as input different data segments. Each segment is a dictionary with 
keys text_id and text. A syntax correction will be applied to all text segments.
- *reformulate;* The reformulate() method takes as input different data segments. Each segment is a dictionary with
  keys text_id and text. A reformulation will be applied to all text segments.
- *translate;* The translate() method takes as input different data segments. Each segment is a dictionary with keys text_id
and text. A translation will be applied to all text segments.

Next we show a few examples of how it works.
```
# Returns corrected text
checker = AdvancedTextChecker()
corrected_data = checker.correct(data)

# Returns corrected text and the original text 
checker = AdvancedTextChecker()
original_and_corrected_data = checker.correct_and_compare(data)
```

In the following each text segment only requires the *text_id* and *text* attributes.
```
# For syntax correction
checker = AdvancedTextChecker()
syntax_corrected_data = checker.correct_syntax(data)

# For reformulation
checker = AdvancedTextChecker()
reformulated_data = checker.reformulate(data)

# For translation
checker = AdvancedTextChecker(language="French")
translated_data = checker.translate(data)
```

Note that, .correct_and_compare() does the exact same thing as .correct(). However, 
.correct_and_compare() returns; the modified (i.e. corrected) message, as well as the original text. See below in Output
format

### Optional attribute setting
The following attributes are optional for AdvancedTextChecker(). If not provided the default ones will be used.
- model_name (default = "openai.gpt-5-mini")
- model_encoding (default = "o200k_base")
- temperature (default = 0.2)
- generative_engine_openai_api_url (default = https://openai.generative.engine.capgemini.com/v1)
- max_completion_tokens (default = 1000)
- language (default = "English")
- prompt_task_message (see below for explanation and an example)

## Prompt generator
The system prompt message is chosen internally by the tool based on the task to be performed
on each segment of the text, i.e., orthography, syntax, reformulation. The prompt is structured in
three parts; *initial message*, *task message*, and *output format message*. A fourth part can be added if the user wants
some specific message to be passed on to the LLM. To do so, the user defines the input attribute, *prompt task message*. 
It can be used, for instance, to force certain words to be unchanged. 

- Example prompt_task_message:
```
The following fixed expressions should not be corrected/reformulated or modified in any way; Capgemini Engineering, ER&D, Data&AI.
```

Initial message (hard-coded)
```
  You are a text correction assistant. You are given a list of lists. Each inner list contains two strings:
    1. A text ID
    2. A text
```
Output format message (hard-coded)
```
Output format:
    - Return a list of lists.
    - Each inner list must contain exactly two elements:
        1. The original text ID
        2. The corrected text

  Important:
    - Do not include any extra text, explanations, or formatting.
    - The output must strictly be a list of lists in the specified format.
```

### Example with a different input attributes than default
For example,
```
checker = AdvancedTextChecker(model_name = "gpt-4", temperature=0.3)
corrected_data = checker.correct(data)
```

## Configuration
- **LLM Settings**: Configure API keys and model parameters in environment variables or a config file.
- **Spell Checker**: Uses default dictionary from `pyspellchecker`.

## Input Format
The input is a JSON object following a predefined schema:
```json
[
  {
    "text_id": "p01",
    "text": "This lib implements corretions using LLM.",
    "correction_type": [
      "orthography",
      "syntax",
      "reformulation"
    ]
  },
  {
    "text_id": "t01",
    "text": "Capgemini Engineering",
    "correction_type": [
      "orthography"
    ]
  }
  
]
```
It may contain extra attributes, but they are ignored during analysis by textAIcheck.

# Output Formats
The output is returned as a JSON object following a predefined schema:
```json
[
  {
   "text_id": "p01", 
   "modified_text": "This library applied corrections using LLM."
  },
  {
    "text_id": "t01",
    "modified_text": "Capgemini Engineering"
  }
]
```
In the case in which correct_and_compare() is called an extra attribute (namely, "original_text") is returned.
```json
[
  {
    "text_id": "p01", 
    "modified_text": "This library applied corrections using LLM.", 
    "original_text": "This lib implements corrections using LLM."
  },
  {
    "text_id": "t01",
    "modified_text": "Capgemini Engineering",
    "original_text": "Capgemini Engineering"
  }
]
```
Note that this library does not contain any postprocessing of the result from the LLM. That means that if a segment of 
the text was not modified by the LLM, it will still return the segment as "modified_text". The docx extraction/imputation
library contains the required postprocessing tools to identify which text has been modified and which not.

## Sanity Check (*text_id*)
All text segments must be processed by the LLM. Each segment is identified by a unique *text_id*. The system raises a
*ValueError* if any segment is missing from the LLM response. This *ensures* complete analysis coverage, as the LLM must
return results for all segments—including those requiring no changes—to confirm evaluation has occurred.

## Testing 
The project includes comprehensive testing.

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest tests/ --cov=term-missing
```

## Contributors

- Moez El GABSI, <moez.el-gabsi@capgemini.com>
- Maialen LARRANAGA ZUMETA , <maialen.larranagazumeta@capgemini.com>

## License

This project is proprietary and for internal use only. Unauthorized distribution is prohibited.
