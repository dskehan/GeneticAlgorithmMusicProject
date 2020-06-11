using GeneticAlgorithmMusicProject.HelperClasses;
using GeneticAlgorithmMusicProject.ViewModels;
using System;
using System.Collections.Generic;
using System.Configuration;
using System.Data;
using System.Linq;
using System.Threading.Tasks;
using System.Windows;

namespace GeneticAlgorithmMusicProject
{
    /// <summary>
    /// Interaction logic for App.xaml
    /// </summary>
    public partial class App : Application
    {
        protected override void OnStartup(StartupEventArgs e)
        {
            

            MainViewModel mainVm = new MainViewModel();
            MainWindow mainWin = new MainWindow(mainVm);
            mainWin.Show();

            base.OnStartup(e);
        }

    }
}
