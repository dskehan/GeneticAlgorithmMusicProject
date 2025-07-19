"""
Genetic Algorithm Music Project - Python Implementation

A comprehensive genetic algorithm framework for evolving audio files.
"""

__version__ = "1.0.0"
__author__ = "Genetic Music Team"
__email__ = "contact@geneticmusic.com"

# Core imports
from .config.ga_config import GAConfig
from .config.audio_config import AudioConfig
from .simulator.genetic_simulator import GeneticSimulator
from .simulator.chromosome import AudioChromosome
from .audio.processor import AudioProcessor
from .audio.player import AudioPlayer

# Main classes for public API
__all__ = [
    "GAConfig",
    "AudioConfig", 
    "GeneticSimulator",
    "AudioChromosome",
    "AudioProcessor",
    "AudioPlayer",
]

# Version info
VERSION_INFO = (1, 0, 0)

def get_version():
    """Get the version string."""
    return __version__

def get_author():
    """Get the author information."""
    return f"{__author__} <{__email__}>"