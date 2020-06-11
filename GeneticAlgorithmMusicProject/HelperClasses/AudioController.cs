using NAudio.Wave;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace GeneticAlgorithmMusicProject.HelperClasses
{
    public class AudioController
    {
        public WaveOutEvent PlaybackWaveOutEvent { get; set; }
        public MediaFoundationReader MediaPlayer { get; set; }


        public AudioController(string chosenFilePath)
        {
            //Dispose any audio previously loaded so multiple uses can be done

            PlaybackWaveOutEvent = new WaveOutEvent();
            MediaPlayer = new MediaFoundationReader(chosenFilePath);
            PlaybackWaveOutEvent.Init(MediaPlayer);
        }


        public void PlayAudio()
        {
            PlaybackWaveOutEvent.Play();
            PlaybackWaveOutEvent.PlaybackStopped += OnPlaybackStopped;
        }

        private void OnPlaybackStopped(object sender, EventArgs e)
        {
            //Reset position to the begining of the sound file since it has stopped
            MediaPlayer.CurrentTime = TimeSpan.FromSeconds(0);
        }

        //Change below to milliseconds
        public int GetSongLengthInMilliseconds()
        {
            if (MediaPlayer != null)
            {
                return Convert.ToInt32(MediaPlayer.TotalTime.TotalMilliseconds);
            }

            return 0;
        }

        public void PauseAudio()
        {
            PlaybackWaveOutEvent.Pause();
        }

        public void StopAudio()
        {
            PlaybackWaveOutEvent.Stop();
        }

        public void RepositionAudioTime(int seconds)
        {
            MediaPlayer.CurrentTime = TimeSpan.FromSeconds(seconds);
        }


        public void DisposeAudio()
        {
            //All audio control cleanup should be done here 
            PlaybackWaveOutEvent.Dispose();
            MediaPlayer.Dispose();
        }




    }
}
