"""
Audio Analyzer

Provides audio analysis capabilities for the genetic algorithm music project.
"""

import numpy as np
import scipy.signal
import scipy.fft
from typing import Dict, List, Tuple, Optional
import librosa


class AudioAnalyzer:
    """
    Audio analysis tools for genetic algorithm fitness evaluation and insights.
    """
    
    def __init__(self, sample_rate: int = 44100):
        """
        Initialize the audio analyzer.
        
        Args:
            sample_rate: Audio sample rate in Hz
        """
        self.sample_rate = sample_rate
    
    def analyze_audio(self, audio_data: np.ndarray) -> Dict[str, float]:
        """
        Perform comprehensive audio analysis.
        
        Args:
            audio_data: Audio data as numpy array
            
        Returns:
            Dictionary with analysis results
        """
        results = {}
        
        # Basic statistics
        results.update(self.basic_statistics(audio_data))
        
        # Frequency analysis
        results.update(self.frequency_analysis(audio_data))
        
        # Temporal analysis
        results.update(self.temporal_analysis(audio_data))
        
        # Spectral features
        results.update(self.spectral_features(audio_data))
        
        # Perceptual features
        results.update(self.perceptual_features(audio_data))
        
        return results
    
    def basic_statistics(self, audio_data: np.ndarray) -> Dict[str, float]:
        """
        Calculate basic statistical measures of audio data.
        
        Args:
            audio_data: Audio data as numpy array
            
        Returns:
            Dictionary with basic statistics
        """
        return {
            "mean": float(np.mean(audio_data)),
            "std": float(np.std(audio_data)),
            "rms": float(np.sqrt(np.mean(audio_data**2))),
            "max_amplitude": float(np.max(np.abs(audio_data))),
            "dynamic_range": float(np.max(audio_data) - np.min(audio_data)),
            "zero_crossing_rate": float(self._zero_crossing_rate(audio_data)),
            "energy": float(np.sum(audio_data**2)),
            "length_seconds": float(len(audio_data) / self.sample_rate)
        }
    
    def frequency_analysis(self, audio_data: np.ndarray) -> Dict[str, float]:
        """
        Analyze frequency domain characteristics.
        
        Args:
            audio_data: Audio data as numpy array
            
        Returns:
            Dictionary with frequency analysis results
        """
        # Compute FFT
        fft = scipy.fft.fft(audio_data)
        frequencies = scipy.fft.fftfreq(len(audio_data), 1/self.sample_rate)
        magnitude = np.abs(fft)
        
        # Only consider positive frequencies
        positive_freq_mask = frequencies >= 0
        frequencies = frequencies[positive_freq_mask]
        magnitude = magnitude[positive_freq_mask]
        
        # Find dominant frequency
        dominant_freq_idx = np.argmax(magnitude)
        dominant_frequency = frequencies[dominant_freq_idx]
        
        # Calculate spectral centroid
        spectral_centroid = np.sum(frequencies * magnitude) / np.sum(magnitude)
        
        # Calculate spectral bandwidth
        spectral_bandwidth = np.sqrt(
            np.sum(((frequencies - spectral_centroid) ** 2) * magnitude) / np.sum(magnitude)
        )
        
        # Calculate spectral rolloff (95% of energy)
        cumulative_magnitude = np.cumsum(magnitude)
        total_energy = cumulative_magnitude[-1]
        rolloff_threshold = 0.95 * total_energy
        rolloff_idx = np.where(cumulative_magnitude >= rolloff_threshold)[0]
        spectral_rolloff = frequencies[rolloff_idx[0]] if len(rolloff_idx) > 0 else frequencies[-1]
        
        return {
            "dominant_frequency": float(dominant_frequency),
            "spectral_centroid": float(spectral_centroid),
            "spectral_bandwidth": float(spectral_bandwidth),
            "spectral_rolloff": float(spectral_rolloff),
            "frequency_range": float(frequencies[-1] - frequencies[0]),
            "high_frequency_energy": float(np.sum(magnitude[frequencies > 4000]) / np.sum(magnitude)),
            "low_frequency_energy": float(np.sum(magnitude[frequencies < 200]) / np.sum(magnitude))
        }
    
    def temporal_analysis(self, audio_data: np.ndarray) -> Dict[str, float]:
        """
        Analyze temporal characteristics of audio.
        
        Args:
            audio_data: Audio data as numpy array
            
        Returns:
            Dictionary with temporal analysis results
        """
        # Calculate envelope
        envelope = np.abs(scipy.signal.hilbert(audio_data))
        
        # Attack time (time to reach 90% of max amplitude)
        max_envelope = np.max(envelope)
        attack_threshold = 0.9 * max_envelope
        attack_indices = np.where(envelope >= attack_threshold)[0]
        attack_time = attack_indices[0] / self.sample_rate if len(attack_indices) > 0 else 0
        
        # Decay characteristics
        decay_start_idx = np.argmax(envelope)
        if decay_start_idx < len(envelope) - 1:
            decay_envelope = envelope[decay_start_idx:]
            decay_rate = -np.polyfit(range(len(decay_envelope)), np.log(decay_envelope + 1e-10), 1)[0]
        else:
            decay_rate = 0
        
        # Temporal variations
        envelope_diff = np.diff(envelope)
        temporal_variation = np.std(envelope_diff)
        
        return {
            "attack_time": float(attack_time),
            "decay_rate": float(decay_rate),
            "temporal_variation": float(temporal_variation),
            "envelope_max": float(max_envelope),
            "envelope_mean": float(np.mean(envelope)),
            "onset_strength": float(np.max(np.diff(envelope)))
        }
    
    def spectral_features(self, audio_data: np.ndarray) -> Dict[str, float]:
        """
        Calculate advanced spectral features using librosa.
        
        Args:
            audio_data: Audio data as numpy array
            
        Returns:
            Dictionary with spectral features
        """
        try:
            # Calculate MFCC features
            mfcc = librosa.feature.mfcc(y=audio_data, sr=self.sample_rate, n_mfcc=13)
            mfcc_mean = np.mean(mfcc, axis=1)
            mfcc_std = np.std(mfcc, axis=1)
            
            # Calculate spectral contrast
            spectral_contrast = librosa.feature.spectral_contrast(y=audio_data, sr=self.sample_rate)
            
            # Calculate chroma features
            chroma = librosa.feature.chroma_stft(y=audio_data, sr=self.sample_rate)
            
            # Calculate spectral features
            spectral_centroid = librosa.feature.spectral_centroid(y=audio_data, sr=self.sample_rate)
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio_data, sr=self.sample_rate)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=self.sample_rate)
            
            features = {
                "mfcc_mean_0": float(mfcc_mean[0]),
                "mfcc_mean_1": float(mfcc_mean[1]),
                "mfcc_mean_2": float(mfcc_mean[2]),
                "mfcc_std_0": float(mfcc_std[0]),
                "mfcc_std_1": float(mfcc_std[1]),
                "mfcc_std_2": float(mfcc_std[2]),
                "spectral_contrast_mean": float(np.mean(spectral_contrast)),
                "spectral_contrast_std": float(np.std(spectral_contrast)),
                "chroma_mean": float(np.mean(chroma)),
                "chroma_std": float(np.std(chroma)),
                "librosa_spectral_centroid": float(np.mean(spectral_centroid)),
                "librosa_spectral_bandwidth": float(np.mean(spectral_bandwidth)),
                "librosa_spectral_rolloff": float(np.mean(spectral_rolloff))
            }
            
        except Exception as e:
            print(f"Warning: Advanced spectral features calculation failed: {e}")
            features = {
                "mfcc_mean_0": 0.0,
                "mfcc_mean_1": 0.0,
                "mfcc_mean_2": 0.0,
                "mfcc_std_0": 0.0,
                "mfcc_std_1": 0.0,
                "mfcc_std_2": 0.0,
                "spectral_contrast_mean": 0.0,
                "spectral_contrast_std": 0.0,
                "chroma_mean": 0.0,
                "chroma_std": 0.0,
                "librosa_spectral_centroid": 0.0,
                "librosa_spectral_bandwidth": 0.0,
                "librosa_spectral_rolloff": 0.0
            }
        
        return features
    
    def perceptual_features(self, audio_data: np.ndarray) -> Dict[str, float]:
        """
        Calculate perceptual audio features.
        
        Args:
            audio_data: Audio data as numpy array
            
        Returns:
            Dictionary with perceptual features
        """
        # Loudness estimation (simple RMS-based)
        loudness = 20 * np.log10(np.sqrt(np.mean(audio_data**2)) + 1e-10)
        
        # Roughness estimation (based on amplitude modulation)
        envelope = np.abs(scipy.signal.hilbert(audio_data))
        envelope_smooth = scipy.signal.savgol_filter(envelope, window_length=101, polyorder=3)
        roughness = np.std(envelope - envelope_smooth)
        
        # Brightness (high-frequency content)
        fft = scipy.fft.fft(audio_data)
        frequencies = scipy.fft.fftfreq(len(audio_data), 1/self.sample_rate)
        magnitude = np.abs(fft)
        
        positive_freq_mask = frequencies >= 0
        frequencies = frequencies[positive_freq_mask]
        magnitude = magnitude[positive_freq_mask]
        
        high_freq_mask = frequencies > 2000
        brightness = np.sum(magnitude[high_freq_mask]) / np.sum(magnitude) if np.sum(magnitude) > 0 else 0
        
        # Harmonicity (ratio of harmonic to inharmonic content)
        harmonicity = self._calculate_harmonicity(audio_data)
        
        return {
            "loudness_db": float(loudness),
            "roughness": float(roughness),
            "brightness": float(brightness),
            "harmonicity": float(harmonicity),
            "perceived_pitch": float(self._estimate_pitch(audio_data))
        }
    
    def compare_audio(self, audio1: np.ndarray, audio2: np.ndarray) -> Dict[str, float]:
        """
        Compare two audio signals and return similarity metrics.
        
        Args:
            audio1: First audio signal
            audio2: Second audio signal
            
        Returns:
            Dictionary with comparison metrics
        """
        # Ensure same length
        min_len = min(len(audio1), len(audio2))
        audio1 = audio1[:min_len]
        audio2 = audio2[:min_len]
        
        # Cross-correlation
        correlation = np.corrcoef(audio1, audio2)[0, 1]
        if np.isnan(correlation):
            correlation = 0.0
        
        # Mean squared error
        mse = np.mean((audio1 - audio2) ** 2)
        
        # Signal-to-noise ratio
        signal_power = np.mean(audio1 ** 2)
        noise_power = np.mean((audio1 - audio2) ** 2)
        snr = 10 * np.log10(signal_power / (noise_power + 1e-10))
        
        # Spectral similarity
        fft1 = np.abs(scipy.fft.fft(audio1))
        fft2 = np.abs(scipy.fft.fft(audio2))
        spectral_correlation = np.corrcoef(fft1, fft2)[0, 1]
        if np.isnan(spectral_correlation):
            spectral_correlation = 0.0
        
        return {
            "correlation": float(correlation),
            "mse": float(mse),
            "snr_db": float(snr),
            "spectral_correlation": float(spectral_correlation),
            "similarity_score": float((abs(correlation) + abs(spectral_correlation)) / 2)
        }
    
    def _zero_crossing_rate(self, audio_data: np.ndarray) -> float:
        """Calculate zero crossing rate."""
        signs = np.sign(audio_data)
        zero_crossings = np.sum(np.abs(np.diff(signs))) / 2
        return zero_crossings / len(audio_data)
    
    def _calculate_harmonicity(self, audio_data: np.ndarray) -> float:
        """
        Estimate harmonicity of audio signal.
        
        Args:
            audio_data: Audio data as numpy array
            
        Returns:
            Harmonicity measure (0-1, higher is more harmonic)
        """
        try:
            # Use autocorrelation to find fundamental frequency
            autocorr = np.correlate(audio_data, audio_data, mode='full')
            autocorr = autocorr[autocorr.size // 2:]
            
            # Find peaks in autocorrelation
            peaks, _ = scipy.signal.find_peaks(autocorr, height=0.1 * np.max(autocorr))
            
            if len(peaks) < 2:
                return 0.0
            
            # Calculate harmonic ratios
            fundamental_period = peaks[0]
            harmonic_strength = 0.0
            
            for i, peak in enumerate(peaks[1:6]):  # Check first 5 harmonics
                expected_harmonic = fundamental_period * (i + 2)
                actual_harmonic = peak
                
                # Check if peak is close to expected harmonic
                if abs(actual_harmonic - expected_harmonic) / expected_harmonic < 0.1:
                    harmonic_strength += autocorr[peak] / autocorr[fundamental_period]
            
            return min(harmonic_strength / 5, 1.0)  # Normalize to 0-1
            
        except Exception:
            return 0.0
    
    def _estimate_pitch(self, audio_data: np.ndarray) -> float:
        """
        Estimate fundamental frequency (pitch) of audio signal.
        
        Args:
            audio_data: Audio data as numpy array
            
        Returns:
            Estimated pitch in Hz
        """
        try:
            # Use autocorrelation method
            autocorr = np.correlate(audio_data, audio_data, mode='full')
            autocorr = autocorr[autocorr.size // 2:]
            
            # Find the first peak after the initial peak
            peaks, _ = scipy.signal.find_peaks(autocorr[1:], height=0.1 * np.max(autocorr))
            
            if len(peaks) > 0:
                fundamental_period = peaks[0] + 1  # +1 because we started from index 1
                pitch = self.sample_rate / fundamental_period
                return min(pitch, self.sample_rate / 2)  # Cap at Nyquist frequency
            else:
                return 0.0
                
        except Exception:
            return 0.0
    
    def generate_report(self, audio_data: np.ndarray) -> str:
        """
        Generate a comprehensive analysis report.
        
        Args:
            audio_data: Audio data as numpy array
            
        Returns:
            Formatted analysis report as string
        """
        analysis = self.analyze_audio(audio_data)
        
        report = f"""
Audio Analysis Report
====================

Basic Statistics:
- Duration: {analysis['length_seconds']:.2f} seconds
- RMS Level: {analysis['rms']:.4f}
- Dynamic Range: {analysis['dynamic_range']:.4f}
- Zero Crossing Rate: {analysis['zero_crossing_rate']:.4f}

Frequency Analysis:
- Dominant Frequency: {analysis['dominant_frequency']:.1f} Hz
- Spectral Centroid: {analysis['spectral_centroid']:.1f} Hz
- Spectral Bandwidth: {analysis['spectral_bandwidth']:.1f} Hz
- Spectral Rolloff: {analysis['spectral_rolloff']:.1f} Hz

Temporal Features:
- Attack Time: {analysis['attack_time']:.3f} seconds
- Decay Rate: {analysis['decay_rate']:.3f}
- Temporal Variation: {analysis['temporal_variation']:.4f}

Perceptual Features:
- Loudness: {analysis['loudness_db']:.1f} dB
- Brightness: {analysis['brightness']:.3f}
- Harmonicity: {analysis['harmonicity']:.3f}
- Estimated Pitch: {analysis['perceived_pitch']:.1f} Hz

Spectral Features:
- MFCC[0]: {analysis['mfcc_mean_0']:.2f} ± {analysis['mfcc_std_0']:.2f}
- MFCC[1]: {analysis['mfcc_mean_1']:.2f} ± {analysis['mfcc_std_1']:.2f}
- MFCC[2]: {analysis['mfcc_mean_2']:.2f} ± {analysis['mfcc_std_2']:.2f}
- Spectral Contrast: {analysis['spectral_contrast_mean']:.2f} ± {analysis['spectral_contrast_std']:.2f}
- Chroma: {analysis['chroma_mean']:.2f} ± {analysis['chroma_std']:.2f}
"""
        
        return report