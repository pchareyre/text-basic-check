# T5-small ONNX Offline Text Correction

Complete guide for deploying T5-small ONNX quantized text correction on Windows without internet access.

## Table of Contents

1. [Overview](#overview)
2. [System Requirements](#system-requirements)
3. [Build Phase (Machine with Internet)](#build-phase-machine-with-internet)
4. [Offline Deployment (Target Machine)](#offline-deployment-target-machine)
5. [Usage Examples](#usage-examples)
6. [Performance Considerations](#performance-considerations)
7. [Windows Integration](#windows-integration)
8. [Troubleshooting](#troubleshooting)

## Overview

This solution provides offline grammar, syntax, and style correction using:
- **T5-small** model exported to ONNX format
- **INT8 dynamic quantization** for faster CPU inference
- **No internet required** on the target machine
- **Windows-compatible** Python inference script

### Key Features
- ✅ Fully offline operation (no API calls)
- ✅ CPU-optimized with INT8 quantization
- ✅ Greedy and beam search decoding
- ✅ ~100-400ms latency per short sentence (greedy)
- ✅ Memory footprint: ~300-500 MB

## System Requirements

### Build Machine (with Internet)
- Python 3.8 or higher
- pip with internet access
- ~2 GB free disk space

### Target Machine (Windows, offline)
- Windows 7 or higher (x64)
- Python 3.8 or higher
- Microsoft Visual C++ Runtime (usually pre-installed)
- ~1 GB free disk space
- ~1 GB RAM for operation

## Build Phase (Machine with Internet)

Execute these steps once on a machine with internet access, then transfer the artifacts to the offline machine.

### Step 1: Setup Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install required packages
pip install transformers optimum[onnxruntime] onnxruntime sentencepiece tokenizers torch
```

### Step 2: Export T5-small to ONNX

**Option A: Using the provided script (recommended)**

Windows:
```cmd
export_model.bat
```

Linux/Mac:
```bash
chmod +x export_model.sh
./export_model.sh
```

**Option B: Manual export**

```bash
optimum-cli export onnx \
    --model t5-small \
    --task text2text-generation \
    --output onnx-t5-small
```

**Expected output:**
```
onnx-t5-small/
├── encoder_model.onnx
├── decoder_model.onnx
├── decoder_with_past_model.onnx
├── config.json
├── generation_config.json
├── spiece.model
├── special_tokens_map.json
├── tokenizer.json
└── tokenizer_config.json
```

### Step 3: Quantize Models (INT8)

Run the quantization script:

```bash
python quantize_t5.py
```

This creates the `t5-small-onnx-q/` directory with quantized models:
- Smaller file sizes (~50% reduction)
- Faster inference on CPU
- Minimal quality loss

**Expected output:**
```
t5-small-onnx-q/
├── encoder_model.onnx (quantized)
├── decoder_model.onnx (quantized)
├── decoder_with_past_model.onnx (quantized)
├── config.json
├── generation_config.json
├── spiece.model
├── special_tokens_map.json
├── tokenizer.json
└── tokenizer_config.json
```

### Step 4: Download Offline Packages

**Option A: Using the provided script (recommended)**

Windows:
```cmd
download_wheels.bat
```

Linux/Mac:
```bash
chmod +x download_wheels.sh
./download_wheels.sh
```

**Option B: Manual download**

```bash
mkdir wheels
pip download --dest wheels --platform win_amd64 --only-binary=:all: \
    onnxruntime transformers optimum sentencepiece tokenizers
pip download --dest wheels transformers optimum
```

### Step 5: Prepare Transfer Package

Create a transfer package with these files/directories:

```
transfer-package/
├── t5-small-onnx-q/          # Quantized models (from Step 3)
├── wheels/                    # Python packages (from Step 4)
├── inference_t5_onnx.py       # Inference script
├── requirements_t5_onnx.txt   # Requirements file
├── test_inference_t5.py       # Test script (optional)
└── README_T5_ONNX.md          # This file
```

Transfer this package to the target Windows machine via USB drive, network share, or other means.

## Offline Deployment (Target Machine)

These steps are executed on the Windows machine without internet access.

### Step 1: Setup Python Environment

```cmd
# Create virtual environment
python -m venv .venv

# Activate
.venv\Scripts\activate

# Verify no internet access is used
set PIP_NO_INDEX=1
```

### Step 2: Install Packages Offline

```cmd
pip install --no-index --find-links wheels -r requirements_t5_onnx.txt
```

This installs all required packages from the local `wheels/` directory.

### Step 3: Verify Installation

```cmd
python inference_t5_onnx.py --help
```

You should see the help message without errors.

### Step 4: Test Inference

```cmd
# Simple test
python inference_t5_onnx.py --text "Corrige: je vais au magazin."

# Run test suite
python test_inference_t5.py
```

## Usage Examples

### Basic Usage (Greedy Decoding - Fastest)

```cmd
python inference_t5_onnx.py --text "Corrige la syntaxe: je vais au magazin pour achetter du pain."
```

**Output:** Corrected text

### Beam Search (Better Quality)

```cmd
python inference_t5_onnx.py --num_beams 4 --text "Corrige la syntaxe: les clients ont été livrés hier, mais le rapport manquent."
```

### Custom Parameters

```cmd
python inference_t5_onnx.py ^
    --model_dir t5-small-onnx-q ^
    --max_new_tokens 128 ^
    --num_beams 2 ^
    --verbose ^
    --text "Your text here"
```

### Command-line Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--model_dir` | `t5-small-onnx-q` | Path to quantized model directory |
| `--text` | (required) | Input text to correct |
| `--max_new_tokens` | `64` | Maximum tokens to generate (32-128 recommended) |
| `--num_beams` | `1` | Beam search width (1=greedy, 4+=better quality) |
| `--verbose` | `False` | Print timing and diagnostic info |

## Performance Considerations

### Latency Benchmarks (CPU)

On modern CPU with AVX2 support:

| Configuration | Latency (per sentence) |
|--------------|------------------------|
| Greedy (num_beams=1) | 100-400 ms |
| Beam=2 | 200-600 ms |
| Beam=4 | 400-1200 ms |

### Optimization Tips

1. **Use Greedy for Real-time**: `num_beams=1` provides fastest inference
2. **Limit Token Generation**: Keep `max_new_tokens` between 32-64 for short sentences
3. **Sentence Segmentation**: Split long paragraphs at punctuation marks
4. **Avoid Repetitions**: `no_repeat_ngram_size=3` (default in script)
5. **Batch Processing**: Process multiple sentences in sequence (model stays loaded)

### Memory Usage

- **Model files**: ~300-500 MB on disk
- **Runtime RAM**: ~500 MB - 1 GB during inference
- **Peak memory**: Increases with longer inputs and higher beam width

## Windows Integration

### Integration Pattern

The Python script can be called from any Windows application using subprocess:

**C# Example:**
```csharp
using System.Diagnostics;

string pythonPath = @".venv\Scripts\python.exe";
string scriptPath = @"inference_t5_onnx.py";
string inputText = "Corrige: je vais au magazin.";

var process = new Process
{
    StartInfo = new ProcessStartInfo
    {
        FileName = pythonPath,
        Arguments = $"{scriptPath} --text \"{inputText}\"",
        RedirectStandardOutput = true,
        RedirectStandardError = true,
        UseShellExecute = false,
        CreateNoWindow = true
    }
};

process.Start();
string output = process.StandardOutput.ReadToEnd();
process.WaitForExit();
```

**PowerShell Example:**
```powershell
$pythonPath = ".venv\Scripts\python.exe"
$text = "Corrige: je vais au magazin."
$result = & $pythonPath inference_t5_onnx.py --text $text
Write-Host $result
```

### Input/Output Contracts

**Input (UTF-8):**
- Plain text via `--text` argument
- Or read from stdin/file if you modify the script

**Output:**
- Corrected text printed to stdout
- Errors printed to stderr

### Error Handling & Robustness

1. **Timeout**: Set process timeout (5-10 seconds recommended)
2. **Logging**: Redirect stderr to log file for debugging
3. **Fallback**: On beam search timeout, retry with greedy decoding
4. **Retry Logic**: Implement retry with exponential backoff for transient errors

### Example Wrapper Script

Create `correct_text.bat`:

```cmd
@echo off
REM Simple wrapper for text correction
.venv\Scripts\python.exe inference_t5_onnx.py --text %*
```

Usage:
```cmd
correct_text.bat "Corrige: je vais au magazin."
```

## Troubleshooting

### Issue: "Module not found" errors

**Solution:**
- Ensure virtual environment is activated: `.venv\Scripts\activate`
- Reinstall packages: `pip install --no-index --find-links wheels -r requirements_t5_onnx.txt`

### Issue: "Model directory not found"

**Solution:**
- Verify `t5-small-onnx-q/` directory exists in the working directory
- Check that directory contains all required .onnx and tokenizer files
- Use `--model_dir` to specify full path

### Issue: Slow inference (>2 seconds per sentence)

**Solution:**
- Use greedy decoding: `--num_beams 1`
- Reduce max tokens: `--max_new_tokens 32`
- Check CPU utilization (should be near 100% during inference)
- Ensure no antivirus scanning the model files during inference

### Issue: Poor correction quality

**Solution:**
- Use beam search: `--num_beams 4`
- T5-small is a general model; for French-specific corrections, consider fine-tuning
- For grammar focus, use mT5-small (multilingual T5)
- Prepend clear instructions: "Corrige la grammaire:" or "Améliore le style:"

### Issue: Memory errors

**Solution:**
- Close other applications
- Reduce `max_new_tokens`
- Use greedy decoding (lower beam width)
- Ensure system has at least 2 GB available RAM

### Issue: Antivirus blocking

**Solution:**
- Add exception for the model directory in antivirus settings
- Add exception for Python executable
- Disable real-time scanning for the working directory

## Advanced Topics

### Fine-tuning for French

For better French grammar correction:

1. Collect French grammar correction pairs
2. Fine-tune mT5-small (multilingual) on your dataset
3. Export and quantize the fine-tuned model (same process)
4. Replace `t5-small-onnx-q/` with your fine-tuned model

### Using mT5-small (Multilingual)

Replace `t5-small` with `google/mt5-small` in the export command:

```bash
optimum-cli export onnx \
    --model google/mt5-small \
    --task text2text-generation \
    --output onnx-mt5-small
```

Then quantize as usual.

### Combining with Other Tools

- **Pre-processing**: Use LanguageTool or Word spell-check first
- **Post-processing**: Apply T5 for style improvements
- **Hybrid**: Basic spell-check → T5 correction → rule-based validation

### Monitoring & Logging

Modify `inference_t5_onnx.py` to log:
- Input text
- Output text
- Timestamp
- Processing time
- User feedback (for model improvement)

### C# Native Alternative (Advanced)

For environments without Python:
- Use Microsoft.ML.OnnxRuntime NuGet package
- Implement SentencePiece tokenizer in C# (complex)
- Load and run ONNX models directly

**Recommendation**: Keep Python script for tokenization simplicity.

## Support & Resources

### Documentation
- Optimum documentation: https://huggingface.co/docs/optimum
- ONNX Runtime: https://onnxruntime.ai/docs/
- Transformers: https://huggingface.co/docs/transformers

### Model Information
- T5-small: https://huggingface.co/t5-small
- mT5-small: https://huggingface.co/google/mt5-small

## Checklist for Deployment

Before deploying to production:

- [ ] Models exported and quantized successfully
- [ ] Wheels downloaded for offline installation
- [ ] Test inference works on build machine
- [ ] Transfer package prepared
- [ ] Offline installation tested on target machine
- [ ] Performance benchmarks meet requirements
- [ ] Error handling implemented in integration code
- [ ] Logging configured
- [ ] Antivirus exceptions configured
- [ ] User documentation provided
- [ ] Fallback strategy defined for failures

## License

The scripts and documentation in this project are MIT licensed.

**Note**: The T5 model is licensed by Google under Apache 2.0. Ensure compliance with model licenses for your use case.

---

**Last Updated**: January 2026
**Version**: 1.0
