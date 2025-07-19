using NAudio.Wave;
using System.IO;

namespace GeneticAlgorithmMusicProject.HelperClasses
{
    public class AudioController : IDisposable
    {
        public WaveOutEvent PlaybackWaveOutEvent { get; private set; }
        public MediaFoundationReader MediaPlayer { get; private set; }
        private bool disposed = false;

        public event EventHandler<string> ErrorOccurred;

        public AudioController(string chosenFilePath)
        {
            if (string.IsNullOrWhiteSpace(chosenFilePath))
            {
                throw new ArgumentException("File path cannot be null or empty.", nameof(chosenFilePath));
            }

            if (!File.Exists(chosenFilePath))
            {
                throw new FileNotFoundException($"Audio file not found: {chosenFilePath}", chosenFilePath);
            }

            try
            {
                InitializeAudio(chosenFilePath);
            }
            catch (Exception ex)
            {
                OnErrorOccurred($"Failed to initialize audio controller: {ex.Message}");
                DisposeResources();
                throw;
            }
        }

        private void InitializeAudio(string filePath)
        {
            try
            {
                // Dispose any audio previously loaded so multiple uses can be done
                DisposeResources();

                PlaybackWaveOutEvent = new WaveOutEvent();
                MediaPlayer = new MediaFoundationReader(filePath);
                PlaybackWaveOutEvent.Init(MediaPlayer);
            }
            catch (Exception ex)
            {
                OnErrorOccurred($"Failed to initialize audio for file '{filePath}': {ex.Message}");
                throw;
            }
        }

        public void PlayAudio()
        {
            try
            {
                if (PlaybackWaveOutEvent == null)
                {
                    OnErrorOccurred("Audio playback device is not initialized.");
                    return;
                }

                if (MediaPlayer == null)
                {
                    OnErrorOccurred("No audio file is loaded.");
                    return;
                }

                PlaybackWaveOutEvent.Play();
                PlaybackWaveOutEvent.PlaybackStopped += OnPlaybackStopped;
            }
            catch (Exception ex)
            {
                OnErrorOccurred($"Failed to play audio: {ex.Message}");
            }
        }

        private void OnPlaybackStopped(object sender, EventArgs e)
        {
            try
            {
                // Reset position to the beginning of the sound file since it has stopped
                if (MediaPlayer != null)
                {
                    MediaPlayer.CurrentTime = TimeSpan.FromSeconds(0);
                }
            }
            catch (Exception ex)
            {
                OnErrorOccurred($"Failed to reset audio position: {ex.Message}");
            }
        }

        /// <summary>
        /// Gets the song length in milliseconds.
        /// </summary>
        /// <returns>Song length in milliseconds, or 0 if no media is loaded.</returns>
        public int GetSongLengthInMilliseconds()
        {
            try
            {
                if (MediaPlayer?.TotalTime != null)
                {
                    return Convert.ToInt32(MediaPlayer.TotalTime.TotalMilliseconds);
                }
            }
            catch (Exception ex)
            {
                OnErrorOccurred($"Failed to get song length: {ex.Message}");
            }

            return 0;
        }

        public void PauseAudio()
        {
            try
            {
                if (PlaybackWaveOutEvent?.PlaybackState == PlaybackState.Playing)
                {
                    PlaybackWaveOutEvent.Pause();
                }
            }
            catch (Exception ex)
            {
                OnErrorOccurred($"Failed to pause audio: {ex.Message}");
            }
        }

        public void StopAudio()
        {
            try
            {
                PlaybackWaveOutEvent?.Stop();
            }
            catch (Exception ex)
            {
                OnErrorOccurred($"Failed to stop audio: {ex.Message}");
            }
        }

        public void RepositionAudioTime(int seconds)
        {
            if (seconds < 0)
            {
                OnErrorOccurred("Audio position cannot be negative.");
                return;
            }

            try
            {
                if (MediaPlayer != null)
                {
                    var newPosition = TimeSpan.FromSeconds(seconds);
                    if (newPosition <= MediaPlayer.TotalTime)
                    {
                        MediaPlayer.CurrentTime = newPosition;
                    }
                    else
                    {
                        OnErrorOccurred($"Position {seconds} seconds exceeds audio duration.");
                    }
                }
                else
                {
                    OnErrorOccurred("No audio file is loaded.");
                }
            }
            catch (Exception ex)
            {
                OnErrorOccurred($"Failed to reposition audio: {ex.Message}");
            }
        }

        private void OnErrorOccurred(string errorMessage)
        {
            ErrorOccurred?.Invoke(this, errorMessage);
        }

        public void DisposeAudio()
        {
            Dispose();
        }

        private void DisposeResources()
        {
            try
            {
                // All audio control cleanup should be done here 
                if (PlaybackWaveOutEvent != null)
                {
                    PlaybackWaveOutEvent.PlaybackStopped -= OnPlaybackStopped;
                    PlaybackWaveOutEvent.Dispose();
                    PlaybackWaveOutEvent = null;
                }

                MediaPlayer?.Dispose();
                MediaPlayer = null;
            }
            catch (Exception ex)
            {
                OnErrorOccurred($"Error during resource disposal: {ex.Message}");
            }
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
                    DisposeResources();
                }
                disposed = true;
            }
        }
    }
}
