using GeneticAlgorithmMusicProject.Commands;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Input;
using Microsoft.WindowsAPICodePack.Dialogs;
using System.IO;
using System.ComponentModel;
using GeneticAlgorithmMusicProject.Simulator;
using System.Threading;
using System.Windows.Threading;
using GeneticAlgorithmMusicProject.HelperClasses;
using System.Windows.Controls;
using GeneticAlgorithmMusicProject.Views;

namespace GeneticAlgorithmMusicProject.ViewModels
{
    public class MainViewModel : INotifyPropertyChanged
    {
        DispatcherTimer runTimer;
        DateTime startTime;

        private readonly AudioPlayback audioPlayback;
        private readonly List<IVisualizationPlugin> visualizations;
        private IVisualizationPlugin selectedVisualization;

        private UserControl _userInterface;
        public UserControl UserInterface
        {
            get
            {
                return _userInterface;
            }
            set
            {
                _userInterface = value;
                NotifyPropertyChanged(nameof(UserInterface));
            }

        }
        private IModule selectedModule;


        public IModule SelectedModule
        {
            get
            {
                return selectedModule;
            }
            set
            {
                if (value != selectedModule)
                {
                    selectedModule?.Deactivate();
                    selectedModule = value;
                    NotifyPropertyChanged("SelectedModule");
                    NotifyPropertyChanged("UserInterface");
                }
            }
        }

        public List<IModule> Modules { get; }


        public MainViewModel()
        {

            UserInterface = new PolygonWaveFormControl();
            //Always using polygon wave form to display
            this.visualizations = new List<IVisualizationPlugin>() { new PolygonWaveFormVisualization()};
            this.selectedVisualization = this.visualizations.FirstOrDefault();

            this.audioPlayback = new AudioPlayback();
            audioPlayback.MaximumCalculated += audioGraph_MaximumCalculated;
            audioPlayback.FftCalculated += audioGraph_FftCalculated;



            SelectedIndex = 0;
            CurrentSimFileName = "No file is selected";
            //CurrentGenoration = "No simulation is currently running";
            OpenFolderCommand = new RelayButtonCommand(o => LoadPreviousSim());
            LoadSoundFile = new RelayButtonCommand(o => LoadSoundFileForSimulation());
            RunSimulation = new RelayButtonCommand(o => RunGeneticSimulation());

            //PlayAudioCommand = new RelayButtonCommand(o => PlaySelectedAudioFile());
            PlayAudioCommand = new RelayButtonCommand(o => PlaySelectedAudioFile());

            PauseAudioCommand = new RelayButtonCommand(o => PauseSelectedAudioFile());
            NextFileCommand = new RelayButtonCommand(o => NextAudioFile());
            PreviousFileCommand = new RelayButtonCommand(o => PreviousAudioFile());
            StopAudioCommand = new RelayButtonCommand(o => StopSelectedAudioFile());

            GenerationNameDisplay = "";
        }



        public void StopSelectedAudioFile()
        {
            //Stop the selected audio file from playing

            //if(AudioControl != null)
            //{
            //    AudioControl.StopAudio();
            //}

            if(audioPlayback != null)
            {
                audioPlayback.Stop();
            }


        }


        void audioGraph_FftCalculated(object sender, FftEventArgs e)
        {
            if (this.SelectedVisualization != null)
            {
                this.SelectedVisualization.OnFftCalculated(e.Result);
            }
        }



        void audioGraph_MaximumCalculated(object sender, MaxSampleEventArgs e)
        {
            if (this.SelectedVisualization != null)
            {
                this.SelectedVisualization.OnMaxCalculated(e.MinSample, e.MaxSample);
            }
        }


        public IVisualizationPlugin SelectedVisualization
        {
            get
            {
                return this.selectedVisualization;
            }
            set
            {
                if (this.selectedVisualization != value)
                {
                    this.selectedVisualization = value;
                    NotifyPropertyChanged(nameof(SelectedVisualization));
                    NotifyPropertyChanged(nameof(Visualization));
                }
            }
        }


        public object Visualization
        {
            get
            {
                return this.selectedVisualization.Content;
            }
        }

