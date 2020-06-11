using GeneticAlgorithmMusicProject.Views;
using NAudio.Dsp;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace GeneticAlgorithmMusicProject.HelperClasses
{
    class PolygonWaveFormVisualization : IVisualizationPlugin
    {
        private readonly PolygonWaveFormControl polygonWaveFormControl = new PolygonWaveFormControl();

        public string Name => "Polygon WaveForm Visualization";

        public object Content => polygonWaveFormControl;

        public void OnMaxCalculated(float min, float max)
        {
            polygonWaveFormControl.AddValue(max, min);
        }

        public void OnFftCalculated(NAudio.Dsp.Complex[] result)
        {
            // nothing to do
        }


    }
}
