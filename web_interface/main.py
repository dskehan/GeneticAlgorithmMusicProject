"""
FastAPI Web Interface for Genetic Algorithm Music Evolution

A modern web interface for evolving audio files using genetic algorithms.
"""

import asyncio
import json
import uuid
from pathlib import Path
from typing import List, Optional, Dict, Any
import aiofiles
from datetime import datetime

from fastapi import (
    FastAPI, 
    UploadFile, 
    File, 
    Form,
    BackgroundTasks,
    WebSocket,
    WebSocketDisconnect,
    HTTPException,
    Depends,
    status
)
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request

from pydantic import BaseModel, Field
import uvicorn

# Import our genetic algorithm components
import sys
sys.path.append('../src')
from genetic_music import GAConfig, AudioConfig
from genetic_music.audio import AudioProcessor
from genetic_music.simulator import AudioChromosome

# Import local services
from services.evolution_service import EvolutionService
from services.websocket_manager import WebSocketManager
from models.evolution_models import EvolutionRequest, EvolutionStatus, EvolutionResult

# Initialize FastAPI app
app = FastAPI(
    title="Genetic Algorithm Music Evolution",
    description="Evolve audio files using genetic algorithms with real-time web interface",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize services
evolution_service = EvolutionService()
websocket_manager = WebSocketManager()

# Storage paths
UPLOAD_DIR = Path("uploads")
RESULTS_DIR = Path("results")
UPLOAD_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)


# Pydantic models for API
class EvolutionParameters(BaseModel):
    """Parameters for genetic algorithm evolution."""
    population_size: int = Field(default=200, ge=10, le=2000)
    mutation_rate: float = Field(default=0.02, ge=0.001, le=0.5)
    crossover_rate: float = Field(default=0.8, ge=0.1, le=1.0)
    max_generations: int = Field(default=100, ge=1, le=1000)
    fitness_threshold: float = Field(default=95.0, ge=50.0, le=100.0)
    elite_size: float = Field(default=0.1, ge=0.0, le=0.5)
    fitness_function: str = Field(default="byte_similarity", regex="^(byte_similarity|spectral|perceptual)$")
    save_generations: List[int] = Field(default=[10, 25, 50, 75, 90, 95])


class JobResponse(BaseModel):
    """Response when starting an evolution job."""
    job_id: str
    status: str
    message: str
    estimated_duration: Optional[int] = None


# === Web Routes ===

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main web interface."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/evolution/{job_id}", response_class=HTMLResponse)
async def evolution_page(request: Request, job_id: str):
    """Serve the evolution monitoring page."""
    job_status = await evolution_service.get_job_status(job_id)
    if not job_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return templates.TemplateResponse(
        "evolution.html", 
        {"request": request, "job_id": job_id, "job_status": job_status}
    )


# === API Routes ===

@app.post("/api/v1/evolve", response_model=JobResponse)
async def start_evolution(
    background_tasks: BackgroundTasks,
    audio_file: UploadFile = File(...),
    population_size: int = Form(200),
    mutation_rate: float = Form(0.02),
    crossover_rate: float = Form(0.8),
    max_generations: int = Form(100),
    fitness_threshold: float = Form(95.0),
    elite_size: float = Form(0.1),
    fitness_function: str = Form("byte_similarity"),
    save_generations: str = Form("10,25,50,75,90,95")
):
    """Start an evolution job with uploaded audio file."""
    
    # Validate file type
    if not audio_file.filename.lower().endswith(('.wav', '.mp3', '.flac', '.ogg')):
        raise HTTPException(
            status_code=400, 
            detail="Unsupported file format. Please upload WAV, MP3, FLAC, or OGG files."
        )
    
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    
    # Save uploaded file
    file_path = UPLOAD_DIR / f"{job_id}_{audio_file.filename}"
    async with aiofiles.open(file_path, 'wb') as f:
        content = await audio_file.read()
        await f.write(content)
    
    # Parse save generations
    try:
        save_gen_list = [int(x.strip()) for x in save_generations.split(",") if x.strip()]
    except ValueError:
        save_gen_list = [10, 25, 50, 75, 90, 95]
    
    # Create evolution parameters
    params = EvolutionParameters(
        population_size=population_size,
        mutation_rate=mutation_rate,
        crossover_rate=crossover_rate,
        max_generations=max_generations,
        fitness_threshold=fitness_threshold,
        elite_size=elite_size,
        fitness_function=fitness_function,
        save_generations=save_gen_list
    )
    
    # Estimate duration (rough calculation)
    estimated_duration = (population_size * max_generations) // 1000  # seconds
    
    # Start background evolution task
    background_tasks.add_task(
        evolution_service.run_evolution,
        job_id=job_id,
        file_path=str(file_path),
        params=params,
        websocket_manager=websocket_manager
    )
    
    return JobResponse(
        job_id=job_id,
        status="started",
        message="Evolution job started successfully",
        estimated_duration=estimated_duration
    )


