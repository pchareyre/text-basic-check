# Quick Build Guide - External Architecture

This guide provides the fastest path to build the Windows executable with **External Model Architecture**.

## Why External Architecture?

✅ **Recommended** for most users:
- Smaller base download (150 MB vs 510 MB)
- Model can be updated independently
- Flexible: users choose to download model separately
- Faster build time

## Prerequisites

**On Windows with Python 3.8+:**

```cmd
# Install all dependencies
pip install -r requirements.txt
pip install -r requirements_api.txt
pip install -r requirements_t5_onnx.txt
pip install -r requirements_exe.txt
```

## Build Steps

### Option 1: One-Command Build (Recommended)

```cmd
build_external.bat
```

That's it! The script will:
1. Check and install PyInstaller if needed
2. Clean previous builds
3. Build the executable
4. Copy T5 model if available
5. Show output location and size

### Option 2: Manual Steps

```cmd
# 1. Export T5 model (if not done yet)
export_model.bat

# 2. Quantize model (if not done yet)
python quantize_t5.py

# 3. Build executable
pyinstaller build_exe_external.spec --clean

# 4. Copy model to distribution (optional)
xcopy /E /I /Y t5-small-onnx-q dist\TextCorrectionApp_External\t5-small-onnx-q
```

## Output

After building, you'll find:

```
dist/TextCorrectionApp_External/
├── TextCorrectionApp.exe      (~50 MB)
├── _internal/                  (~100 MB dependencies)
│   ├── backend/
│   ├── frontend/
│   └── [libraries]
└── t5-small-onnx-q/           (~360 MB - optional)
    ├── encoder_model.onnx
    ├── decoder_model.onnx
    ├── decoder_with_past_model.onnx
    └── [tokenizer files]
```

**Total Size:**
- Without model: ~150 MB (SymSpell only)
- With model: ~510 MB (SymSpell + T5 grammar)

## Testing

```cmd
cd dist\TextCorrectionApp_External
TextCorrectionApp.exe
```

Application will:
1. Start FastAPI backend (localhost:8000)
2. Start Streamlit frontend (localhost:8501)
3. Open browser automatically

## Distribution

### Strategy 1: Base + Optional Model (Recommended)

**Create two separate downloads:**

```cmd
# 1. Create base package (150 MB)
cd dist
powershell Compress-Archive -Path TextCorrectionApp_External\* -DestinationPath TextCorrection_Base.zip -Force

# 2. Create model-only package (360 MB)
cd TextCorrectionApp_External
powershell Compress-Archive -Path t5-small-onnx-q -DestinationPath ..\TextCorrection_T5Model.zip -Force
```

**User Instructions:**
```
1. Download and extract TextCorrection_Base.zip
2. (Optional) Download and extract TextCorrection_T5Model.zip into same directory
3. Run TextCorrectionApp.exe
```

### Strategy 2: Complete Package

```cmd
cd dist
powershell Compress-Archive -Path TextCorrectionApp_External -DestinationPath TextCorrection_Complete.zip -Force
```

Single 510 MB download with everything included.

## Troubleshooting

**"PyInstaller not found"**
```cmd
pip install -r requirements_exe.txt
```

**"T5 model not found" during build**
```cmd
# The exe will still work (SymSpell only)
# To add T5 later:
export_model.bat
python quantize_t5.py
# Then rebuild or manually copy t5-small-onnx-q/ next to the .exe
```

**"Build takes too long"**
- Normal: 3-5 minutes on modern hardware
- PyInstaller analyzes all dependencies
- Subsequent builds are faster (cached)

**"Exe is large"**
- 150 MB is normal for Python + FastAPI + Streamlit + dependencies
- This includes web server, UI framework, and all libraries
- Much smaller than alternatives (Electron apps are 200-300 MB)

## Build Time Estimates

- First build: 5-10 minutes
- Subsequent builds: 2-3 minutes
- Model export: 2-3 minutes (one-time)
- Model quantization: 1-2 minutes (one-time)

## Size Breakdown

| Component | Size | Description |
|-----------|------|-------------|
| TextCorrectionApp.exe | 50 MB | Main executable |
| _internal/ | 100 MB | Python runtime + dependencies |
| t5-small-onnx-q/ (optional) | 360 MB | T5 model for grammar correction |
| **Total without T5** | **150 MB** | SymSpell spell checking only |
| **Total with T5** | **510 MB** | Full correction pipeline |

## Comparison: External vs Embedded

| Feature | External | Embedded |
|---------|----------|----------|
| Base size | 150 MB | 510 MB |
| Model updates | ✅ Easy | ❌ Rebuild required |
| Build time | 3-5 min | 5-10 min |
| Distribution | Flexible | Simple |
| User choice | ✅ Optional T5 | ❌ Always included |
| **Recommended** | ✅ Yes | For simple users |

## Next Steps

1. Build with `build_external.bat`
2. Test the executable
3. Create distribution packages
4. Share with users

For detailed information, see:
- [DEPLOYMENT_WINDOWS.md](DEPLOYMENT_WINDOWS.md) - Complete deployment guide
- [ARCHITECTURE.md](ARCHITECTURE.md) - Project architecture
- [README_API.md](README_API.md) - Web application usage

---

**Last Updated:** January 3, 2026  
**Build Script:** `build_external.bat`  
**Architecture:** External Model (Recommended)
