# Performance Testing Suite

This directory contains tools for benchmarking and evaluating the performance of the text-basic-check spell checker.

## Directory Structure

```
perf_tests/
├── README.md                      # This file
├── generate_corpus.py             # Generate test corpus with errors
├── benchmark_corrections.py       # Benchmark spell checker performance
├── corpus/                        # Test corpus files (shared across branches)
│   ├── corpus_ortho_syntax_ground_truth.txt
│   ├── corpus_ortho_errors_only.txt
│   └── corpus_ortho_syntax_errors_both.txt
└── results_orthograph_only/       # Branch-specific benchmark results
    ├── benchmark_results_ortho_only.txt
    └── benchmark_results_ortho_syntax_both.txt
```

## Branch-Specific Organization

To avoid merge conflicts between branches, each branch stores results in its own subfolder:
- `feature/orthograph-only` branch → `results_orthograph_only/` (this branch)
- `feature/ortho-syntax-t5` branch → `results_ortho_syntax_t5/`

The corpus files in `corpus/` are shared across all branches to ensure fair comparison.

## Usage

### 1. Generate Test Corpus

Generate a corpus of 500 sentences with different types of errors:

```bash
cd perf_tests
python generate_corpus.py
```

This creates three files in the `corpus/` directory:
- **corpus_ortho_syntax_ground_truth.txt**: 500 grammatically correct sentences
- **corpus_ortho_errors_only.txt**: Same sentences with orthographic (spelling) errors only
- **corpus_ortho_syntax_errors_both.txt**: Sentences with both orthographic and syntax errors

### 2. Run Benchmarks

Run the benchmarking suite to evaluate spell checker performance:

```bash
cd perf_tests
python benchmark_corrections.py
```

This will:
1. Load the ground truth and error corpora
2. Run the spell checker on each error corpus
3. Calculate metrics (precision, recall, F1-score, accuracy)
4. Generate detailed results files in the `results/` directory

## Metrics Explained

### Precision
- **Formula**: TP / (TP + FP)
- **Meaning**: Of all corrections made, what percentage were correct
- **High precision**: Few incorrect corrections

### Recall
- **Formula**: TP / (TP + FN)
- **Meaning**: Of all errors present, what percentage were fixed correctly
- **High recall**: Few errors missed

### F1-Score
- **Formula**: 2 × (Precision × Recall) / (Precision + Recall)
- **Meaning**: Harmonic mean of precision and recall
- **Balanced measure**: Good overall performance indicator

### Accuracy
- **Formula**: (TP + TN) / (TP + TN + FP + FN)
- **Meaning**: Overall correctness of all word-level decisions

### Confusion Matrix Terms
- **TP (True Positives)**: Errors correctly fixed
- **FP (False Positives)**: Incorrect corrections or correct words wrongly changed
- **FN (False Negatives)**: Errors that were not fixed
- **TN (True Negatives)**: Correct words that were kept correct

## Example Results

Typical performance on orthographic errors only:
- Precision: ~85%
- Recall: ~95%
- F1-Score: ~90%

Performance degrades on mixed orthographic and syntax errors since the spell checker focuses on orthography.

## Extending the Suite

To add new test scenarios:
1. Modify `generate_corpus.py` to add new error patterns
2. Update `benchmark_corrections.py` to add new evaluation metrics
3. Create new corpus files in the `corpus/` directory
4. Add corresponding benchmark configurations

## Notes

- The corpus is generated with a fixed random seed (42) for reproducibility
- Error rates are configurable in `generate_corpus.py`
- Timing metrics are included to measure performance speed
- Results are saved as human-readable text files for easy review