        public void NextAudioFile()
        {
            //Move to next audio file in selected folder
            //Since the audio file is changing the controller will need to be remade

            SelectedPreviousSimSoundFileIndex++;


            if (SelectedPreviousSimSoundFileIndex <= PreviousSimSoundFiles.Length -1)
            {
                SelectedPreviousSimSoundFile = PreviousSimSoundFiles[SelectedPreviousSimSoundFileIndex];
            }
            else
            {
                SelectedPreviousSimSoundFileIndex = 0;
                SelectedPreviousSimSoundFile = PreviousSimSoundFiles[SelectedPreviousSimSoundFileIndex];
            }

            //Reload the Audio controller since we have most likely changed sound file
            SetAudioController(SelectedPreviousSimSoundFile);
            audioPlayback.Load(SelectedPreviousSimSoundFile);


        }

        public void PreviousAudioFile()
        {
            //Move to next audio file in selected folder
            //Since the audio file is changing the controller will need to be remade

            SelectedPreviousSimSoundFileIndex--;


            if (SelectedPreviousSimSoundFileIndex >= 0)
            {
                SelectedPreviousSimSoundFile = PreviousSimSoundFiles[SelectedPreviousSimSoundFileIndex];
            }
            else
            {
                SelectedPreviousSimSoundFileIndex = PreviousSimSoundFiles.Length - 1;
                SelectedPreviousSimSoundFile = PreviousSimSoundFiles[SelectedPreviousSimSoundFileIndex];
            }

            //Reload the Audio controller since we have most likely changed sound file
            SetAudioController(SelectedPreviousSimSoundFile);
            audioPlayback.Load(SelectedPreviousSimSoundFile);

        }


        public void PauseSelectedAudioFile()
        {
            //Pause selected audio file

            //if(AudioControl != null)
            //{
            //    AudioControl.PauseAudio();
            //}

            if(audioPlayback != null)
            {
                audioPlayback.Pause();
            }


        }

        public void PlaySelectedAudioFile()
        {
            //Play selected audio file

            //if(AudioControl != null)
            //{
            //    AudioControl.PlayAudio();
            //}

            //Trying new method 

            audioPlayback.Play();

        }

        public void UpdateCurrentSimulationStats(string currentGenoration, string lastGenUpdated,
            string currentFitness)
        {
            //Update CurrentGenoration, LastGenorationUpdated, CurrentFitness, TimeRunning
            CurrentGenoration = "Current Generation: " + currentGenoration;
            LastGenorationUpdated = "Last Updated: " + lastGenUpdated;
            CurrentFitness = "Current Fitness: " + currentFitness;
            //TimeRunning = timeRunning;
        }


        public AudioController AudioControl;


        //Records the current tab index
        private int _selectedIndex = 0;
        public int SelectedIndex
        {
            get
            {
                return _selectedIndex;
            }
            set
            {
                _selectedIndex = value;
                NotifyPropertyChanged(nameof(SelectedIndex));

            }
        }



        private string _currentSimFileName;
        public string CurrentSimFileName
        {
            get
            {
                return _currentSimFileName;
            }
            set
            {
                _currentSimFileName = value;
                NotifyPropertyChanged(nameof(CurrentSimFileName));
            }
        }



        private bool _loadResultsBorderVis;
        public bool LoadResultsBorderVis
        {
            get
            {
                return _loadResultsBorderVis;
            }
            set
            {
                _loadResultsBorderVis = value;
                NotifyPropertyChanged(nameof(LoadResultsBorderVis));
            }
        }

        private string _soundFilePathForSimulation;
        public string SoundFilePathForSimulation
        {
            get
            {
                return _soundFilePathForSimulation;
            }
            set
            {
                _soundFilePathForSimulation = value;
                NotifyPropertyChanged(nameof(SoundFilePathForSimulation));
            }
        }

        //Current Simulation status updates
        private string _currentGenoration;
        public string CurrentGenoration
        {
            get
            {
                return _currentGenoration;
            }
            set
            {
                _currentGenoration = value;
                NotifyPropertyChanged(nameof(CurrentGenoration));
            }
        }
        
        private string _lastGenorationUpdated;
        public string LastGenorationUpdated
        {
            get
            {
                return _lastGenorationUpdated;
            }
            set
            {
                _lastGenorationUpdated = value;
                NotifyPropertyChanged(nameof(LastGenorationUpdated));
            }
        }

        private string _currentFitness;
        public string CurrentFitness
        {
            get
            {
                return _currentFitness;
            }
            set
            {
                _currentFitness = value;
                NotifyPropertyChanged(nameof(CurrentFitness));
            }
        }

        private string _timeRunning;
        public string TimeRunning
        {
            get
            {
                return _timeRunning;
            }
            set
            {
                _timeRunning = value;
                NotifyPropertyChanged(nameof(TimeRunning));

            }
        }
        //The above are for live simulation


        public ICommand OpenFolderCommand { get; set; }

