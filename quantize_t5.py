"""
Quantization script for T5-small ONNX models.
This script applies dynamic INT8 quantization to the exported ONNX models.

Usage:
    python quantize_t5.py

Requirements:
    - onnxruntime must be installed
    - Source ONNX models must exist in 'onnx-t5-small/' directory
"""

from onnxruntime.quantization import QuantType, quantize_dynamic
import os
import shutil


def quantize_models(src_dir="onnx-t5-small", dst_dir="t5-small-onnx-q"):
    """
    Quantize T5 ONNX models with dynamic INT8 quantization.
    
    Args:
        src_dir: Source directory containing exported ONNX models
        dst_dir: Destination directory for quantized models
    """
    print(f"Starting quantization process...")
    print(f"Source directory: {src_dir}")
    print(f"Destination directory: {dst_dir}")
    
    # Create destination directory
    os.makedirs(dst_dir, exist_ok=True)
    
    # Model files to quantize
    model_files = [
        "encoder_model.onnx",
        "decoder_model.onnx",
        "decoder_with_past_model.onnx"
    ]
    
    # Quantize each model
    for model_name in model_files:
        src_path = os.path.join(src_dir, model_name)
        dst_path = os.path.join(dst_dir, model_name)
        
        if not os.path.exists(src_path):
            print(f"WARNING: {src_path} not found, skipping...")
            continue
        
        print(f"\nQuantizing {model_name}...")
        try:
            quantize_dynamic(
                model_input=src_path,
                model_output=dst_path,
                per_channel=False,  # Simple and robust
                reduce_range=False,
                weight_type=QuantType.QInt8
            )
            print(f"✓ {model_name} quantized successfully")
        except Exception as e:
            print(f"ERROR quantizing {model_name}: {e}")
            raise
    
    # Copy tokenizer and config files
    print("\nCopying tokenizer and configuration files...")
    config_files = [
        "spiece.model",
        "tokenizer.json",
        "config.json",
        "special_tokens_map.json",
        "generation_config.json",
        "tokenizer_config.json"
    ]
    
    for filename in config_files:
        src_file = os.path.join(src_dir, filename)
        dst_file = os.path.join(dst_dir, filename)
        
        if os.path.exists(src_file):
            shutil.copy(src_file, dst_file)
            print(f"✓ Copied {filename}")
        else:
            print(f"WARNING: {filename} not found in source directory")
    
    print(f"\n✓ Quantization complete!")
    print(f"Quantized models saved to: {dst_dir}/")
    print(f"\nNext steps:")
    print(f"1. Test inference with: python inference_t5_onnx.py --text 'test phrase'")
    print(f"2. Prepare offline wheels with: pip download --dest wheels onnxruntime transformers optimum sentencepiece tokenizers")


if __name__ == "__main__":
    quantize_models()
