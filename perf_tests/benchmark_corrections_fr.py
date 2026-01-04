"""
Benchmark spell checker performance with precision, recall, and F1-score metrics.

This script:
1. Loads ground truth and error corpus
2. Runs spell checker on error corpus
3. Compares corrections with ground truth
4. Calculates precision, recall, and F1-score
5. Writes metrics to text files
"""

import os
import sys
import time
from typing import List, Dict, Tuple

# Add parent directory to path to import text_basic_check
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from text_basic_check import SpellChecker


def load_corpus(filepath: str) -> List[str]:
    """Load corpus from file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]


def tokenize_for_comparison(text: str) -> List[str]:
    """Tokenize text for word-level comparison."""
    import re
    # Split on whitespace and remove punctuation
    words = []
    for token in text.split():
        word = re.sub(r'^[^\w\']+|[^\w\']+$', '', token)
        if word:
            words.append(word.lower())
    return words


def calculate_metrics(ground_truth: List[str], corrected: List[str], original_errors: List[str]) -> Dict:
    """
    Calculate precision, recall, and F1-score.
    
    Metrics:
    - True Positives (TP): Words that were incorrect and corrected to the right word
    - False Positives (FP): Words that were changed incorrectly (wrong correction or correct word changed)
    - False Negatives (FN): Words that remained incorrect (errors not fixed)
    - True Negatives (TN): Words that were already correct and stayed correct
    """
    total_sentences = len(ground_truth)
    
    tp = 0  # Correct corrections
    fp = 0  # Incorrect corrections
    fn = 0  # Missed errors
    tn = 0  # Correctly kept words
    
    total_errors_in_corpus = 0
    total_corrections_made = 0
    
    for gt_sentence, corrected_sentence, error_sentence in zip(ground_truth, corrected, original_errors):
        gt_words = tokenize_for_comparison(gt_sentence)
        corrected_words = tokenize_for_comparison(corrected_sentence)
        error_words = tokenize_for_comparison(error_sentence)
        
        # Make sure all have same length (padding if needed)
        max_len = max(len(gt_words), len(corrected_words), len(error_words))
        gt_words += [''] * (max_len - len(gt_words))
        corrected_words += [''] * (max_len - len(corrected_words))
        error_words += [''] * (max_len - len(error_words))
        
        for gt_word, corr_word, err_word in zip(gt_words, corrected_words, error_words):
            if not gt_word and not err_word:
                continue
            
            # Check if there was an error
            has_error = (err_word != gt_word)
            
            if has_error:
                total_errors_in_corpus += 1
                
                # Check if correction was made
                if corr_word != err_word:
                    total_corrections_made += 1
                    
                    # Check if correction is right
                    if corr_word == gt_word:
                        tp += 1  # Correct correction
                    else:
                        fp += 1  # Wrong correction
                else:
                    fn += 1  # Error not fixed
            else:
                # No error in original
                if corr_word == gt_word:
                    tn += 1  # Correctly kept
                else:
                    fp += 1  # Incorrectly changed
    
    # Calculate metrics
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0.0
    
    return {
        'true_positives': tp,
        'false_positives': fp,
        'false_negatives': fn,
        'true_negatives': tn,
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score,
        'accuracy': accuracy,
        'total_sentences': total_sentences,
        'total_errors_in_corpus': total_errors_in_corpus,
        'total_corrections_made': total_corrections_made,
    }


def benchmark_spell_checker(ground_truth_file: str, error_file: str, output_file: str, language: str = 'en'):
    """
    Benchmark spell checker on given corpus.
    
    Args:
        ground_truth_file: Path to ground truth corpus
        error_file: Path to corpus with errors
        output_file: Path to output metrics file
        language: Language code ('en' or 'fr')
    """
    print(f"\n{'='*70}")
    print(f"Benchmarking: {error_file}")
    print(f"{'='*70}\n")
    
    # Load corpus
    print("Loading corpus...")
    ground_truth = load_corpus(ground_truth_file)
    error_corpus = load_corpus(error_file)
    
    print(f"  Ground truth: {len(ground_truth)} sentences")
    print(f"  Error corpus: {len(error_corpus)} sentences")
    
    # Initialize spell checker
    print(f"\nInitializing spell checker ({language})...")
    start_time = time.time()
    checker = SpellChecker(language=language)
    init_time = time.time() - start_time
    print(f"  ✓ Initialized in {init_time:.3f} seconds")
    
    # Correct all sentences
    print("\nCorrecting sentences...")
    start_time = time.time()
    corrected = []
    for i, sentence in enumerate(error_corpus):
        if (i + 1) % 100 == 0:
            print(f"  Progress: {i+1}/{len(error_corpus)} sentences")
        corrected.append(checker.correct_text(sentence))
    correction_time = time.time() - start_time
    print(f"  ✓ Corrected {len(error_corpus)} sentences in {correction_time:.3f} seconds")
    print(f"  Average: {correction_time/len(error_corpus)*1000:.2f} ms per sentence")
    
    # Calculate metrics
    print("\nCalculating metrics...")
    metrics = calculate_metrics(ground_truth, corrected, error_corpus)
    
    # Display results
    print(f"\n{'='*70}")
    print("RESULTS")
    print(f"{'='*70}\n")
    
    print(f"Total sentences:          {metrics['total_sentences']}")
    print(f"Total errors in corpus:   {metrics['total_errors_in_corpus']}")
    print(f"Total corrections made:   {metrics['total_corrections_made']}")
    print()
    print(f"True Positives (TP):      {metrics['true_positives']} (correct corrections)")
    print(f"False Positives (FP):     {metrics['false_positives']} (wrong corrections)")
    print(f"False Negatives (FN):     {metrics['false_negatives']} (missed errors)")
    print(f"True Negatives (TN):      {metrics['true_negatives']} (correctly kept)")
    print()
    print(f"Precision:                {metrics['precision']:.4f} ({metrics['precision']*100:.2f}%)")
    print(f"Recall:                   {metrics['recall']:.4f} ({metrics['recall']*100:.2f}%)")
    print(f"F1-Score:                 {metrics['f1_score']:.4f} ({metrics['f1_score']*100:.2f}%)")
    print(f"Accuracy:                 {metrics['accuracy']:.4f} ({metrics['accuracy']*100:.2f}%)")
    print()
    print(f"Initialization time:      {init_time:.3f} seconds")
    print(f"Total correction time:    {correction_time:.3f} seconds")
    print(f"Average per sentence:     {correction_time/len(error_corpus)*1000:.2f} ms")
    
    # Write to file
    print(f"\nWriting results to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write(f"BENCHMARK RESULTS: {error_file}\n")
        f.write("="*70 + "\n\n")
        
        f.write("CONFIGURATION\n")
        f.write("-"*70 + "\n")
        f.write(f"Ground truth file: {ground_truth_file}\n")
        f.write(f"Error corpus file: {error_file}\n")
        f.write(f"Spell checker:     SymSpell (text-basic-check)\n")
        f.write(f"Language:          {language.upper()}\n")
        f.write("\n")
        
        f.write("CORPUS STATISTICS\n")
        f.write("-"*70 + "\n")
        f.write(f"Total sentences:          {metrics['total_sentences']}\n")
        f.write(f"Total errors in corpus:   {metrics['total_errors_in_corpus']}\n")
        f.write(f"Total corrections made:   {metrics['total_corrections_made']}\n")
        f.write("\n")
        
        f.write("CONFUSION MATRIX\n")
        f.write("-"*70 + "\n")
        f.write(f"True Positives (TP):      {metrics['true_positives']} (correct corrections)\n")
        f.write(f"False Positives (FP):     {metrics['false_positives']} (wrong corrections)\n")
        f.write(f"False Negatives (FN):     {metrics['false_negatives']} (missed errors)\n")
        f.write(f"True Negatives (TN):      {metrics['true_negatives']} (correctly kept)\n")
        f.write("\n")
        
        f.write("PERFORMANCE METRICS\n")
        f.write("-"*70 + "\n")
        f.write(f"Precision:                {metrics['precision']:.4f} ({metrics['precision']*100:.2f}%)\n")
        f.write(f"  Formula: TP / (TP + FP)\n")
        f.write(f"  Interpretation: Of all corrections made, what % were correct\n")
        f.write("\n")
        f.write(f"Recall:                   {metrics['recall']:.4f} ({metrics['recall']*100:.2f}%)\n")
        f.write(f"  Formula: TP / (TP + FN)\n")
        f.write(f"  Interpretation: Of all errors, what % were fixed correctly\n")
        f.write("\n")
        f.write(f"F1-Score:                 {metrics['f1_score']:.4f} ({metrics['f1_score']*100:.2f}%)\n")
        f.write(f"  Formula: 2 * (Precision * Recall) / (Precision + Recall)\n")
        f.write(f"  Interpretation: Harmonic mean of precision and recall\n")
        f.write("\n")
        f.write(f"Accuracy:                 {metrics['accuracy']:.4f} ({metrics['accuracy']*100:.2f}%)\n")
        f.write(f"  Formula: (TP + TN) / (TP + TN + FP + FN)\n")
        f.write(f"  Interpretation: Overall correctness of all words\n")
        f.write("\n")
        
        f.write("TIMING METRICS\n")
        f.write("-"*70 + "\n")
        f.write(f"Initialization time:      {init_time:.3f} seconds\n")
        f.write(f"Total correction time:    {correction_time:.3f} seconds\n")
        f.write(f"Average per sentence:     {correction_time/len(error_corpus)*1000:.2f} ms\n")
        f.write("\n")
        
        f.write("EXAMPLES\n")
        f.write("-"*70 + "\n")
        for i in range(min(5, len(ground_truth))):
            f.write(f"\nExample {i+1}:\n")
            f.write(f"  Ground truth: {ground_truth[i]}\n")
            f.write(f"  With errors:  {error_corpus[i]}\n")
            f.write(f"  Corrected:    {corrected[i]}\n")
        f.write("\n")
        
        f.write("="*70 + "\n")
    
    print(f"  ✓ Results saved to {output_file}")
    
    return metrics


def main():
    """Run benchmarks on both French error corpora."""
    print("\n" + "="*70)
    print("TEXT-BASIC-CHECK BENCHMARKING SUITE (FRENCH)")
    print("="*70)
    
    # Get directory paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    corpus_dir = os.path.join(script_dir, 'corpus')
    results_dir = os.path.join(script_dir, 'results_orthograph_only')
    
    # Ensure results directory exists
    os.makedirs(results_dir, exist_ok=True)
    
    ground_truth_file = os.path.join(corpus_dir, 'corpus_ortho_syntax_ground_truth_fr.txt')
    
    # Check if French corpus exists
    if not os.path.exists(ground_truth_file):
        print(f"\nERROR: French corpus not found. Please generate it first:")
        print("  cd perf_tests")
        print("  python generate_corpus_fr.py")
        sys.exit(1)
    
    # Benchmark 1: Orthographic errors only (French)
    print("\n[1/2] Benchmarking French orthographic errors only...")
    metrics_ortho = benchmark_spell_checker(
        ground_truth_file,
        os.path.join(corpus_dir, 'corpus_ortho_errors_only_fr.txt'),
        os.path.join(results_dir, 'benchmark_results_ortho_only_fr.txt'),
        language='fr'
    )
    
    # Benchmark 2: Both orthographic and syntax errors (French)
    print("\n[2/2] Benchmarking French orthographic and syntax errors...")
    metrics_both = benchmark_spell_checker(
        ground_truth_file,
        os.path.join(corpus_dir, 'corpus_ortho_syntax_errors_both_fr.txt'),
        os.path.join(results_dir, 'benchmark_results_ortho_syntax_both_fr.txt'),
        language='fr'
    )
    
    # Summary comparison
    print(f"\n{'='*70}")
    print("SUMMARY COMPARISON (FRENCH)")
    print(f"{'='*70}\n")
    
    print(f"{'Metric':<25} {'Ortho Only':>15} {'Ortho + Syntax':>15}")
    print("-"*70)
    print(f"{'Precision':<25} {metrics_ortho['precision']:>14.2%} {metrics_both['precision']:>15.2%}")
    print(f"{'Recall':<25} {metrics_ortho['recall']:>14.2%} {metrics_both['recall']:>15.2%}")
    print(f"{'F1-Score':<25} {metrics_ortho['f1_score']:>14.2%} {metrics_both['f1_score']:>15.2%}")
    print(f"{'Accuracy':<25} {metrics_ortho['accuracy']:>14.2%} {metrics_both['accuracy']:>15.2%}")
    print()
    
    print("Benchmarking complete!")
    print(f"\nGenerated files in {results_dir}:")
    print("  - benchmark_results_ortho_only_fr.txt")
    print("  - benchmark_results_ortho_syntax_both_fr.txt")
    print()


if __name__ == "__main__":
    main()
