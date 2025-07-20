"""Audio processing components for genetic algorithm music project."""

from .processor import AudioProcessor

# Optional imports
try:
    from .player import AudioPlayer
    PLAYER_AVAILABLE = True
except ImportError:
    PLAYER_AVAILABLE = False
    AudioPlayer = None

try:
    from .analyzer import AudioAnalyzer
    ANALYZER_AVAILABLE = True
except ImportError:
    ANALYZER_AVAILABLE = False
    AudioAnalyzer = None

# Base exports
__all__ = ["AudioProcessor"]

# Add optional exports
if PLAYER_AVAILABLE:
    __all__.append("AudioPlayer")

if ANALYZER_AVAILABLE:
    __all__.append("AudioAnalyzer")