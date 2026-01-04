# Performance Testing Implementation Summary

## Overview

This document summarizes the performance testing infrastructure implemented for the text-basic-check project across multiple branches.

## What Was Implemented

### 1. Corpus Generation (`generate_corpus.py`)
- Generates 500 grammatically correct sentences (ground truth)
- Creates two error variants:
  - **corpus_ortho_errors_only.txt**: Orthographic (spelling) errors only
  - **corpus_ortho_syntax_errors_both.txt**: Both orthographic and syntax errors
- Uses fixed random seed (42) for reproducibility
- Error injection includes:
  - Character substitution (e.g., 'a' → 'e')
  - Character omission
  - Character duplication
  - Character transposition
  - Syntax errors (missing articles, wrong verb forms, etc.)

### 2. Benchmarking Scripts

#### For feature/orthograph-only branch: `benchmark_corrections.py`
- Uses SymSpell-based spell checker from text_basic_check module
- Evaluates performance on both error corpora
- Saves results to `results_orthograph_only/`

#### For feature/ortho-syntax-t5 branch: `benchmark_corrections_t5.py`
- Uses T5-small ONNX model for grammar correction
- Evaluates performance on both error corpora
- Saves results to `results_ortho_syntax_t5/`

### 3. Metrics Calculated

All benchmarks calculate the following metrics:

- **Precision**: TP / (TP + FP) - Of corrections made, % that were correct
- **Recall**: TP / (TP + FN) - Of errors present, % that were fixed correctly
- **F1-Score**: Harmonic mean of precision and recall
- **Accuracy**: (TP + TN) / Total - Overall word-level correctness
- **Timing metrics**: Initialization time, total correction time, average per sentence

Confusion matrix breakdown:
- **TP (True Positives)**: Errors correctly fixed
- **FP (False Positives)**: Incorrect corrections or correct words wrongly changed
- **FN (False Negatives)**: Errors missed/not fixed
- **TN (True Negatives)**: Correct words kept correct

### 4. Clean Architecture

```
perf_tests/
├── README.md                          # Documentation
├── generate_corpus.py                 # Corpus generation
├── benchmark_corrections.py           # Spell checker benchmarking
├── benchmark_corrections_t5.py        # T5 model benchmarking
├── corpus/                            # Shared across branches
│   ├── corpus_ortho_syntax_ground_truth.txt
│   ├── corpus_ortho_errors_only.txt
│   └── corpus_ortho_syntax_errors_both.txt
├── results_orthograph_only/           # Branch-specific results
│   ├── benchmark_results_ortho_only.txt
│   └── benchmark_results_ortho_syntax_both.txt
└── results_ortho_syntax_t5/           # Branch-specific results
    ├── benchmark_results_ortho_only_t5.txt
    └── benchmark_results_ortho_syntax_both_t5.txt
```

**Key Design Decision**: Branch-specific result folders prevent merge conflicts when different branches are merged together.

## Initial Benchmark Results

### feature/orthograph-only Branch (SymSpell)

**Orthographic Errors Only:**
- Precision: 84.83%
- Recall: 95.32%
- F1-Score: 89.77%
- Accuracy: 96.53%
- Average speed: 0.06 ms per sentence

**Orthographic + Syntax Errors:**
- Precision: 38.33%
- Recall: 13.32%
- F1-Score: 19.77%
- Accuracy: 45.16%
- Average speed: 0.06 ms per sentence

**Analysis**: SymSpell performs excellently on pure spelling errors but struggles with syntax errors (as expected, since it's not designed for grammar correction).

### feature/ortho-syntax-t5 Branch

Results pending - requires T5 model to be exported and available. Script is ready to run once model is available at `t5-small-onnx-q/` directory.

## Usage Instructions

### Generate Corpus
```bash
cd perf_tests
python generate_corpus.py
```

### Run Benchmarks (SymSpell)
```bash
cd perf_tests
python benchmark_corrections.py
```

### Run Benchmarks (T5)
```bash
# First, ensure T5 model is exported
python export_model.py

# Then run benchmarks
cd perf_tests
python benchmark_corrections_t5.py
```

## Files Generated

### Corpus Files (in perf_tests/corpus/)
- `corpus_ortho_syntax_ground_truth.txt` (500 lines, ~23 KB)
- `corpus_ortho_errors_only.txt` (500 lines, ~23 KB)
- `corpus_ortho_syntax_errors_both.txt` (500 lines, ~24 KB)

### Result Files
- Branch-specific result files in respective `results_*/` folders
- Each contains detailed metrics, confusion matrix, timing, and examples
- Human-readable text format for easy review

## Branch Status

### ✅ feature/orthograph-only (via copilot/featureorthograph-only)
- Corpus generated
- Benchmarks implemented and run
- Results available
- README complete

### ✅ feature/ortho-syntax-t5
- Corpus generated
- T5-specific benchmarks implemented
- Results pending T5 model availability
- README complete
- Branch committed (push pending authentication)

## Next Steps

1. **On feature/ortho-syntax-t5**: Export T5 model and run benchmarks
2. **Comparison**: Compare results between SymSpell and T5 approaches
3. **Optimization**: Based on results, identify areas for improvement
4. **Extension**: Consider adding more error types or languages

## Benefits of This Implementation

1. **Reproducible**: Fixed random seed ensures consistent corpus generation
2. **Comprehensive**: Multiple metrics provide full picture of performance
3. **Merge-safe**: Branch-specific folders prevent conflicts
4. **Well-documented**: READMEs in each branch explain usage
5. **Extensible**: Easy to add new benchmarks or error types
6. **Fast**: Automated evaluation on 500 sentences in seconds
7. **Comparable**: Same corpus across branches enables fair comparison
