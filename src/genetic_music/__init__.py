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

# Optional imports (may require additional dependencies)
try:
    from .audio.player import AudioPlayer
    AUDIO_PLAYER_AVAILABLE = True
except ImportError:
    AUDIO_PLAYER_AVAILABLE = False
    AudioPlayer = None

try:
    from .audio.analyzer import AudioAnalyzer
    AUDIO_ANALYZER_AVAILABLE = True
except ImportError:
    AUDIO_ANALYZER_AVAILABLE = False
    AudioAnalyzer = None

# Main classes for public API
__all__ = [
    "GAConfig",
    "AudioConfig", 
    "GeneticSimulator",
    "AudioChromosome",
    "AudioProcessor"
]

# Add optional classes if available
if AUDIO_PLAYER_AVAILABLE:
    __all__.append("AudioPlayer")

if AUDIO_ANALYZER_AVAILABLE:
    __all__.append("AudioAnalyzer")

# Version info
def get_version():
    """Get the current version of the genetic music package."""
    return __version__

def get_available_features():
    """Get information about available optional features."""
    return {
        "audio_player": AUDIO_PLAYER_AVAILABLE,
        "audio_analyzer": AUDIO_ANALYZER_AVAILABLE,
        "version": __version__
    }