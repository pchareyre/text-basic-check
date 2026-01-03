# text-basic-check

A simple spell-checking and syntax correction library for Python that doesn't use generative AI. Built incrementally with PySpellChecker as the core engine.

## Features

- ✅ Basic spell checking
- ✅ Find misspelled words
- ✅ Get spelling suggestions
- ✅ Auto-correct text
- ✅ Text analysis with detailed error information
- 🔄 Multi-language support (via PySpellChecker)

## Installation

```bash
pip install -r requirements.txt
```

Or install in development mode:

```bash
pip install -e .
```

## Quick Start

```python
from text_basic_check import SpellChecker

# Initialize the spell checker
checker = SpellChecker(language='en')

# Check a single word
is_correct = checker.check_word('hello')  # True
is_correct = checker.check_word('helo')   # False

# Find errors in text
text = "This is a smple text with erors"
errors = checker.find_errors(text)
print(errors)  # ['smple', 'erors']

# Get suggestions for a misspelled word
suggestions = checker.get_suggestions('helo')
print(suggestions)  # ['hello', 'help', 'held', ...]

# Correct a single word
corrected = checker.correct_word('helo')
print(corrected)  # 'hello'

# Correct entire text
corrected_text = checker.correct_text(text)
print(corrected_text)  # "This is a simple text with errors"

# Full analysis
analysis = checker.analyze(text)
print(analysis)
# {
#     'errors': ['smple', 'erors'],
#     'corrections': {'smple': ['simple', ...], 'erors': ['errors', ...]},
#     'error_count': 2
# }
```

## Running the Example

```bash
python example.py
```

## Running Tests

```bash
python -m pytest tests/
```

Or with unittest:

```bash
python -m unittest discover tests
```

## Project Structure

```
text-basic-check/
├── text_basic_check/      # Main package
│   ├── __init__.py        # Package initialization
│   └── spell_checker.py   # Spell checker module
├── tests/                 # Test suite
│   ├── __init__.py
│   └── test_spell_checker.py
├── example.py             # Usage example
├── requirements.txt       # Dependencies
├── setup.py              # Package setup
└── README.md             # This file
```

## Development Roadmap

### Phase 1: Basic Spell Checking ✅
- [x] Project setup and structure
- [x] Basic spell checker module with PySpellChecker
- [x] Core functionality: check, find errors, suggest, correct
- [x] Basic tests
- [x] Simple usage example

### Phase 2: Enhanced Functionality (Planned)
- [ ] Grammar checking
- [ ] Text normalization
- [ ] Context-aware corrections
- [ ] Support for multiple languages
- [ ] Custom dictionaries

### Phase 3: Advanced Features (Future)
- [ ] Performance optimizations
- [ ] Batch processing
- [ ] File format support (txt, doc, etc.)
- [ ] Command-line interface
- [ ] Configuration options

## License

MIT License

## Contributing

Contributions are welcome! This library is being developed incrementally, focusing on basic, reliable functionality without generative AI.