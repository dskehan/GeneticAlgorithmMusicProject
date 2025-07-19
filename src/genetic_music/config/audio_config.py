"""Audio processing configuration management."""

from typing import Optional
from dataclasses import dataclass
from pathlib import Path
import toml


@dataclass
class AudioConfig:
    """Configuration class for audio processing parameters."""
    
    # Audio format parameters
    sample_rate: int = 44100  # Hz
    bit_depth: int = 16  # bits
    channels: int = 1  # 1=mono, 2=stereo
    
    # Processing parameters
    chunk_size: int = 1024  # samples per chunk
    buffer_size: int = 4096  # buffer size for real-time processing
    
    # File format parameters
    output_format: str = "wav"  # "wav", "mp3", "flac"
    compression_quality: int = 5  # 0-9 for FLAC, 0-320 for MP3
    
    # Audio processing options
    normalize: bool = True  # Normalize audio levels
    apply_windowing: bool = True  # Apply windowing for FFT
    window_type: str = "hann"  # "hann", "hamming", "blackman"
    
    # Quality settings
    anti_aliasing: bool = True
    dither: bool = True
    
    # WAV file specific
    wav_header_size: int = 44  # Standard WAV header size in bytes
    
    # Analysis parameters
    fft_size: int = 2048  # FFT window size
    hop_length: Optional[int] = None  # Hop length for STFT (None = fft_size//4)
    
    # Playback parameters
    latency: float = 0.2  # seconds
    device_index: Optional[int] = None  # Audio device index (None = default)
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.hop_length is None:
            self.hop_length = self.fft_size // 4
        self.validate()
    
    def validate(self) -> None:
        """Validate audio configuration parameters."""
        errors = []
        
        # Sample rate validation
        if self.sample_rate <= 0:
            errors.append("Sample rate must be positive")
        
        if self.sample_rate not in [8000, 11025, 16000, 22050, 44100, 48000, 96000, 192000]:
            errors.append(f"Unusual sample rate: {self.sample_rate}. Common rates: 44100, 48000")
        
        # Bit depth validation
        if self.bit_depth not in [8, 16, 24, 32]:
            errors.append(f"Invalid bit depth: {self.bit_depth}. Valid: 8, 16, 24, 32")
        
        # Channels validation
        if self.channels not in [1, 2]:
            errors.append("Channels must be 1 (mono) or 2 (stereo)")
        
        # Chunk size validation
        if self.chunk_size <= 0 or (self.chunk_size & (self.chunk_size - 1)) != 0:
            errors.append("Chunk size must be a positive power of 2")
        
        # Buffer size validation
        if self.buffer_size <= 0:
            errors.append("Buffer size must be positive")
        
        # Format validation
        if self.output_format not in ["wav", "mp3", "flac", "ogg"]:
            errors.append(f"Unsupported output format: {self.output_format}")
        
        # Quality validation
        if not 0 <= self.compression_quality <= 9:
            errors.append("Compression quality must be between 0 and 9")
        
        # Window type validation
        if self.window_type not in ["hann", "hamming", "blackman", "bartlett", "none"]:
            errors.append(f"Invalid window type: {self.window_type}")
        
        # FFT validation
        if self.fft_size <= 0 or (self.fft_size & (self.fft_size - 1)) != 0:
            errors.append("FFT size must be a positive power of 2")
        
        if self.hop_length <= 0:
            errors.append("Hop length must be positive")
        
        # WAV header validation
        if self.wav_header_size < 44:
            errors.append("WAV header size must be at least 44 bytes")
        
        # Latency validation
        if self.latency <= 0:
            errors.append("Latency must be positive")
        
        if errors:
            raise ValueError(f"Invalid audio configuration: {'; '.join(errors)}")
    
    @classmethod
    def create_default(cls) -> "AudioConfig":
        """Create default audio configuration."""
        return cls()
    
    @classmethod
    def create_high_quality(cls) -> "AudioConfig":
        """Create high-quality audio configuration."""
        return cls(
            sample_rate=96000,
            bit_depth=24,
            fft_size=4096,
            compression_quality=9,
            anti_aliasing=True,
            dither=True,
        )
    
    @classmethod
    def create_fast(cls) -> "AudioConfig":
        """Create configuration optimized for speed."""
        return cls(
            sample_rate=22050,
            bit_depth=16,
            chunk_size=512,
            fft_size=1024,
            normalize=False,
            anti_aliasing=False,
            dither=False,
        )
    
    @classmethod
    def create_stereo(cls) -> "AudioConfig":
        """Create stereo audio configuration."""
        return cls(
            channels=2,
            sample_rate=44100,
            bit_depth=16,
        )
    
    @classmethod
    def from_file(cls, file_path: Path) -> "AudioConfig":
        """Load audio configuration from a TOML file."""
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = toml.load(f)
        
        # Extract audio config section
        audio_data = data.get('audio', {})
        return cls(**audio_data)
    
    def to_file(self, file_path: Path) -> None:
        """Save audio configuration to a TOML file."""
        config_data = {
            'audio': {
                'sample_rate': self.sample_rate,
                'bit_depth': self.bit_depth,
                'channels': self.channels,
                'chunk_size': self.chunk_size,
                'buffer_size': self.buffer_size,
                'output_format': self.output_format,
                'compression_quality': self.compression_quality,
                'normalize': self.normalize,
                'apply_windowing': self.apply_windowing,
                'window_type': self.window_type,
                'anti_aliasing': self.anti_aliasing,
                'dither': self.dither,
                'wav_header_size': self.wav_header_size,
                'fft_size': self.fft_size,
                'hop_length': self.hop_length,
                'latency': self.latency,
                'device_index': self.device_index,
            }
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            toml.dump(config_data, f)
    
    def get_frame_count(self, duration_seconds: float) -> int:
        """Calculate the number of frames for a given duration."""
        return int(duration_seconds * self.sample_rate)
    
    def get_duration(self, frame_count: int) -> float:
        """Calculate duration in seconds for a given frame count."""
        return frame_count / self.sample_rate
    
    def get_bytes_per_sample(self) -> int:
        """Get the number of bytes per sample."""
        return self.bit_depth // 8
    
    def get_bytes_per_frame(self) -> int:
        """Get the number of bytes per frame (all channels)."""
        return self.channels * self.get_bytes_per_sample()
    
    def copy(self, **changes) -> "AudioConfig":
        """Create a copy of the configuration with specified changes."""
        import copy
        new_config = copy.deepcopy(self)
        for key, value in changes.items():
            if hasattr(new_config, key):
                setattr(new_config, key, value)
            else:
                raise AttributeError(f"AudioConfig has no attribute '{key}'")
        new_config.validate()
        return new_config
    
    def __str__(self) -> str:
        """String representation of the configuration."""
        return (
            f"AudioConfig(sample_rate={self.sample_rate}, "
            f"bit_depth={self.bit_depth}, "
            f"channels={self.channels}, "
            f"format={self.output_format})"
        )