        public ICommand LoadSoundFile { get; set; }
        public ICommand RunSimulation { get; set; }


        public ICommand PlayAudioCommand { get; set; }
        public ICommand PauseAudioCommand { get; set; }
        public ICommand NextFileCommand { get; set; }
        public ICommand PreviousFileCommand { get; set; }
        public ICommand StopAudioCommand { get; set; }



        private string _genorationNumber;
        public string GenerationNameDisplay
        {
            get
            {
                return _genorationNumber;
            }
            set
            {
                _genorationNumber = value;
                NotifyPropertyChanged(nameof(GenerationNameDisplay));
            }
        }

        public string ChosenFolderPath { get; set; }
        public string[] PreviousSimSoundFiles { get; set; }
        private string _selectedPreviousSimSoundFile;
        public string SelectedPreviousSimSoundFile
        {
            get
            {
                return _selectedPreviousSimSoundFile;
            }
            set
            {
                _selectedPreviousSimSoundFile = value;
                NotifyPropertyChanged(nameof(SelectedPreviousSimSoundFile));
            }
        }
        public int SelectedPreviousSimSoundFileIndex = 0;
  

        public void RunGeneticSimulation()
        {
            var temp = SoundFilePathForSimulation.Split('\\');
            CurrentSimFileName = temp[temp.Length-1];

            SetTabToCurrentSimulation();
            runTimer = new DispatcherTimer(new TimeSpan(0, 0, 0, 1, 0), DispatcherPriority.Background,
                Timer_Tick, Dispatcher.CurrentDispatcher);
            runTimer.IsEnabled = true;
            startTime = DateTime.Now;


            //Check that a sound file path has been selected
            if (SoundFilePathForSimulation != null)
            {
                GeneticSimulator genSim = new GeneticSimulator();

                Thread genThread = new Thread(() =>
                {
                    Thread.CurrentThread.IsBackground = true;
                    genSim.StartSimulation(SoundFilePathForSimulation, this);
      
                });

                genThread.Start();

                //genSim.StartSimulation(SoundFilePathForSimulation);

            }


        }

        private void Timer_Tick(object sender, EventArgs e)
        {
            var result = (DateTime.Now - startTime);
            TimeRunning = "Time Running: " + string.Format("{0:00}:{1:00}:{2:00}", result.Hours, result.Minutes, result.Seconds);
        }


        public void LoadSoundFileForSimulation()
        {
            CommonOpenFileDialog dialog = new CommonOpenFileDialog();
            dialog.InitialDirectory = "C:\\Users";

            if (dialog.ShowDialog() == CommonFileDialogResult.Ok)
            {

                SoundFilePathForSimulation = dialog.FileName;

            }

        }

        public void SetTabToCurrentSimulation()
        {
            SelectedIndex = 1;
        }

        public void SetAudioController(string newFilePath)
        {
            if(AudioControl != null)
            {
                AudioControl.StopAudio();
            }

            string[] fileName = newFilePath.Split('\\');
            
            GenerationNameDisplay = fileName[fileName.Length - 1];
            AudioControl = new AudioController(newFilePath);
        }

        public void LoadPreviousSim()
        {
            //Open project file (to display genoration wav files to play)
            CommonOpenFileDialog dialog = new CommonOpenFileDialog();
            dialog.InitialDirectory = Environment.GetFolderPath(Environment.SpecialFolder.Desktop);
            dialog.IsFolderPicker = true;

            if (dialog.ShowDialog() == CommonFileDialogResult.Ok)
            {
                //MessageBox.Show("You selected: " + dialog.FileName);
                ChosenFolderPath = dialog.FileName;
                PreviousSimSoundFiles = Directory.GetFiles(ChosenFolderPath);
                SelectedPreviousSimSoundFileIndex = 0;

                if (PreviousSimSoundFiles.Length >= 1)
                {
                    //Add error handling here incase the chosen folder does not contain any wav files
                    //Also remove all non .Wav files from file array (use message box to handle this)
                    SelectedPreviousSimSoundFile = PreviousSimSoundFiles[SelectedPreviousSimSoundFileIndex];
                    LoadResultsBorderVis = true;
                    SetAudioController(SelectedPreviousSimSoundFile);
                    audioPlayback.Load(SelectedPreviousSimSoundFile);

                }
            }
        }

        public event PropertyChangedEventHandler PropertyChanged;
        protected void NotifyPropertyChanged(String info)
        {
            if (PropertyChanged != null)
            {
                PropertyChanged(this, new PropertyChangedEventArgs(info));
            }
        }

    }
}
