using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace GeneticAlgorithmMusicProject.Simulator
{
    public class Chromosome
    {
        public Chromosome(char[] dna, char[] goal)
        {
            GeneticSimulator genSim = new GeneticSimulator();

            DNA = dna;
            Fitness = genSim.FitnessCalculater(dna, goal);
        }
        public char[] DNA { get; set; }
        public double Fitness { get; set; }
    }
}
