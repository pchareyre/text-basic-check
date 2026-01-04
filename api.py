"""
FastAPI backend for text correction service.

This API provides endpoints for:
- Uploading text files
- Running spell checking (SymSpell)
- Running grammar correction (T5-ONNX)
- Downloading intermediate and final corrected texts
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import tempfile
import shutil
import uuid
from typing import Dict, Optional
from datetime import datetime

# Import local spell checker
from text_basic_check import SpellChecker

# Try to import T5 inference modules
try:
    from transformers import AutoTokenizer
    from optimum.onnxruntime import ORTModelForSeq2SeqLM
    T5_AVAILABLE = True
except ImportError:
    T5_AVAILABLE = False

app = FastAPI(
    title="Text Correction API",
    description="Offline text correction using SymSpell and T5-ONNX",
    version="1.0.0"
)

# Enable CORS for Streamlit integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage for processed files (in-memory for simplicity)
# In production, use a database or persistent storage
file_storage: Dict[str, Dict[str, str]] = {}

# T5 model cache
t5_model = None
t5_tokenizer = None


def load_t5_model(model_dir: str = "t5-small-onnx-q"):
    """Load T5 ONNX model and tokenizer."""
    global t5_model, t5_tokenizer
    
    if not T5_AVAILABLE:
        raise RuntimeError("T5 dependencies not installed. Install: transformers, optimum[onnxruntime]")
    
    if t5_model is None or t5_tokenizer is None:
        model_path = Path(model_dir)
        if not model_path.exists():
            raise RuntimeError(f"T5 model not found at {model_path}. Run export and quantization scripts first.")
        
        t5_tokenizer = AutoTokenizer.from_pretrained(
            model_dir,
            use_fast=True,
            local_files_only=True
        )
        
        t5_model = ORTModelForSeq2SeqLM.from_pretrained(
            model_dir,
            file_name="encoder_model.onnx",
            decoder_file_name="decoder_model.onnx",
            decoder_with_past_file_name="decoder_with_past_model.onnx",
            local_files_only=True
        )
    
    return t5_tokenizer, t5_model


def apply_symspell_correction(text: str) -> str:
    """Apply SymSpell spell checking correction."""
    checker = SpellChecker(language='en')
    return checker.correct_text(text)


def apply_t5_correction(text: str, num_beams: int = 1, max_new_tokens: int = 64) -> str:
    """Apply T5 grammar correction."""
    tokenizer, model = load_t5_model()
    
    # Prepend instruction for better correction
    input_text = f"grammar: {text}"
    
    inputs = tokenizer(input_text, return_tensors="pt")
    outputs = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        num_beams=num_beams,
        no_repeat_ngram_size=3,
        early_stopping=True
    )
    
    result = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return result


@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "message": "Text Correction API",
        "endpoints": {
            "upload": "/upload",
            "download_intermediate": "/download/{file_id}/intermediate",
            "download_final": "/download/{file_id}/final",
            "status": "/status/{file_id}",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "t5_available": T5_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    enable_t5: bool = True
):
    """
    Upload a text file for correction.
    
    Process:
    1. Read uploaded file
    2. Apply SymSpell correction (save intermediate)
    3. Apply T5 grammar correction (save final) - if enabled
    4. Return file ID for downloads
    
    Args:
        file: Text file to correct
        enable_t5: Feature flag to enable/disable T5 grammar correction (default: True)
    """
    if not file.filename.endswith('.txt'):
        raise HTTPException(status_code=400, detail="Only .txt files are supported")
    
    try:
        # Read uploaded file
        content = await file.read()
        original_text = content.decode('utf-8')
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Step 1: Apply SymSpell correction
        intermediate_text = apply_symspell_correction(original_text)
        
        # Step 2: Apply T5 correction (only if enabled, available, and text is not too long)
        t5_applied = False
        if enable_t5 and T5_AVAILABLE:
            try:
                # Process in chunks if text is long (T5 has token limits)
                if len(intermediate_text) > 500:
                    # Split into sentences and process
                    sentences = intermediate_text.split('.')
                    corrected_sentences = []
                    for sentence in sentences:
                        if sentence.strip():
                            corrected = apply_t5_correction(sentence.strip() + '.', num_beams=1)
                            corrected_sentences.append(corrected)
                    final_text = ' '.join(corrected_sentences)
                else:
                    final_text = apply_t5_correction(intermediate_text, num_beams=1)
                t5_applied = True
            except Exception as e:
                # If T5 fails, use intermediate as final
                final_text = intermediate_text
                print(f"T5 correction failed: {e}")
        else:
            final_text = intermediate_text
            if not enable_t5:
                print("T5 correction disabled by feature flag")
        
        # Create temporary directory for this file
        temp_dir = Path(tempfile.gettempdir()) / "text_correction" / file_id
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Save files
        original_path = temp_dir / "original.txt"
        intermediate_path = temp_dir / "intermediate.txt"
        final_path = temp_dir / "final.txt"
        
        original_path.write_text(original_text, encoding='utf-8')
        intermediate_path.write_text(intermediate_text, encoding='utf-8')
        final_path.write_text(final_text, encoding='utf-8')
        
        # Store metadata
        file_storage[file_id] = {
            "original_filename": file.filename,
            "original_path": str(original_path),
            "intermediate_path": str(intermediate_path),
            "final_path": str(final_path),
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "file_id": file_id,
            "original_filename": file.filename,
            "status": "completed",
            "message": "File processed successfully",
            "t5_enabled": enable_t5,
            "t5_applied": t5_applied,
            "intermediate_corrections": len(intermediate_text) - len(original_text),
            "final_corrections": len(final_text) - len(intermediate_text)
        }
        
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded text")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@app.get("/download/{file_id}/intermediate")
async def download_intermediate(file_id: str):
    """Download intermediate corrected file (after SymSpell)."""
    if file_id not in file_storage:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = file_storage[file_id]["intermediate_path"]
    original_name = file_storage[file_id]["original_filename"]
    
    # Generate download filename
    download_name = original_name.replace('.txt', '_intermediate.txt')
    
    return FileResponse(
        file_path,
        media_type="text/plain",
        filename=download_name
    )


@app.get("/download/{file_id}/final")
async def download_final(file_id: str):
    """Download final corrected file (after T5)."""
    if file_id not in file_storage:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = file_storage[file_id]["final_path"]
    original_name = file_storage[file_id]["original_filename"]
    
    # Generate download filename
    download_name = original_name.replace('.txt', '_final.txt')
    
    return FileResponse(
        file_path,
        media_type="text/plain",
        filename=download_name
    )


@app.get("/status/{file_id}")
async def get_status(file_id: str):
    """Get processing status for a file."""
    if file_id not in file_storage:
        raise HTTPException(status_code=404, detail="File not found")
    
    return {
        "file_id": file_id,
        "status": "completed",
        "metadata": file_storage[file_id]
    }


@app.delete("/cleanup/{file_id}")
async def cleanup_file(file_id: str):
    """Clean up temporary files for a given file ID."""
    if file_id not in file_storage:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Remove temporary directory
    temp_dir = Path(file_storage[file_id]["original_path"]).parent
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    
    # Remove from storage
    del file_storage[file_id]
    
    return {"message": "Files cleaned up successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
