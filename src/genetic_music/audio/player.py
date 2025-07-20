"""
Audio Player

Handles audio playback functionality for the genetic algorithm music project.
"""

import numpy as np
import soundfile as sf
import tempfile
from pathlib import Path
from typing import Optional, Union
import threading
import time

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False


class AudioPlayer:
    """
    Audio player for playing evolved audio samples.
    
    Supports multiple backends: pygame, pyaudio, or system default.
    """
    
    def __init__(self, backend: str = "auto"):
        """
        Initialize the audio player.
        
        Args:
            backend: Audio backend to use ("pygame", "pyaudio", "system", or "auto")
        """
        self.backend = backend
        self.is_playing = False
        self.current_thread: Optional[threading.Thread] = None
        
        # Auto-select backend
        if backend == "auto":
            if PYGAME_AVAILABLE:
                self.backend = "pygame"
            elif PYAUDIO_AVAILABLE:
                self.backend = "pyaudio"
            else:
                self.backend = "system"
        
        # Initialize backend
        self._initialize_backend()
    
    def _initialize_backend(self):
        """Initialize the selected audio backend."""
        if self.backend == "pygame" and PYGAME_AVAILABLE:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        elif self.backend == "pyaudio" and PYAUDIO_AVAILABLE:
            self.pa = pyaudio.PyAudio()
        elif self.backend == "system":
            # System backend doesn't require initialization
            pass
        else:
            print(f"Warning: Backend '{self.backend}' not available, falling back to system")
            self.backend = "system"
    
    def play_audio_data(self, audio_data: np.ndarray, sample_rate: int = 44100, 
                       header_data: Optional[np.ndarray] = None, blocking: bool = False):
        """
        Play audio data directly.
        
        Args:
            audio_data: Audio data as numpy array
            sample_rate: Sample rate in Hz
            header_data: Optional WAV header data
            blocking: Whether to block until playback finishes
        """
        if self.is_playing:
            self.stop()
        
        if blocking:
            self._play_audio_data_sync(audio_data, sample_rate, header_data)
        else:
            self.current_thread = threading.Thread(
                target=self._play_audio_data_sync,
                args=(audio_data, sample_rate, header_data)
            )
            self.current_thread.daemon = True
            self.current_thread.start()
    
    def _play_audio_data_sync(self, audio_data: np.ndarray, sample_rate: int, 
                             header_data: Optional[np.ndarray]):
        """Synchronous audio playback implementation."""
        self.is_playing = True
        
        try:
            if self.backend == "pygame" and PYGAME_AVAILABLE:
                self._play_with_pygame(audio_data, sample_rate)
            elif self.backend == "pyaudio" and PYAUDIO_AVAILABLE:
                self._play_with_pyaudio(audio_data, sample_rate)
            else:
                self._play_with_system(audio_data, sample_rate, header_data)
        except Exception as e:
            print(f"Error during audio playback: {e}")
        finally:
            self.is_playing = False
    
    def _play_with_pygame(self, audio_data: np.ndarray, sample_rate: int):
        """Play audio using pygame backend."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            # Ensure audio data is in the right format
            if audio_data.dtype != np.int16:
                # Convert to int16
                if audio_data.dtype == np.float32 or audio_data.dtype == np.float64:
                    audio_data = (audio_data * 32767).astype(np.int16)
                else:
                    audio_data = audio_data.astype(np.int16)
            
            # Save to temporary file
            sf.write(tmp_path, audio_data, sample_rate)
            
            # Play with pygame
            pygame.mixer.music.load(tmp_path)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy() and self.is_playing:
                time.sleep(0.1)
                
        finally:
            # Clean up temporary file
            try:
                Path(tmp_path).unlink()
            except FileNotFoundError:
                pass
    
    def _play_with_pyaudio(self, audio_data: np.ndarray, sample_rate: int):
        """Play audio using pyaudio backend."""
        # Ensure audio data is in the right format
        if audio_data.dtype != np.float32:
            if audio_data.dtype == np.int16:
                audio_data = audio_data.astype(np.float32) / 32767.0
            else:
                audio_data = audio_data.astype(np.float32)
        
        # Determine number of channels
        channels = 1 if len(audio_data.shape) == 1 else audio_data.shape[1]
        
        # Open stream
        stream = self.pa.open(
            format=pyaudio.paFloat32,
            channels=channels,
            rate=sample_rate,
            output=True,
            frames_per_buffer=1024
        )
        
        try:
            # Play audio in chunks
            chunk_size = 1024
            for i in range(0, len(audio_data), chunk_size):
                if not self.is_playing:
                    break
                chunk = audio_data[i:i + chunk_size]
                stream.write(chunk.tobytes())
        finally:
            stream.stop_stream()
            stream.close()
    
    def _play_with_system(self, audio_data: np.ndarray, sample_rate: int, 
                         header_data: Optional[np.ndarray]):
        """Play audio using system default player."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            # Save to temporary file
            sf.write(tmp_path, audio_data, sample_rate)
            
            # Play with system default
            import subprocess
            import sys
            
            if sys.platform.startswith('darwin'):  # macOS
                subprocess.run(['afplay', tmp_path], check=True)
            elif sys.platform.startswith('win'):  # Windows
                subprocess.run(['start', tmp_path], shell=True, check=True)
            else:  # Linux
                subprocess.run(['aplay', tmp_path], check=True)
                
        except subprocess.CalledProcessError as e:
            print(f"Error playing audio with system player: {e}")
        except FileNotFoundError:
            print("System audio player not found")
        finally:
            # Clean up temporary file
            try:
                Path(tmp_path).unlink()
            except FileNotFoundError:
                pass
    
    def play_file(self, file_path: Union[str, Path], blocking: bool = False):
        """
        Play an audio file.
        
        Args:
            file_path: Path to the audio file
            blocking: Whether to block until playback finishes
        """
        try:
            audio_data, sample_rate = sf.read(str(file_path))
            self.play_audio_data(audio_data, sample_rate, blocking=blocking)
        except Exception as e:
            print(f"Error playing file {file_path}: {e}")
    
    def stop(self):
        """Stop audio playback."""
        self.is_playing = False
        
        if self.backend == "pygame" and PYGAME_AVAILABLE:
            pygame.mixer.music.stop()
        
        # Wait for thread to finish
        if self.current_thread and self.current_thread.is_alive():
            self.current_thread.join(timeout=1.0)
    
    def is_playing_audio(self) -> bool:
        """Check if audio is currently playing."""
        return self.is_playing
    
    def get_available_backends(self) -> list:
        """Get list of available audio backends."""
        backends = ["system"]
        if PYGAME_AVAILABLE:
            backends.append("pygame")
        if PYAUDIO_AVAILABLE:
            backends.append("pyaudio")
        return backends
    
    def cleanup(self):
        """Clean up audio resources."""
        self.stop()
        
        if self.backend == "pyaudio" and PYAUDIO_AVAILABLE and hasattr(self, 'pa'):
            self.pa.terminate()
        elif self.backend == "pygame" and PYGAME_AVAILABLE:
            pygame.mixer.quit()
    
    def __del__(self):
        """Destructor to clean up resources."""
        try:
            self.cleanup()
        except:
            pass


