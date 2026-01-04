"""
Offline T5-small ONNX inference script for text correction.
This script performs grammar/syntax/style correction using a quantized T5-small model.

Usage:
    # Greedy decoding (fastest)
    python inference_t5_onnx.py --text "Corrige la syntaxe: je vais au magazin pour achetter du pain."
    
    # Beam search (better quality, slower)
    python inference_t5_onnx.py --model_dir t5-small-onnx-q --num_beams 4 --text "Corrige la syntaxe: les clients ont été livrés hier, mais le rapport manquent."
    
    # With custom parameters
    python inference_t5_onnx.py --max_new_tokens 128 --num_beams 2 --text "Your text here"

Requirements:
    - onnxruntime (CPU version)
    - transformers
    - optimum[onnxruntime]
    - sentencepiece
    - tokenizers
"""

import argparse
import sys
import time
from pathlib import Path

try:
    from transformers import AutoTokenizer
    from optimum.onnxruntime import ORTModelForSeq2SeqLM
except ImportError as e:
    print(f"ERROR: Missing required dependencies: {e}")
    print("Please install required packages:")
    print("  pip install transformers optimum[onnxruntime] onnxruntime sentencepiece tokenizers")
    sys.exit(1)


def load_model(model_dir: Path):
    """
    Load the quantized T5 ONNX model and tokenizer.
    
    Args:
        model_dir: Path to the directory containing the quantized ONNX models
        
    Returns:
        Tuple of (tokenizer, model)
    """
    print(f"Loading model from: {model_dir}")
    
    try:
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            model_dir,
            use_fast=True,
            local_files_only=True  # Ensure offline mode
        )
        print("✓ Tokenizer loaded")
        
        # Load ONNX model
        model = ORTModelForSeq2SeqLM.from_pretrained(
            model_dir,
            file_name="encoder_model.onnx",
            decoder_file_name="decoder_model.onnx",
            decoder_with_past_file_name="decoder_with_past_model.onnx",
            local_files_only=True  # Ensure offline mode
        )
        print("✓ ONNX model loaded")
        
        return tokenizer, model
    
    except Exception as e:
        print(f"ERROR loading model: {e}")
        print(f"\nMake sure the model directory '{model_dir}' exists and contains:")
        print("  - encoder_model.onnx")
        print("  - decoder_model.onnx")
        print("  - decoder_with_past_model.onnx")
        print("  - tokenizer files (config.json, tokenizer.json, etc.)")
        sys.exit(1)


def generate_text(tokenizer, model, text, max_new_tokens=64, num_beams=1, verbose=False):
    """
    Generate corrected text using the T5 model.
    
    Args:
        tokenizer: The tokenizer instance
        model: The ONNX model instance
        text: Input text to correct
        max_new_tokens: Maximum number of new tokens to generate
        num_beams: Number of beams for beam search (1 = greedy decoding)
        verbose: Whether to print timing information
        
    Returns:
        Corrected text string
    """
    start_time = time.time()
    
    # Tokenize input
    inputs = tokenizer(text, return_tensors="pt")
    
    if verbose:
        tokenize_time = time.time() - start_time
        print(f"Tokenization time: {tokenize_time*1000:.2f}ms")
        gen_start = time.time()
    
    # Generate output
    # Greedy decoding (num_beams=1) or beam search (num_beams>1)
    outputs = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        num_beams=num_beams,
        no_repeat_ngram_size=3,  # Avoid repetitions
        early_stopping=True
    )
    
    if verbose:
        gen_time = time.time() - gen_start
        print(f"Generation time: {gen_time*1000:.2f}ms")
        decode_start = time.time()
    
    # Decode output
    result = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    if verbose:
        decode_time = time.time() - decode_start
        total_time = time.time() - start_time
        print(f"Decoding time: {decode_time*1000:.2f}ms")
        print(f"Total time: {total_time*1000:.2f}ms")
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Offline T5-small ONNX text correction",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simple correction (greedy)
  python inference_t5_onnx.py --text "Corrige: je vais au magazin."
  
  # With beam search for better quality
  python inference_t5_onnx.py --num_beams 4 --text "Corrige: le rapport manquent."
  
  # Custom model directory
  python inference_t5_onnx.py --model_dir ./my-model --text "Your text"
        """
    )
    
    parser.add_argument(
        "--model_dir",
        type=str,
        default="t5-small-onnx-q",
        help="Path to the quantized ONNX model directory (default: t5-small-onnx-q)"
    )
    
    parser.add_argument(
        "--text",
        type=str,
        required=True,
        help="Input text to correct"
    )
    
    parser.add_argument(
        "--max_new_tokens",
        type=int,
        default=64,
        help="Maximum number of new tokens to generate (default: 64)"
    )
    
    parser.add_argument(
        "--num_beams",
        type=int,
        default=1,
        help="Number of beams for beam search. 1=greedy (fastest), 4+=better quality (default: 1)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print timing and diagnostic information"
    )
    
    args = parser.parse_args()
    
    # Validate model directory
    model_path = Path(args.model_dir)
    if not model_path.exists():
        print(f"ERROR: Model directory not found: {model_path}")
        print("\nPlease ensure you have:")
        print("1. Exported the model: optimum-cli export onnx --model t5-small --task text2text-generation --output onnx-t5-small")
        print("2. Quantized the model: python quantize_t5.py")
        sys.exit(1)
    
    # Load model
    tokenizer, model = load_model(model_path)
    
    if args.verbose:
        print(f"\nInput text: {args.text}")
        print(f"Parameters: max_new_tokens={args.max_new_tokens}, num_beams={args.num_beams}")
        print()
    
    # Generate corrected text
    corrected = generate_text(
        tokenizer,
        model,
        args.text,
        max_new_tokens=args.max_new_tokens,
        num_beams=args.num_beams,
        verbose=args.verbose
    )
    
    # Output result
    print(corrected)


if __name__ == "__main__":
    main()
