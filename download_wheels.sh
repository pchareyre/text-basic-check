#!/bin/bash
# Download Python wheels for offline installation on Windows x64
# Run this script on a machine with internet access

echo "======================================"
echo "Downloading wheels for offline install"
echo "======================================"
echo ""

# Create wheels directory
mkdir -p wheels
echo "Created wheels directory"

# Download packages for Windows x64
echo "Downloading packages..."
pip download --dest wheels --platform win_amd64 --only-binary=:all: onnxruntime transformers optimum sentencepiece tokenizers

# Also download source distributions for pure Python packages
pip download --dest wheels transformers optimum

echo ""
echo "✓ Download complete!"
echo ""
echo "Wheels saved to: ./wheels/"
echo "Files to transfer to offline machine:"
echo "  1. wheels/ directory"
echo "  2. requirements_t5_onnx.txt"
echo "  3. t5-small-onnx-q/ directory (quantized models)"
echo "  4. inference_t5_onnx.py"
echo ""
echo "On the offline machine, run:"
echo "  python -m venv .venv"
echo "  .venv\\Scripts\\activate"
echo "  pip install --no-index --find-links wheels -r requirements_t5_onnx.txt"
