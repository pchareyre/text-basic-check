"""
Simple example of using the text-basic-check library.
"""

from text_basic_check import SpellChecker


def main():
    # Initialize the spell checker
    checker = SpellChecker(language='en')
    
    # Example text with spelling errors
    text = "This is a smple text with som erors in it."
    
    print("Original text:")
    print(text)
    print()
    
    # Find errors
    errors = checker.find_errors(text)
    print(f"Found {len(errors)} errors: {errors}")
    print()
    
    # Get suggestions for each error
    print("Suggestions:")
    for error in errors:
        suggestions = checker.get_suggestions(error)
        print(f"  {error} -> {suggestions}")
    print()
    
    # Correct the text
    corrected = checker.correct_text(text)
    print("Corrected text:")
    print(corrected)
    print()
    
    # Full analysis
    analysis = checker.analyze(text)
    print("Full analysis:")
    print(f"  Error count: {analysis['error_count']}")
    print(f"  Errors: {analysis['errors']}")
    print(f"  Corrections: {analysis['corrections']}")


if __name__ == "__main__":
    main()