class ChromosomePlayer(AudioPlayer):
    """
    Specialized audio player for AudioChromosome objects.
    """
    
    def play_chromosome(self, chromosome, sample_rate: int = 44100, 
                       header_data: Optional[np.ndarray] = None, blocking: bool = False):
        """
        Play an AudioChromosome.
        
        Args:
            chromosome: AudioChromosome to play
            sample_rate: Sample rate in Hz
            header_data: Optional WAV header data
            blocking: Whether to block until playback finishes
        """
        self.play_audio_data(chromosome.dna, sample_rate, header_data, blocking)
    
    def compare_chromosomes(self, original, evolved, sample_rate: int = 44100,
                          pause_duration: float = 1.0):
        """
        Play two chromosomes in sequence for comparison.
        
        Args:
            original: Original AudioChromosome
            evolved: Evolved AudioChromosome
            sample_rate: Sample rate in Hz
            pause_duration: Pause between playbacks in seconds
        """
        print("Playing original...")
        self.play_chromosome(original, sample_rate, blocking=True)
        
        time.sleep(pause_duration)
        
        print("Playing evolved...")
        self.play_chromosome(evolved, sample_rate, blocking=True)
    
    def play_evolution_sequence(self, chromosomes: list, sample_rate: int = 44100,
                              pause_duration: float = 0.5):
        """
        Play a sequence of chromosomes showing evolution progress.
        
        Args:
            chromosomes: List of AudioChromosomes in evolution order
            sample_rate: Sample rate in Hz
            pause_duration: Pause between playbacks in seconds
        """
        for i, chromosome in enumerate(chromosomes):
            print(f"Playing generation {i + 1} (fitness: {chromosome.fitness:.2f}%)...")
            self.play_chromosome(chromosome, sample_rate, blocking=True)
            
            if i < len(chromosomes) - 1:  # Don't pause after the last one
                time.sleep(pause_duration)