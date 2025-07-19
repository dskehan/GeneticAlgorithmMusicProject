"""Audio file processing and manipulation."""

from typing import Tuple, Optional, Union
from pathlib import Path
import numpy as np
import soundfile as sf
import librosa
from ..config.audio_config import AudioConfig


class AudioProcessor:
    """Handles audio file I/O and processing operations."""
    
    def __init__(self, config: Optional[AudioConfig] = None):
        """
        Initialize the audio processor.
        
        Args:
            config: Audio configuration, defaults to AudioConfig.create_default()
        """
        self.config = config or AudioConfig.create_default()
    
    def load_wav_file(self, file_path: Union[str, Path]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Load a WAV file and separate header from audio data.
        
        Args:
            file_path: Path to the WAV file
            
        Returns:
            Tuple of (audio_data, header_data) as numpy arrays
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is invalid or too small
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        
        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        
        # Read the raw file bytes
        try:
            with open(file_path, 'rb') as f:
                raw_bytes = f.read()
        except IOError as e:
            raise ValueError(f"Failed to read file: {e}")
        
        if len(raw_bytes) < self.config.wav_header_size:
            raise ValueError(
                f"File too small to be a valid WAV file. "
                f"Expected at least {self.config.wav_header_size} bytes, got {len(raw_bytes)}"
            )
        
        # Separate header and audio data
        header_data = np.frombuffer(
            raw_bytes[:self.config.wav_header_size], 
            dtype=np.uint8
        )
        audio_data = np.frombuffer(
            raw_bytes[self.config.wav_header_size:], 
            dtype=np.uint8
        )
        
        return audio_data, header_data
    
    def load_audio_with_librosa(self, file_path: Union[str, Path]) -> Tuple[np.ndarray, int]:
        """
        Load audio file using librosa for better format support.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Tuple of (audio_samples, sample_rate)
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        
        try:
            # Load audio with librosa
            audio_data, sample_rate = librosa.load(
                str(file_path),
                sr=self.config.sample_rate,
                mono=(self.config.channels == 1)
            )
            
            return audio_data, sample_rate
            
        except Exception as e:
            raise ValueError(f"Failed to load audio file: {e}")
    
    def save_wav_file(self, audio_data: np.ndarray, header_data: np.ndarray, 
                      output_path: Union[str, Path]) -> None:
        """
        Save audio data as a WAV file with the provided header.
        
        Args:
            audio_data: Audio data as numpy array
            header_data: WAV header data
            output_path: Path for the output file
        """
        output_path = Path(output_path)
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Combine header and audio data
            full_data = np.concatenate([header_data, audio_data])
            
            # Write to file
            with open(output_path, 'wb') as f:
                f.write(full_data.tobytes())
                
        except IOError as e:
            raise ValueError(f"Failed to save WAV file: {e}")
    
    def save_audio_with_soundfile(self, audio_data: np.ndarray, 
                                  output_path: Union[str, Path]) -> None:
        """
        Save audio data using soundfile for better format support.
        
        Args:
            audio_data: Audio samples as float array
            output_path: Path for the output file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Ensure audio data is in correct format
            if audio_data.dtype != np.float32:
                if audio_data.dtype == np.uint8:
                    # Convert uint8 to float32
                    audio_data = (audio_data.astype(np.float32) - 128) / 128.0
                else:
                    audio_data = audio_data.astype(np.float32)
            
            # Normalize if requested
            if self.config.normalize:
                max_val = np.max(np.abs(audio_data))
                if max_val > 0:
                    audio_data = audio_data / max_val
            
            # Save with soundfile
            sf.write(
                str(output_path),
                audio_data,
                self.config.sample_rate,
                subtype=f'PCM_{self.config.bit_depth}'
            )
            
        except Exception as e:
            raise ValueError(f"Failed to save audio file: {e}")
    
    def convert_bytes_to_audio(self, byte_data: np.ndarray) -> np.ndarray:
        """
        Convert byte data to audio samples.
        
        Args:
            byte_data: Audio data as bytes (uint8)
            
        Returns:
            Audio samples as float32 array
        """
        if byte_data.dtype != np.uint8:
            byte_data = byte_data.astype(np.uint8)
        
        # Convert to float32 range [-1, 1]
        audio_samples = (byte_data.astype(np.float32) - 128) / 128.0
        
        return audio_samples
    
    def convert_audio_to_bytes(self, audio_samples: np.ndarray) -> np.ndarray:
        """
        Convert audio samples to byte data.
        
        Args:
            audio_samples: Audio samples as float array
            
        Returns:
            Audio data as bytes (uint8)
        """
        # Ensure audio is in [-1, 1] range
        audio_clipped = np.clip(audio_samples, -1.0, 1.0)
        
        # Convert to uint8 range [0, 255]
        byte_data = ((audio_clipped * 128.0) + 128).astype(np.uint8)
        
        return byte_data
    
    def resample_audio(self, audio_data: np.ndarray, 
                       original_sr: int, target_sr: int) -> np.ndarray:
        """
        Resample audio to a different sample rate.
        
        Args:
            audio_data: Audio samples
            original_sr: Original sample rate
            target_sr: Target sample rate
            
        Returns:
            Resampled audio data
        """
        if original_sr == target_sr:
            return audio_data
        
        try:
            resampled = librosa.resample(
                audio_data, 
                orig_sr=original_sr, 
                target_sr=target_sr
            )
            return resampled
        except Exception as e:
            raise ValueError(f"Failed to resample audio: {e}")
    
    def apply_window(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Apply windowing function to audio data.
        
        Args:
            audio_data: Audio samples
            
        Returns:
            Windowed audio data
        """
        if not self.config.apply_windowing or self.config.window_type == "none":
            return audio_data
        
        window_funcs = {
            "hann": np.hanning,
            "hamming": np.hamming,
            "blackman": np.blackman,
            "bartlett": np.bartlett
        }
        
        if self.config.window_type not in window_funcs:
            raise ValueError(f"Unsupported window type: {self.config.window_type}")
        
        window = window_funcs[self.config.window_type](len(audio_data))
        return audio_data * window
    
    def get_audio_info(self, file_path: Union[str, Path]) -> dict:
        """
        Get information about an audio file.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Dictionary with audio file information
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        
        try:
            info = sf.info(str(file_path))
            
            return {
                "duration": info.duration,
                "frames": info.frames,
                "sample_rate": info.samplerate,
                "channels": info.channels,
                "format": info.format,
                "subtype": info.subtype,
                "file_size": file_path.stat().st_size,
            }
            
        except Exception as e:
            raise ValueError(f"Failed to get audio info: {e}")
    
    def create_output_filename(self, base_name: str, fitness: float, 
                              generation: int = None) -> str:
        """
        Create standardized output filename.
        
        Args:
            base_name: Base filename without extension
            fitness: Fitness value
            generation: Optional generation number
            
        Returns:
            Formatted filename
        """
        fitness_str = f"{fitness:.2f}".replace(".", "_")
        
        if generation is not None:
            return f"{base_name}_gen{generation:04d}_fitness{fitness_str}.{self.config.output_format}"
        else:
            return f"{base_name}_fitness{fitness_str}.{self.config.output_format}"
    
    def validate_audio_file(self, file_path: Union[str, Path]) -> bool:
        """
        Validate if a file is a valid audio file.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            True if valid, False otherwise
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists() or not file_path.is_file():
                return False
            
            # Try to get info without loading the full file
            sf.info(str(file_path))
            return True
            
        except Exception:
            return False
    
    def get_file_size_mb(self, file_path: Union[str, Path]) -> float:
        """Get file size in megabytes."""
        file_path = Path(file_path)
        if not file_path.exists():
            return 0.0
        
        return file_path.stat().st_size / (1024 * 1024)