# text-basic-check

A simple spell-checking and syntax correction library for Python that doesn't use generative AI. Built with SymSpell for high-performance spell checking.

## Features

- ✅ Basic spell checking
- ✅ Find misspelled words
- ✅ Get spelling suggestions
- ✅ Auto-correct text
- ✅ Text analysis with detailed error information
- ✅ High-performance spell checking with SymSpell
- 🔄 Multi-language support (currently English, extensible)
- ⭐ **NEW**: T5-small ONNX offline text correction (grammar/syntax/style)

## Advanced: T5-ONNX Text Correction

For advanced grammar, syntax, and style correction, this repository now includes support for offline T5-small ONNX inference. This feature:

- Works completely offline (no internet required on target machine)
- Uses quantized INT8 ONNX models for fast CPU inference
- Supports Windows deployment with Python scripts
- Provides 100-400ms latency per sentence (greedy decoding)

**📖 See [README_T5_ONNX.md](README_T5_ONNX.md) for complete setup and usage guide.**

Quick example:
```bash
# After setup (see README_T5_ONNX.md)
python inference_t5_onnx.py --text "Corrige: je vais au magazin."
```

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

## Performance Demo

To see performance metrics and comparison:

```bash
python performance_demo.py
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
- [x] Basic spell checker module with SymSpell
- [x] Core functionality: check, find errors, suggest, correct
- [x] Basic tests
- [x] Simple usage example
- [x] Performance optimizations with SymSpell

### Phase 2: Enhanced Functionality (Planned)
- [ ] Grammar checking
- [ ] Text normalization
- [ ] Context-aware corrections
- [ ] Support for multiple languages
- [ ] Custom dictionaries

### Phase 3: Advanced Features (Future)
- [x] Performance optimizations (SymSpell integration)
- [ ] Batch processing
- [ ] File format support (txt, doc, etc.)
- [ ] Command-line interface
- [ ] Configuration options

## Performance

This library now uses **SymSpell** for spell checking, which provides significant performance improvements over traditional implementations:

- **Fast lookups**: O(1) average case complexity
- **Efficient memory usage**: Optimized dictionary structure
- **Frequency-based ranking**: More accurate suggestions
- **Scalable**: Performance remains consistent with larger texts

Run `python performance_demo.py` to see performance metrics on your system.

## Why SymSpell?

SymSpell is a symmetric delete spelling correction algorithm that is significantly faster than other spell checking algorithms like Norvig's or BK-trees. It achieves this by pre-generating all possible deletes within a given edit distance and storing them in a dictionary, enabling O(1) lookup times.

## License

MIT License

## Contributing

Contributions are welcome! This library is being developed incrementally, focusing on basic, reliable functionality without generative AI.