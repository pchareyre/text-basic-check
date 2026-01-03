#!/bin/bash
# Export T5-small model to ONNX format
# This script must be run on a machine with internet access

echo "======================================"
echo "Exporting T5-small to ONNX format"
echo "======================================"
echo ""

# Check if optimum-cli is installed
if ! command -v optimum-cli &> /dev/null
then
    echo "ERROR: optimum-cli not found"
    echo "Please install: pip install optimum[onnxruntime]"
    exit 1
fi

# Export T5-small to ONNX
echo "Exporting T5-small model..."
echo "This will download the model from Hugging Face (requires internet)"
echo ""

optimum-cli export onnx \
    --model t5-small \
    --task text2text-generation \
    --output onnx-t5-small

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Export successful!"
    echo ""
    echo "Output directory: onnx-t5-small/"
    echo "Files created:"
    echo "  - encoder_model.onnx"
    echo "  - decoder_model.onnx"
    echo "  - decoder_with_past_model.onnx"
    echo "  - tokenizer files (spiece.model, config.json, etc.)"
    echo ""
    echo "Next step: Quantify the models"
    echo "  python quantize_t5.py"
else
    echo ""
    echo "ERROR: Export failed"
    exit 1
fi
