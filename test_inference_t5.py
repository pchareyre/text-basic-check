"""
Test cases for T5-ONNX text correction.
This file contains sample French sentences with errors for testing the inference.

Run tests with:
    python test_inference_t5.py

Or test individual cases manually with:
    python inference_t5_onnx.py --text "test phrase here"
"""

import subprocess
import sys
from pathlib import Path


# Test cases: (input_text, description)
TEST_CASES = [
    (
        "Corrige la syntaxe: je vais au magazin pour achetter du pain.",
        "Spelling errors: magazin -> magasin, achetter -> acheter"
    ),
    (
        "Corrige la syntaxe: les clients ont été livrés hier, mais le rapport manquent.",
        "Subject-verb agreement error: manquent -> manque"
    ),
    (
        "Corrige: Il à donné sont livre a son ami.",
        "Homophones errors: à -> a, sont -> son, a -> à"
    ),
    (
        "Améliore: Le texte est pas bon et contient erreurs.",
        "Missing negation article and determiner: est pas -> n'est pas, contient erreurs -> contient des erreurs"
    ),
    (
        "Corrige: Les enfants joue dans le jardin avec leur amis.",
        "Agreement errors: joue -> jouent, leur -> leurs"
    ),
]


def run_inference(text, model_dir="t5-small-onnx-q", num_beams=1, verbose=False):
    """
    Run inference on a single test case.
    
    Args:
        text: Input text to correct
        model_dir: Path to the model directory
        num_beams: Number of beams for beam search
        verbose: Print timing info
        
    Returns:
        Tuple of (success: bool, output: str, error: str)
    """
    cmd = [
        sys.executable,
        "inference_t5_onnx.py",
        "--model_dir", model_dir,
        "--text", text,
        "--num_beams", str(num_beams)
    ]
    
    if verbose:
        cmd.append("--verbose")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            check=True
        )
        return True, result.stdout.strip(), ""
    except subprocess.TimeoutExpired:
        return False, "", "Timeout (>30s)"
    except subprocess.CalledProcessError as e:
        return False, "", f"Error: {e.stderr}"
    except Exception as e:
        return False, "", f"Exception: {str(e)}"


def main():
    """Run all test cases and display results."""
    print("=" * 80)
    print("T5-ONNX Text Correction Test Suite")
    print("=" * 80)
    print()
    
    # Check if model directory exists
    model_dir = "t5-small-onnx-q"
    if not Path(model_dir).exists():
        print(f"ERROR: Model directory not found: {model_dir}")
        print("\nPlease ensure you have:")
        print("1. Exported the model: ./export_model.sh (or .bat on Windows)")
        print("2. Quantized the model: python quantize_t5.py")
        print()
        sys.exit(1)
    
    print(f"Model directory: {model_dir}")
    print(f"Running {len(TEST_CASES)} test cases...")
    print()
    
    results = []
    for i, (input_text, description) in enumerate(TEST_CASES, 1):
        print(f"Test {i}/{len(TEST_CASES)}: {description}")
        print(f"  Input:  {input_text}")
        
        # Run with greedy decoding (fast)
        success, output, error = run_inference(input_text, model_dir, num_beams=1)
        
        if success:
            print(f"  Output: {output}")
            results.append((True, description))
        else:
            print(f"  ERROR: {error}")
            results.append((False, description))
        
        print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    success_count = sum(1 for s, _ in results if s)
    total_count = len(results)
    
    print(f"Tests passed: {success_count}/{total_count}")
    
    if success_count < total_count:
        print("\nFailed tests:")
        for success, desc in results:
            if not success:
                print(f"  - {desc}")
    
    print()
    print("Note: T5-small is a general-purpose model. For optimal French grammar")
    print("correction, consider fine-tuning or using mT5-small (multilingual).")
    print()
    
    # Return exit code
    sys.exit(0 if success_count == total_count else 1)


if __name__ == "__main__":
    main()
