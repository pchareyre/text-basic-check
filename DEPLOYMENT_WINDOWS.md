# Windows Executable Deployment Guide

Complete guide for creating standalone Windows executables for the Text Correction application.

## Table of Contents

1. [Overview](#overview)
2. [Architecture Comparison](#architecture-comparison)
3. [Prerequisites](#prerequisites)
4. [Building Process](#building-process)
5. [Architecture Details](#architecture-details)
6. [Testing](#testing)
7. [Distribution](#distribution)
8. [Troubleshooting](#troubleshooting)

## Overview

This guide explains how to package the Text Correction application as a standalone Windows executable (.exe) that can be distributed to users without requiring Python installation.

### Key Features
- ✅ No Python installation required on target machine
- ✅ Single-click launch
- ✅ Self-contained application
- ✅ Two architecture options (Embedded vs External model)
- ✅ Automatic browser opening

## Architecture Comparison

### Architecture 1: Embedded Model (Recommended for Simple Distribution)

**Structure:**
```
TextCorrectionApp_Embedded/
├── TextCorrectionApp.exe    (~50 MB)
├── _internal/                (Dependencies + Model ~400 MB)
│   ├── backend/
│   ├── frontend/
│   ├── text_basic_check/
│   ├── t5-small-onnx-q/      ← Model EMBEDDED
│   └── [DLLs and libraries]
└── [Other files]
```

**Pros:**
- ✅ Single directory to distribute
- ✅ No external model dependency
- ✅ User-friendly (everything in one place)
- ✅ No configuration needed

**Cons:**
- ❌ Large size (~450-500 MB total)
- ❌ Cannot update model separately
- ❌ Longer build time
- ❌ Larger download for users

**Best for:**
- End users who want simple installation
- One-time distribution
- Users who don't need model updates

**Estimated Sizes:**
- Executable: ~50 MB
- Dependencies: ~100 MB
- T5 Model: ~360 MB
- **Total: ~510 MB**

---

### Architecture 2: External Model (Recommended for Developers/Power Users)

**Structure:**
```
TextCorrectionApp_External/
├── TextCorrectionApp.exe    (~50 MB)
├── _internal/                (Dependencies ~100 MB)
│   ├── backend/
│   ├── frontend/
│   ├── text_basic_check/
│   └── [DLLs and libraries]
└── t5-small-onnx-q/          ← Model EXTERNAL (~360 MB)
    ├── encoder_model.onnx
    ├── decoder_model.onnx
    ├── decoder_with_past_model.onnx
    └── [tokenizer files]
```

**Pros:**
- ✅ Smaller base executable (~150 MB without model)
- ✅ Model can be updated independently
- ✅ Faster build time
- ✅ Optional T5 (can run without it)
- ✅ Easier to debug model issues

**Cons:**
- ❌ Requires model directory alongside exe
- ❌ Users must maintain directory structure
- ❌ Slightly more complex distribution

**Best for:**
- Power users who may want to update models
- Development and testing
- Users who may want SymSpell-only mode
- Situations where download size matters

**Estimated Sizes:**
- Executable + Dependencies: ~150 MB
- T5 Model (optional): ~360 MB
- **Total with T5: ~510 MB**
- **Total without T5: ~150 MB**

---

### Recommendation Matrix

| Use Case | Recommended Architecture | Reason |
|----------|-------------------------|---------|
| **General users** | Embedded | Simplest installation |
| **Corporate deployment** | Embedded | Easier IT deployment |
| **Frequent model updates** | External | Model can be swapped |
| **Limited bandwidth** | External (no model) | Download only 150 MB |
| **SymSpell-only usage** | External (no model) | Don't need T5 |
| **Development/Testing** | External | Faster iteration |

**Overall Best Practice:** 
- **Use EXTERNAL for distribution** - Users get flexibility
- Provide model as separate download
- 150 MB base + 360 MB optional model = Better UX

## Prerequisites

### On Build Machine (Windows with Python)

1. **Python 3.8+** installed
2. **All dependencies installed:**
```bash
pip install -r requirements.txt
pip install -r requirements_api.txt
pip install -r requirements_t5_onnx.txt
pip install -r requirements_exe.txt
```

3. **T5 Model prepared** (for embedded or external):
```bash
# Export model
export_model.bat

# Quantize model
python quantize_t5.py
```

4. **Verify directory structure:**
```
text-basic-check/
├── backend/
├── frontend/
├── text_basic_check/
├── t5-small-onnx-q/     ← Must exist for embedded build
├── launcher.py
├── build_embedded.bat
├── build_external.bat
├── build_exe_embedded.spec
└── build_exe_external.spec
```

## Building Process

### Option 1: Build with Embedded Model

```cmd
# Run the build script
build_embedded.bat
```

**What happens:**
1. Checks PyInstaller installation
2. Checks if T5 model exists
3. Cleans previous builds
4. Runs PyInstaller with embedded spec
5. Creates `dist/TextCorrectionApp_Embedded/`
6. Includes model inside distribution
7. Shows size and instructions

**Build time:** ~5-10 minutes (depending on hardware)

### Option 2: Build with External Model

```cmd
# Run the build script
build_external.bat
```

**What happens:**
1. Checks PyInstaller installation
2. Cleans previous builds
3. Runs PyInstaller with external spec
4. Creates `dist/TextCorrectionApp_External/`
5. Copies T5 model if it exists
6. Shows size and instructions

**Build time:** ~3-5 minutes (faster without embedding model)

### Manual Build (Advanced)

```cmd
# Install PyInstaller if needed
pip install pyinstaller

# Build embedded version
pyinstaller build_exe_embedded.spec --clean

# OR build external version
pyinstaller build_exe_external.spec --clean

# For external, copy model manually if needed
xcopy /E /I /Y t5-small-onnx-q dist\TextCorrectionApp_External\t5-small-onnx-q
```

## Architecture Details

### PyInstaller Specification Files

Both `.spec` files control the build process:

**Common Elements:**
- Entry point: `launcher.py`
- Hidden imports: All backend/frontend modules
- Excluded modules: matplotlib, scipy, pandas (reduce size)
- UPX compression: Enabled (reduces size)
- Console: Enabled (for debugging)

**Differences:**

| Feature | Embedded Spec | External Spec |
|---------|--------------|---------------|
| T5 Model | Included in datas | Not included |
| Distribution size | ~510 MB | ~150-510 MB |
| Model updates | Requires rebuild | Just replace directory |
| Output directory | `TextCorrectionApp_Embedded/` | `TextCorrectionApp_External/` |

### Launcher Script

The `launcher.py` script:
1. Detects if running as executable or script
2. Sets up Python path correctly
3. Configures model directory
4. Starts backend in separate process
5. Starts frontend in main process
6. Opens browser automatically
7. Handles shutdown gracefully

**Model Detection:**
```python
# For embedded: looks in _MEIPASS
# For external: looks next to .exe
model_dir = exe_dir / 't5-small-onnx-q'
```

## Testing

### Test on Build Machine

```cmd
# Navigate to output directory
cd dist\TextCorrectionApp_Embedded
# or
cd dist\TextCorrectionApp_External

# Run executable
TextCorrectionApp.exe
```

**Expected behavior:**
1. Console window opens
2. Shows "Starting FastAPI backend..."
3. Shows "Starting Streamlit frontend..."
4. Browser opens to http://localhost:8501
5. Application UI loads

### Test Checklist

- [ ] Executable launches without errors
- [ ] Backend starts on port 8000
- [ ] Frontend opens in browser
- [ ] Can upload .txt file
- [ ] SymSpell correction works
- [ ] T5 correction works (if model included)
- [ ] Can download intermediate file
- [ ] Can download final file
- [ ] Feature flag toggle works
- [ ] Application closes cleanly

### Test Without Python

To truly test standalone operation:
1. Copy dist folder to a machine without Python
2. Or temporarily rename Python installation
3. Run executable and verify all features work

### Size Verification

```cmd
# Check total size
dir dist\TextCorrectionApp_Embedded /s

# Expected sizes:
# Embedded: ~510 MB total
# External: ~150 MB base, +360 MB if model included
```

## Distribution

### Packaging for Distribution

**Embedded Architecture:**
```cmd
# Option 1: ZIP archive
cd dist
tar -a -c -f TextCorrectionApp_Embedded.zip TextCorrectionApp_Embedded

# Option 2: Create installer (using NSIS, Inno Setup, etc.)
```

**External Architecture:**
```cmd
# Option 1: ZIP base application
cd dist
tar -a -c -f TextCorrectionApp_Base.zip TextCorrectionApp_External

# Option 2: Separate model ZIP (optional download)
tar -a -c -f T5_Model.zip TextCorrectionApp_External\t5-small-onnx-q

# Option 3: Complete package
tar -a -c -f TextCorrectionApp_Complete.zip TextCorrectionApp_External
```

### Distribution Strategies

**Strategy 1: Single Package (Embedded)**
- Pros: One download, simple for users
- Cons: Large file (~510 MB)
- Use case: Corporate deployment, simple distribution

**Strategy 2: Split Downloads (External)**
- Base application: ~150 MB (required)
- T5 Model: ~360 MB (optional)
- Pros: Users choose what to download
- Cons: Requires instructions
- Use case: Flexible deployment, bandwidth-conscious

**Strategy 3: Installer**
- Create an installer using tools like:
  - Inno Setup (free)
  - NSIS (free)
  - Advanced Installer (commercial)
- Pros: Professional appearance, registry entries, start menu shortcuts
- Cons: Additional complexity

### User Instructions

**For Embedded:**
```
Text Correction Application - Installation Instructions

1. Extract TextCorrectionApp_Embedded.zip
2. Navigate to TextCorrectionApp_Embedded folder
3. Double-click TextCorrectionApp.exe
4. Application will start automatically in your browser
5. Upload .txt files to correct text

Requirements:
- Windows 7 or later (x64)
- 1 GB free RAM
- Internet NOT required

Size: ~510 MB
```

**For External:**
```
Text Correction Application - Installation Instructions

1. Extract TextCorrectionApp_External.zip
2. (Optional) Extract T5_Model.zip into same directory
3. Your folder should contain:
   - TextCorrectionApp.exe
   - _internal/ directory
   - t5-small-onnx-q/ directory (optional, for grammar correction)
4. Double-click TextCorrectionApp.exe
5. Application will start automatically in your browser

Requirements:
- Windows 7 or later (x64)
- 1 GB free RAM
- Internet NOT required

Size: 
- Base (SymSpell only): ~150 MB
- With T5 grammar correction: ~510 MB
```

## Troubleshooting

### Build Issues

**"PyInstaller not found"**
```cmd
pip install -r requirements_exe.txt
```

**"Module not found during build"**
- Check hiddenimports in .spec file
- Add missing module to hiddenimports list

**"Build succeeds but exe doesn't run"**
- Test with `--console` flag (already enabled)
- Check for missing DLLs
- Verify all data files are included

**"Model not found" during build**
```cmd
# Make sure model exists
dir t5-small-onnx-q

# If not, create it:
export_model.bat
python quantize_t5.py
```

### Runtime Issues

**"Application won't start"**
- Check if ports 8000 and 8501 are available
- Run as Administrator if needed
- Check antivirus isn't blocking

**"T5 correction not working"**
- External: Check if t5-small-onnx-q/ exists next to .exe
- Embedded: Model should be automatic
- Check console output for error messages

**"Browser doesn't open"**
- Manually navigate to http://localhost:8501
- Check if streamlit started (see console)

**"High memory usage"**
- Normal: T5 model uses ~500 MB - 1 GB
- Close other applications if needed

### File Size Issues

**"Executable too large"**
- Use External architecture
- Distribute model separately
- Enable UPX compression (already enabled)
- Exclude unnecessary modules

**"Want to reduce size further"**
- Remove T5 completely (SymSpell only): ~100 MB
- Use lighter model (future enhancement)
- Compress with 7zip: ~30% reduction

## Advanced Topics

### Creating Desktop Shortcut

Users can create a shortcut:
1. Right-click TextCorrectionApp.exe
2. Send to → Desktop (create shortcut)
3. Rename to "Text Correction Tool"

### Adding Custom Icon

Place `icon.ico` in project root before building:
```
text-basic-check/
├── icon.ico          ← Add this
├── launcher.py
└── build_*.spec
```

The .spec files will automatically use it.

### Environment Variables

Users can configure via environment variables:
```cmd
set APP_API_PORT=9000
set FRONTEND_API_URL=http://localhost:9000
TextCorrectionApp.exe
```

### Creating Windows Installer

Using Inno Setup (example):
```inno
[Setup]
AppName=Text Correction Tool
AppVersion=1.0
DefaultDirName={pf}\TextCorrectionTool
OutputBaseFilename=TextCorrectionSetup

[Files]
Source: "dist\TextCorrectionApp_External\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{commondesktop}\Text Correction Tool"; Filename: "{app}\TextCorrectionApp.exe"
```

## Performance Comparison

| Metric | Embedded | External | Notes |
|--------|----------|----------|-------|
| **Build time** | 5-10 min | 3-5 min | External faster |
| **Distribution size** | 510 MB | 150-510 MB | External flexible |
| **Startup time** | ~8 sec | ~8 sec | Same |
| **First run disk I/O** | High | High | Same |
| **Model update** | Rebuild | Replace dir | External easier |
| **User complexity** | Low | Medium | Embedded simpler |

## Conclusion

### Recommended Approach

**For most use cases:** **External Architecture**

Reasons:
1. Smaller base download (150 MB vs 510 MB)
2. Users can choose to download model separately
3. Model can be updated without reinstalling
4. Faster development iteration
5. Better for testing

**Provide:**
- `TextCorrectionApp_Base.zip` (150 MB) - Always
- `T5_Model.zip` (360 MB) - Optional download
- Clear instructions on directory structure

### Distribution Checklist

- [ ] Build chosen architecture
- [ ] Test on clean Windows machine
- [ ] Verify all features work
- [ ] Check file sizes
- [ ] Create ZIP archives
- [ ] Write user instructions
- [ ] Test instructions with new user
- [ ] Host files for download
- [ ] Provide checksums (optional)
- [ ] Include README.txt in ZIP

---

**Last Updated:** January 3, 2026  
**Version:** 1.0  
**Contact:** See main README.md for support
