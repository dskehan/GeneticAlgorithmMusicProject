using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace GeneticAlgorithmMusicProject.Simulator
{
    /// <summary>
    /// Represents a chromosome in the genetic algorithm.
    /// </summary>
    public class Chromosome
    {
        /// <summary>
        /// Initializes a new instance of the Chromosome class.
        /// </summary>
        /// <param name="dna">The DNA sequence of the chromosome.</param>
        /// <param name="goal">The target goal sequence for fitness calculation.</param>
        /// <exception cref="ArgumentNullException">Thrown when dna or goal is null.</exception>
        /// <exception cref="ArgumentException">Thrown when dna and goal have different lengths.</exception>
        public Chromosome(char[] dna, char[] goal)
        {
            if (dna == null)
                throw new ArgumentNullException(nameof(dna));
            
            if (goal == null)
                throw new ArgumentNullException(nameof(goal));

            if (dna.Length != goal.Length)
                throw new ArgumentException("DNA and goal must have the same length.");

            DNA = (char[])dna.Clone(); // Create a copy to avoid external modifications
            Fitness = CalculateFitness(DNA, goal);
        }

        /// <summary>
        /// Gets the DNA sequence of the chromosome.
        /// </summary>
        public char[] DNA { get; private set; }

        /// <summary>
        /// Gets the fitness value of the chromosome (0-100 percentage).
        /// </summary>
        public double Fitness { get; private set; }

        /// <summary>
        /// Calculates the fitness of a chromosome compared to the goal.
        /// </summary>
        /// <param name="chromosome">The chromosome to evaluate.</param>
        /// <param name="goal">The target goal sequence.</param>
        /// <returns>Fitness percentage (0-100).</returns>
        private static double CalculateFitness(char[] chromosome, char[] goal)
        {
            if (goal.Length == 0)
                return 0;

            int commonCount = 0;
            for (int i = 0; i < chromosome.Length; i++)
            {
                if (chromosome[i] == goal[i])
                {
                    commonCount++;
                }
            }

            return (double)commonCount / goal.Length * 100.0;
        }

        /// <summary>
        /// Creates a deep copy of the chromosome.
        /// </summary>
        /// <param name="goal">The goal sequence for the new chromosome.</param>
        /// <returns>A new chromosome with the same DNA.</returns>
        public Chromosome Clone(char[] goal)
        {
            return new Chromosome(DNA, goal);
        }

        /// <summary>
        /// Returns a string representation of the chromosome.
        /// </summary>
        /// <returns>A string containing fitness and DNA information.</returns>
        public override string ToString()
        {
            return $"Fitness: {Fitness:F2}%, DNA Length: {DNA.Length}";
        }
    }
}
