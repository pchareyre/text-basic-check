"""
File upload and correction router.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from ..models import UploadResponse
from ..services.correction import SpellCheckingService, GrammarCorrectionService
from ..services.storage import FileStorageService
from ..config import settings

router = APIRouter(prefix="/files", tags=["files"])

# Initialize services
spell_service = SpellCheckingService(language=settings.spell_checker_language)
grammar_service = GrammarCorrectionService(model_dir=settings.t5_model_dir)
storage_service = FileStorageService(base_dir=settings.temp_dir)


@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    enable_t5: bool = True
):
    """
    Upload a text file for correction.
    
    Process:
    1. Read uploaded file
    2. Apply SymSpell correction (save intermediate)
    3. Apply T5 grammar correction if enabled (save final)
    4. Return file ID for downloads
    
    Args:
        file: Text file to correct
        enable_t5: Feature flag to enable/disable T5 grammar correction
    """
    # Validate file extension
    if not file.filename.endswith('.txt'):
        raise HTTPException(
            status_code=400,
            detail="Only .txt files are supported"
        )
    
    try:
        # Read uploaded file
        content = await file.read()
        original_text = content.decode('utf-8')
        
        # Create file entry in storage
        file_id = storage_service.create_file_entry(file.filename)
        
        # Save original
        storage_service.save_file(file_id, "original", original_text)
        
        # Step 1: Apply SymSpell correction
        intermediate_text = spell_service.correct_text(original_text)
        storage_service.save_file(file_id, "intermediate", intermediate_text)
        
        # Step 2: Apply T5 correction (if enabled and available)
        t5_applied = False
        final_text = intermediate_text
        
        if enable_t5 and grammar_service.is_available():
            try:
                # Use chunked correction for longer texts
                final_text = grammar_service.correct_text_chunked(
                    intermediate_text,
                    chunk_size=500,
                    num_beams=1
                )
                t5_applied = True
                storage_service.update_metadata(file_id, t5_applied=True)
            except Exception as e:
                print(f"T5 correction failed: {e}")
                final_text = intermediate_text
        elif not enable_t5:
            print("T5 correction disabled by feature flag")
        
        # Save final text
        storage_service.save_file(file_id, "final", final_text)
        
        return UploadResponse(
            file_id=file_id,
            original_filename=file.filename,
            status="completed",
            message="File processed successfully",
            t5_enabled=enable_t5,
            t5_applied=t5_applied,
            intermediate_corrections=len(intermediate_text) - len(original_text),
            final_corrections=len(final_text) - len(intermediate_text)
        )
        
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="File must be UTF-8 encoded text"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )


@router.get("/download/{file_id}/intermediate")
async def download_intermediate(file_id: str):
    """Download intermediate corrected file (after SymSpell)."""
    if not storage_service.file_exists(file_id):
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        file_path = storage_service.get_file_path(file_id, "intermediate")
        metadata = storage_service.get_metadata(file_id)
        original_name = metadata["original_filename"]
        
        download_name = original_name.replace('.txt', '_intermediate.txt')
        
        return FileResponse(
            file_path,
            media_type="text/plain",
            filename=download_name
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error downloading file: {str(e)}"
        )


@router.get("/download/{file_id}/final")
async def download_final(file_id: str):
    """Download final corrected file (after T5)."""
    if not storage_service.file_exists(file_id):
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        file_path = storage_service.get_file_path(file_id, "final")
        metadata = storage_service.get_metadata(file_id)
        original_name = metadata["original_filename"]
        
        download_name = original_name.replace('.txt', '_final.txt')
        
        return FileResponse(
            file_path,
            media_type="text/plain",
            filename=download_name
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error downloading file: {str(e)}"
        )


@router.get("/status/{file_id}")
async def get_status(file_id: str):
    """Get processing status for a file."""
    if not storage_service.file_exists(file_id):
        raise HTTPException(status_code=404, detail="File not found")
    
    return {
        "file_id": file_id,
        "status": "completed",
        "metadata": storage_service.get_metadata(file_id)
    }


@router.delete("/cleanup/{file_id}")
async def cleanup_file(file_id: str):
    """Clean up temporary files for a given file ID."""
    if not storage_service.file_exists(file_id):
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        storage_service.cleanup_file(file_id)
        return {"message": "Files cleaned up successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error cleaning up files: {str(e)}"
        )
