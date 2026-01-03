# Text Correction API & Web Interface

Complete web application for text correction using SymSpell and T5-ONNX.

## Overview

This application provides a web interface for correcting text files through a two-stage process:
1. **SymSpell Correction** - Fast spell checking
2. **T5 Grammar Correction** - Advanced grammar and style improvements

## Architecture

- **Backend**: FastAPI REST API (`api.py`)
- **Frontend**: Streamlit web interface (`app.py`)
- **Correction Pipeline**: SymSpell → T5-ONNX

## Installation

### 1. Install Base Dependencies

```bash
# Install core packages
pip install -r requirements.txt
pip install -r requirements_api.txt
```

### 2. Install T5-ONNX Dependencies (Optional but Recommended)

```bash
pip install -r requirements_t5_onnx.txt
```

### 3. Prepare T5 Model (if using T5 correction)

Follow the instructions in `README_T5_ONNX.md`:

```bash
# Export model
./export_model.sh  # or export_model.bat on Windows

# Quantize model
python quantize_t5.py
```

This creates the `t5-small-onnx-q/` directory with quantized models.

## Usage

### Running the Application

#### Option 1: Two Separate Terminals (Recommended for Development)

**Terminal 1 - Start API Server:**
```bash
python api.py
```
The API will be available at http://localhost:8000

**Terminal 2 - Start Streamlit Interface:**
```bash
streamlit run app.py
```
The web interface will open automatically in your browser (usually http://localhost:8501)

#### Option 2: Using the Start Script

**Linux/Mac:**
```bash
chmod +x start_app.sh
./start_app.sh
```

**Windows:**
```cmd
start_app.bat
```

### Using the Web Interface

1. **Open the Streamlit interface** in your browser
2. **Check system status** in the sidebar (API should be running)
3. **Upload a .txt file** containing text with errors
4. **Click "Correct Text"** to process
5. **View results**:
   - Original text
   - Intermediate text (after SymSpell correction)
   - Final text (after T5 grammar correction)
6. **Download corrected versions** using the download buttons

## API Endpoints

### `POST /upload`
Upload a text file for correction.

**Request:**
- Form data with file upload

**Response:**
```json
{
  "file_id": "uuid",
  "original_filename": "text.txt",
  "status": "completed",
  "message": "File processed successfully"
}
```

### `GET /download/{file_id}/intermediate`
Download intermediate corrected file (after SymSpell).

### `GET /download/{file_id}/final`
Download final corrected file (after T5).

### `GET /health`
Check API health status.

### `GET /status/{file_id}`
Get processing status for a file.

## Workflow

```
Upload .txt file
     ↓
SymSpell Spell Checking
     ↓
Save intermediate.txt
     ↓
T5 Grammar Correction
     ↓
Save final.txt
     ↓
Display & Download
```

## Configuration

### API Configuration (api.py)

```python
# T5 model directory
model_dir = "t5-small-onnx-q"

# Server settings
host = "0.0.0.0"
port = 8000
```

### Streamlit Configuration (app.py)

```python
# API endpoint
API_URL = "http://localhost:8000"
```

## File Storage

Processed files are temporarily stored in:
- Linux/Mac: `/tmp/text_correction/{file_id}/`
- Windows: `%TEMP%\text_correction\{file_id}\`

Files include:
- `original.txt` - Original uploaded text
- `intermediate.txt` - After SymSpell correction
- `final.txt` - After T5 grammar correction

## Features

### ✅ Implemented
- File upload (.txt files)
- Two-stage correction pipeline
- Intermediate and final file downloads
- Real-time status checking
- Automatic text display
- Statistics dashboard
- Error handling
- CORS support for API

### 🔄 Pipeline Details

**Stage 1: SymSpell**
- Fast dictionary-based spell checking
- Handles common typos and misspellings
- ~1ms per word
- Language: English (extensible)

**Stage 2: T5-ONNX**
- Neural grammar correction
- Style improvements
- Context-aware corrections
- ~100-400ms per sentence (greedy)
- Offline operation with quantized models

## Error Handling

- **API not running**: Frontend shows error message with instructions
- **Invalid file format**: Only .txt files accepted
- **T5 unavailable**: Falls back to SymSpell-only correction
- **Large files**: Automatic text chunking for T5 processing
- **Encoding errors**: UTF-8 required

## Development

### Running Tests

```bash
# Test spell checker
python -m pytest tests/

# Test API endpoints
python -m pytest tests/test_api.py  # (create test file)

# Test T5 inference
python test_inference_t5.py
```

### API Documentation

FastAPI provides automatic interactive documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Troubleshooting

### "API is not available"
- Ensure the API server is running: `python api.py`
- Check if port 8000 is available
- Verify API_URL in app.py matches your setup

### "T5 model not found"
- Run model export: `./export_model.sh`
- Run quantization: `python quantize_t5.py`
- Verify `t5-small-onnx-q/` directory exists

### "ModuleNotFoundError"
- Install all dependencies:
  ```bash
  pip install -r requirements.txt
  pip install -r requirements_api.txt
  pip install -r requirements_t5_onnx.txt
  ```

### Slow T5 Processing
- Use greedy decoding (default, faster)
- Process shorter text chunks
- Ensure CPU has AVX2 support
- Consider using only SymSpell for real-time applications

## Production Deployment

### Using Docker (Recommended)

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements*.txt ./
RUN pip install -r requirements.txt -r requirements_api.txt -r requirements_t5_onnx.txt

COPY . .

EXPOSE 8000 8501

CMD ["sh", "-c", "python api.py & streamlit run app.py --server.address=0.0.0.0"]
```

### Using Gunicorn (Production API)

```bash
pip install gunicorn
gunicorn api:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Environment Variables

```bash
export API_HOST=0.0.0.0
export API_PORT=8000
export MODEL_DIR=t5-small-onnx-q
```

## Security Considerations

- ⚠️ File uploads are stored temporarily - implement cleanup
- ⚠️ No authentication - add authentication for production
- ⚠️ CORS is open - restrict origins in production
- ⚠️ File size limits - implement upload size restrictions
- ✅ UTF-8 validation
- ✅ File type validation

## Performance

### Expected Performance
- SymSpell: ~1ms per word
- T5 (greedy): 100-400ms per sentence
- T5 (beam=4): 400-1200ms per sentence
- Total pipeline: ~500ms-2s for typical text

### Memory Usage
- API: ~200-500 MB
- With T5 loaded: +500 MB-1 GB
- Per request: +50-100 MB

## License

MIT License - Same as the main project

## Support

For issues or questions:
1. Check troubleshooting section
2. Review API documentation at /docs
3. See main README.md and README_T5_ONNX.md

---

**Last Updated**: January 3, 2026  
**Version**: 1.0
