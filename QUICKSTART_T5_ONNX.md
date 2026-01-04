# Quick Start Guide - T5-ONNX Offline Text Correction

This guide provides the fastest path to get T5-ONNX text correction working.

## For Build Machine (with Internet)

### 1. One-Command Setup
```bash
# Windows
setup_build.bat

# Linux/Mac
chmod +x setup_build.sh && ./setup_build.sh
```

### 2. Or Manual Steps
```bash
# Install dependencies
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
pip install transformers optimum[onnxruntime] onnxruntime sentencepiece tokenizers torch

# Export model
export_model.bat  # Windows
./export_model.sh  # Linux/Mac

# Quantize
python quantize_t5.py

# Download offline packages
download_wheels.bat  # Windows
./download_wheels.sh  # Linux/Mac
```

### 3. Transfer Files
Copy to USB drive or network share:
- `t5-small-onnx-q/` directory
- `wheels/` directory
- `inference_t5_onnx.py`
- `requirements_t5_onnx.txt`
- `README_T5_ONNX.md`

## For Target Machine (Windows, Offline)

### 1. Install
```cmd
python -m venv .venv
.venv\Scripts\activate
pip install --no-index --find-links wheels -r requirements_t5_onnx.txt
```

### 2. Test
```cmd
python inference_t5_onnx.py --text "Corrige: je vais au magazin."
```

### 3. Use
```cmd
# Fast (greedy)
python inference_t5_onnx.py --text "Your text here"

# Better quality (beam search)
python inference_t5_onnx.py --num_beams 4 --text "Your text here"
```

## Troubleshooting

**"Module not found"**: Did you activate the virtual environment?
```cmd
.venv\Scripts\activate
```

**"Model not found"**: Is `t5-small-onnx-q/` in the current directory?
```cmd
dir t5-small-onnx-q
```

**Too slow**: Use greedy decoding and reduce max tokens
```cmd
python inference_t5_onnx.py --num_beams 1 --max_new_tokens 32 --text "..."
```

## Full Documentation

See [README_T5_ONNX.md](README_T5_ONNX.md) for complete documentation, integration examples, and advanced topics.
