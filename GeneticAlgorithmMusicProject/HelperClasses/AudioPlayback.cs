using NAudio.Wave;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.IO;

namespace GeneticAlgorithmMusicProject.HelperClasses
{
    class AudioPlayback : IDisposable
    {
        private IWavePlayer playbackDevice;
        private WaveStream fileStream;
        private bool disposed = false;

        public event EventHandler<FftEventArgs> FftCalculated;
        public event EventHandler<MaxSampleEventArgs> MaximumCalculated;
        public event EventHandler<string> ErrorOccurred;

        public void Load(string fileName)
        {
            if (string.IsNullOrWhiteSpace(fileName))
            {
                OnErrorOccurred("File name cannot be null or empty.");
                return;
            }

            if (!File.Exists(fileName))
            {
                OnErrorOccurred($"File not found: {fileName}");
                return;
            }

            try
            {
                Stop();
                CloseFile();
                EnsureDeviceCreated();
                OpenFile(fileName);
            }
            catch (Exception ex)
            {
                OnErrorOccurred($"Failed to load audio file: {ex.Message}");
                CloseFile();
            }
        }

        private void CloseFile()
        {
            try
            {
                fileStream?.Dispose();
                fileStream = null;
            }
            catch (Exception ex)
            {
                OnErrorOccurred($"Error closing audio file: {ex.Message}");
            }
        }

        private void OpenFile(string fileName)
        {
            try
            {
                var inputStream = new AudioFileReader(fileName);
                fileStream = inputStream;
                var aggregator = new SampleAggregator(inputStream);
                aggregator.NotificationCount = inputStream.WaveFormat.SampleRate / GeneticAlgorithmConfig.DEFAULT_NOTIFICATION_COUNT_DIVISOR;
                aggregator.PerformFFT = true;
                aggregator.FftCalculated += (s, a) => FftCalculated?.Invoke(this, a);
                aggregator.MaximumCalculated += (s, a) => MaximumCalculated?.Invoke(this, a);
                
                if (playbackDevice == null)
                {
                    throw new InvalidOperationException("Playback device is not initialized.");
                }
                
                playbackDevice.Init(aggregator);
            }
            catch (Exception ex)
            {
                OnErrorOccurred($"Problem opening file '{fileName}': {ex.Message}");
                CloseFile();
                throw;
            }
        }

        private void EnsureDeviceCreated()
        {
            if (playbackDevice == null)
            {
                CreateDevice();
            }
        }

        private void CreateDevice()
        {
            try
            {
                playbackDevice = new WaveOut { DesiredLatency = GeneticAlgorithmConfig.DEFAULT_DESIRED_LATENCY };
            }
            catch (Exception ex)
            {
                OnErrorOccurred($"Failed to create audio device: {ex.Message}");
                throw;
            }
        }

        public void Play()
        {
            try
            {
                if (playbackDevice == null)
                {
                    OnErrorOccurred("Playback device is not initialized.");
                    return;
                }

                if (fileStream == null)
                {
                    OnErrorOccurred("No audio file is loaded.");
                    return;
                }

                if (playbackDevice.PlaybackState != PlaybackState.Playing)
                {
                    playbackDevice.Play();
                }
            }
            catch (Exception ex)
            {
                OnErrorOccurred($"Failed to play audio: {ex.Message}");
            }
        }

        public void Pause()
        {
            try
            {
                if (playbackDevice?.PlaybackState == PlaybackState.Playing)
                {
                    playbackDevice.Pause();
                }
            }
            catch (Exception ex)
            {
                OnErrorOccurred($"Failed to pause audio: {ex.Message}");
            }
        }

        public void Stop()
        {
            try
            {
                playbackDevice?.Stop();
                if (fileStream != null)
                {
                    fileStream.Position = 0;
                }
            }
            catch (Exception ex)
            {
                OnErrorOccurred($"Failed to stop audio: {ex.Message}");
            }
        }

        private void OnErrorOccurred(string errorMessage)
        {
            ErrorOccurred?.Invoke(this, errorMessage);
        }

        public void Dispose()
        {
            Dispose(true);
            GC.SuppressFinalize(this);
        }

        protected virtual void Dispose(bool disposing)
        {
            if (!disposed)
            {
                if (disposing)
                {
                    try
                    {
                        Stop();
                        CloseFile();
                        playbackDevice?.Dispose();
                        playbackDevice = null;
                    }
                    catch (Exception ex)
                    {
                        OnErrorOccurred($"Error during disposal: {ex.Message}");
                    }
                }
                disposed = true;
            }
        }
    }
}