@app.get("/api/v1/status/{job_id}")
async def get_job_status(job_id: str):
    """Get the current status of an evolution job."""
    status = await evolution_service.get_job_status(job_id)
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return status


@app.get("/api/v1/results/{job_id}")
async def get_job_results(job_id: str):
    """Get the results of a completed evolution job."""
    results = await evolution_service.get_job_results(job_id)
    if not results:
        raise HTTPException(status_code=404, detail="Job not found or not completed")
    
    return results


@app.get("/api/v1/download/{job_id}/{filename}")
async def download_result(job_id: str, filename: str):
    """Download a specific result file."""
    file_path = RESULTS_DIR / job_id / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type='audio/wav'
    )


@app.get("/api/v1/jobs")
async def list_jobs(limit: int = 50, offset: int = 0):
    """List all evolution jobs."""
    jobs = await evolution_service.list_jobs(limit=limit, offset=offset)
    return {"jobs": jobs, "total": len(jobs)}


@app.delete("/api/v1/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete an evolution job and its results."""
    success = await evolution_service.delete_job(job_id)
    if not success:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {"message": "Job deleted successfully"}


# === WebSocket Routes ===

@app.websocket("/ws/evolution/{job_id}")
async def evolution_websocket(websocket: WebSocket, job_id: str):
    """WebSocket endpoint for real-time evolution updates."""
    await websocket.accept()
    await websocket_manager.connect(job_id, websocket)
    
    try:
        while True:
            # Keep connection alive and handle client messages
            data = await websocket.receive_text()
            
            # Handle client commands (pause, resume, stop)
            if data == "pause":
                await evolution_service.pause_job(job_id)
            elif data == "resume":
                await evolution_service.resume_job(job_id)
            elif data == "stop":
                await evolution_service.stop_job(job_id)
            
    except WebSocketDisconnect:
        await websocket_manager.disconnect(job_id, websocket)


# === Utility Routes ===

@app.get("/api/v1/presets")
async def get_presets():
    """Get predefined evolution parameter presets."""
    return {
        "fast": {
            "population_size": 100,
            "mutation_rate": 0.05,
            "max_generations": 50,
            "fitness_threshold": 90.0,
            "description": "Quick evolution for testing"
        },
        "balanced": {
            "population_size": 200,
            "mutation_rate": 0.02,
            "max_generations": 100,
            "fitness_threshold": 95.0,
            "description": "Balanced speed and quality"
        },
        "thorough": {
            "population_size": 500,
            "mutation_rate": 0.01,
            "max_generations": 300,
            "fitness_threshold": 98.0,
            "description": "High-quality evolution (slow)"
        },
        "experimental": {
            "population_size": 1000,
            "mutation_rate": 0.001,
            "max_generations": 1000,
            "fitness_threshold": 99.5,
            "description": "Maximum quality (very slow)"
        }
    }


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "active_jobs": len(evolution_service.active_jobs)
    }


# === Error Handlers ===

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler for unexpected errors."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )


# === Startup/Shutdown Events ===

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    print("🎵 Starting Genetic Algorithm Music Evolution Web Interface")
    print("📡 WebSocket manager initialized")
    print("🔬 Evolution service initialized")
    

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("🛑 Shutting down evolution service...")
    await evolution_service.cleanup()
    print("👋 Genetic Algorithm Music Evolution Web Interface stopped")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )