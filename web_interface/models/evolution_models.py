"""
Evolution Models

Pydantic models for genetic algorithm evolution API.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class EvolutionStatus(str, Enum):
    """Evolution job status enumeration."""
    INITIALIZING = "initializing"
    LOADING_AUDIO = "loading_audio"
    CREATING_POPULATION = "creating_population"
    EVOLVING = "evolving"
    COMPLETED = "completed"
    ERROR = "error"
    PAUSED = "paused"
    STOPPED = "stopped"
    FITNESS_THRESHOLD_REACHED = "fitness_threshold_reached"
    CONVERGED = "converged"


class FitnessFunction(str, Enum):
    """Available fitness functions."""
    BYTE_SIMILARITY = "byte_similarity"
    SPECTRAL = "spectral"
    PERCEPTUAL = "perceptual"


class EvolutionRequest(BaseModel):
    """Request model for starting evolution."""
    population_size: int = Field(default=200, ge=10, le=2000, description="Population size")
    mutation_rate: float = Field(default=0.02, ge=0.001, le=0.5, description="Mutation rate")
    crossover_rate: float = Field(default=0.8, ge=0.1, le=1.0, description="Crossover rate")
    max_generations: int = Field(default=100, ge=1, le=1000, description="Maximum generations")
    fitness_threshold: float = Field(default=95.0, ge=50.0, le=100.0, description="Fitness threshold")
    elite_size: float = Field(default=0.1, ge=0.0, le=0.5, description="Elite proportion")
    fitness_function: FitnessFunction = Field(default=FitnessFunction.BYTE_SIMILARITY, description="Fitness function")
    save_generations: List[int] = Field(default=[10, 25, 50, 75, 90, 95], description="Generations to save")


class EvolutionProgress(BaseModel):
    """Real-time evolution progress data."""
    job_id: str = Field(description="Job identifier")
    status: EvolutionStatus = Field(description="Current status")
    progress: float = Field(ge=0.0, le=100.0, description="Progress percentage")
    generation: int = Field(ge=0, description="Current generation")
    best_fitness: float = Field(ge=0.0, le=100.0, description="Best fitness in current generation")
    avg_fitness: float = Field(ge=0.0, le=100.0, description="Average fitness in current generation")
    population_size: int = Field(ge=1, description="Population size")
    stagnant_generations: Optional[int] = Field(default=0, description="Generations without improvement")
    start_time: datetime = Field(description="Job start time")
    estimated_remaining: Optional[int] = Field(default=None, description="Estimated seconds remaining")


class EvolutionResult(BaseModel):
    """Final evolution results."""
    job_id: str = Field(description="Job identifier")
    status: EvolutionStatus = Field(description="Final status")
    final_generation: int = Field(ge=0, description="Final generation reached")
    final_best_fitness: float = Field(ge=0.0, le=100.0, description="Final best fitness")
    final_avg_fitness: float = Field(ge=0.0, le=100.0, description="Final average fitness")
    total_time: float = Field(ge=0.0, description="Total execution time in seconds")
    convergence_generation: Optional[int] = Field(default=None, description="Generation where convergence occurred")
    files: List[Dict[str, Any]] = Field(default=[], description="Generated result files")


class JobSummary(BaseModel):
    """Summary of an evolution job."""
    job_id: str = Field(description="Job identifier")
    status: EvolutionStatus = Field(description="Job status")
    progress: float = Field(ge=0.0, le=100.0, description="Progress percentage")
    start_time: datetime = Field(description="Job start time")
    end_time: Optional[datetime] = Field(default=None, description="Job end time")
    best_fitness: float = Field(ge=0.0, le=100.0, description="Best fitness achieved")
    generation: int = Field(ge=0, description="Current/final generation")


class EvolutionStatistics(BaseModel):
    """Detailed evolution statistics."""
    job_id: str = Field(description="Job identifier")
    final_generation: int = Field(ge=0, description="Final generation")
    best_fitness: float = Field(ge=0.0, le=100.0, description="Best fitness")
    avg_fitness: float = Field(ge=0.0, le=100.0, description="Average fitness")
    population_size: int = Field(ge=1, description="Population size")
    fitness_distribution: Dict[str, float] = Field(description="Fitness distribution statistics")
    generation_stats: List[Dict[str, float]] = Field(default=[], description="Per-generation statistics")


class PresetConfiguration(BaseModel):
    """Predefined evolution configuration preset."""
    name: str = Field(description="Preset name")
    description: str = Field(description="Preset description")
    population_size: int = Field(ge=10, le=2000, description="Population size")
    mutation_rate: float = Field(ge=0.001, le=0.5, description="Mutation rate")
    crossover_rate: float = Field(ge=0.1, le=1.0, description="Crossover rate")
    max_generations: int = Field(ge=1, le=1000, description="Maximum generations")
    fitness_threshold: float = Field(ge=50.0, le=100.0, description="Fitness threshold")
    elite_size: float = Field(ge=0.0, le=0.5, description="Elite proportion")
    estimated_duration: str = Field(description="Estimated duration description")


class WebSocketMessage(BaseModel):
    """WebSocket message structure."""
    type: str = Field(description="Message type")
    job_id: Optional[str] = Field(default=None, description="Job identifier")
    data: Dict[str, Any] = Field(description="Message data")
    timestamp: datetime = Field(default_factory=datetime.now, description="Message timestamp")


class JobControl(BaseModel):
    """Job control command."""
    action: str = Field(regex="^(pause|resume|stop)$", description="Control action")
    job_id: str = Field(description="Job identifier")


class HealthStatus(BaseModel):
    """System health status."""
    status: str = Field(description="Health status")
    timestamp: datetime = Field(description="Status timestamp")
    version: str = Field(description="API version")
    active_jobs: int = Field(ge=0, description="Number of active jobs")
    total_connections: int = Field(ge=0, description="Total WebSocket connections")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(description="Error message")
    status_code: int = Field(description="HTTP status code")
    timestamp: datetime = Field(description="Error timestamp")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")


class FileInfo(BaseModel):
    """Information about a result file."""
    filename: str = Field(description="File name")
    size: int = Field(ge=0, description="File size in bytes")
    download_url: str = Field(description="Download URL")
    created_at: Optional[datetime] = Field(default=None, description="File creation time")
    file_type: Optional[str] = Field(default=None, description="File type/format")


class AudioInfo(BaseModel):
    """Audio file information."""
    filename: str = Field(description="Original filename")
    duration: float = Field(ge=0.0, description="Duration in seconds")
    sample_rate: int = Field(ge=1, description="Sample rate in Hz")
    channels: int = Field(ge=1, description="Number of channels")
    bit_depth: Optional[int] = Field(default=None, description="Bit depth")
    file_size: int = Field(ge=0, description="File size in bytes")


class UploadResponse(BaseModel):
    """File upload response."""
    success: bool = Field(description="Upload success status")
    filename: str = Field(description="Uploaded filename")
    size: int = Field(ge=0, description="File size in bytes")
    audio_info: Optional[AudioInfo] = Field(default=None, description="Audio file information")
    message: str = Field(description="Response message")