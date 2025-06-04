from fastapi import FastAPI, UploadFile, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from pathlib import Path
import tempfile
import torch
from pyannote.audio import Pipeline
from datetime import timedelta
import logging
import time

from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description="Voice to Text and Speaker Diarization using Pyannote",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# CORS middleware configuration
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Global model instances
DIARIZATION_MODEL = None

# Track processing status
processing_status = {
    "is_processing": False,
    "last_processed": None,
    "processing_time": None
}

def format_time(seconds: float) -> str:
    """Convert seconds to SRT time format"""
    return str(timedelta(seconds=seconds)).replace('.', ',')

class DiarizationResult(BaseModel):
    start: float
    end: float
    speaker: str
    text: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "start": 1.23,
                "end": 4.56,
                "speaker": "SPEAKER_00",
                "text": "Hello, this is a test."
            }
        }

class TranscriptionResponse(BaseModel):
    segments: List[DiarizationResult]
    full_text: str
    processing_time: Optional[float] = None
    
    class Config:
        schema_extra = {
            "example": {
                "segments": [
                    {
                        "start": 1.23,
                        "end": 4.56,
                        "speaker": "SPEAKER_00",
                        "text": "Hello, this is a test."
                    }
                ],
                "full_text": "Hello, this is a test.",
                "processing_time": 2.34
            }
        }

@app.on_event("startup")
async def load_models():
    """Load ML models on startup"""
    global DIARIZATION_MODEL
    
    if not settings.HUGGINGFACE_TOKEN:
        logger.error("HUGGINGFACE_TOKEN not found in environment variables")
        return
    
    try:
        logger.info(f"Loading diarization model: {settings.DIARIZATION_MODEL}")
        DIARIZATION_MODEL = Pipeline.from_pretrained(
            settings.DIARIZATION_MODEL,
            use_auth_token=settings.HUGGINGFACE_TOKEN
        )
        logger.info("Successfully loaded diarization model")
    except Exception as e:
        logger.error(f"Failed to load models: {str(e)}")
        if "accept the conditions" in str(e).lower():
            logger.error("You need to accept the model's terms and conditions at https://huggingface.co/pyannote/speaker-diarization")
        raise

def validate_audio_file(file: UploadFile) -> None:
    """Validate the uploaded audio file"""
    # Check file type
    content_type = file.content_type
    if content_type not in settings.SUPPORTED_AUDIO_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {content_type} not supported. Supported types: {', '.join(settings.SUPPORTED_AUDIO_TYPES)}"
        )
    
    # Check file size (max 100MB)
    max_size = 100 * 1024 * 1024  # 100MB
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset file pointer
    
    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is 100MB"
        )

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main interface"""
    return FileResponse('static/index.html')

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": DIARIZATION_MODEL is not None,
        "processing": processing_status["is_processing"]
    }

@app.post("/api/v1/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    audio_file: UploadFile,
    num_speakers: Optional[int] = None,
    min_speakers: Optional[int] = None,
    max_speakers: Optional[int] = None
):
    """
    Transcribe audio file with speaker diarization
    
    Parameters:
    - audio_file: Audio file to process (wav, mp3, etc.)
    - num_speakers: Exact number of speakers (optional)
    - min_speakers: Minimum number of speakers (optional)
    - max_speakers: Maximum number of speakers (optional)
    """
    global processing_status
    
    # Check if model is loaded
    if not DIARIZATION_MODEL:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Diarization model not loaded. Please check server logs."
        )
    
    # Check if already processing
    if processing_status["is_processing"]:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Server is currently processing another request. Please try again later."
        )
    
    # Validate audio file
    try:
        validate_audio_file(audio_file)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error validating file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid audio file"
        )
    
    # Update processing status
    processing_status["is_processing"] = True
    processing_status["last_processed"] = time.time()
    start_time = time.time()
    
    # Save uploaded file to temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(audio_file.filename).suffix) as tmp:
        tmp.write(audio_file.file.read())
        audio_path = tmp.name
    
    try:
        logger.info(f"Processing audio file: {audio_file.filename}")
        logger.debug(f"Speaker settings - num: {num_speakers}, min: {min_speakers}, max: {max_speakers}")
        
        # Apply diarization
        diarization = DIARIZATION_MODEL(
            audio_path,
            num_speakers=num_speakers,
            min_speakers=min_speakers,
            max_speakers=max_speakers
        )
        
        # Convert to response format
        segments = []
        speakers = set()
        
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segments.append(DiarizationResult(
                start=round(turn.start, 2),
                end=round(turn.end, 2),
                speaker=speaker,
                text=None  # This would be filled by an ASR model
            ))
            speakers.add(speaker)
        
        processing_time = time.time() - start_time
        
        logger.info(f"Processed audio in {processing_time:.2f} seconds. Found {len(speakers)} speakers.")
        
        return {
            "segments": segments,
            "full_text": "",  # Would be filled by ASR
            "processing_time": round(processing_time, 2)
        }
        
    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing audio: {str(e)}"
        )
    finally:
        # Clean up
        processing_status["is_processing"] = False
        processing_status["processing_time"] = time.time() - start_time
        
        try:
            os.unlink(audio_path)
        except Exception as e:
            logger.warning(f"Failed to delete temporary file {audio_path}: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
