"""
Example demonstration with French text request simulation.

This script demonstrates the spell checker on a simulated text with
spelling errors, as requested in the problem statement.
"""

from text_basic_check import SpellChecker
import time


def main():
    print("=" * 70)
    print("Demonstration: Text-Basic-Check with SymSpell")
    print("=" * 70)
    print()
    
    # Initialize the spell checker
    print("Initializing spell checker with SymSpell...")
    start = time.time()
    checker = SpellChecker(language='en')
    init_time = time.time() - start
    print(f"✓ Initialized in {init_time:.3f} seconds")
    print()
    
    # Sample text with various spelling errors
    text = """
    Ths is a demonstrtion of the spel checker. It containz severl
    intentonal erors to show how the systm works. The performnce 
    improvments with SymSpel are signifcant compared to the prevous
    implementtion using PySpelChecker.
    """
    
    print("Original text with errors:")
    print("-" * 70)
    print(text)
    print("-" * 70)
    print()
    
    # Find errors
    print("Finding spelling errors...")
    start = time.time()
    errors = checker.find_errors(text)
    find_time = time.time() - start
    print(f"✓ Found {len(errors)} errors in {find_time*1000:.2f} ms")
    print(f"  Errors: {errors}")
    print()
    
    # Get suggestions for each error
    print("Suggestions for each error:")
    print("-" * 70)
    for error in errors:
        suggestions = checker.get_suggestions(error, max_suggestions=3)
        print(f"  {error:15} → {suggestions}")
    print()
    
    # Correct the entire text
    print("Correcting text...")
    start = time.time()
    corrected = checker.correct_text(text)
    correct_time = time.time() - start
    print(f"✓ Corrected in {correct_time*1000:.2f} ms")
    print()
    
    print("Corrected text:")
    print("-" * 70)
    print(corrected)
    print("-" * 70)
    print()
    
    # Full analysis
    print("Full analysis:")
    print("-" * 70)
    start = time.time()
    analysis = checker.analyze(text)
    analyze_time = time.time() - start
    print(f"✓ Analysis completed in {analyze_time*1000:.2f} ms")
    print(f"  Total errors found: {analysis['error_count']}")
    print(f"  Errors: {analysis['errors']}")
    print()
    print("  Top suggestions for each error:")
    for error, suggestions in analysis['corrections'].items():
        print(f"    {error:15} → {suggestions[:3]}")
    print()
    
    # Performance summary
    print("=" * 70)
    print("Performance Summary")
    print("=" * 70)
    print(f"  Initialization:  {init_time*1000:.2f} ms")
    print(f"  Find errors:     {find_time*1000:.2f} ms")
    print(f"  Correct text:    {correct_time*1000:.2f} ms")
    print(f"  Full analysis:   {analyze_time*1000:.2f} ms")
    print()
    print("✓ SymSpell provides excellent performance for spell checking!")
    print()


if __name__ == "__main__":
    main()
