using System;
using System.Collections.Generic;

namespace GeneticAlgorithmMusicProject.HelperClasses
{
    /// <summary>
    /// Configuration class for genetic algorithm parameters.
    /// </summary>
    public class GeneticAlgorithmConfig
    {
        // Default values for genetic algorithm parameters
        public const int DEFAULT_POPULATION_SIZE = 500;
        public const int DEFAULT_MUTATION_FACTOR = 50;
        public const int DEFAULT_DESIRED_LATENCY = 200;
        public const int DEFAULT_NOTIFICATION_COUNT_DIVISOR = 100;
        public const int DEFAULT_MIN_RANDOM_CHAR = 0;
        public const int DEFAULT_MAX_RANDOM_CHAR = 255;
        public const int DEFAULT_WAV_HEADER_SIZE = 44;
        public const double DEFAULT_FITNESS_MULTIPLIER = 10.0;

        /// <summary>
        /// Size of the population in each generation.
        /// </summary>
        public int PopulationSize { get; set; } = DEFAULT_POPULATION_SIZE;

        /// <summary>
        /// Number of mutations to perform on each chromosome.
        /// </summary>
        public int MutationFactor { get; set; } = DEFAULT_MUTATION_FACTOR;

        /// <summary>
        /// Desired audio latency in milliseconds.
        /// </summary>
        public int DesiredLatency { get; set; } = DEFAULT_DESIRED_LATENCY;

        /// <summary>
        /// Divisor for calculating notification count based on sample rate.
        /// </summary>
        public int NotificationCountDivisor { get; set; } = DEFAULT_NOTIFICATION_COUNT_DIVISOR;

        /// <summary>
        /// Minimum value for random character generation.
        /// </summary>
        public int MinRandomCharValue { get; set; } = DEFAULT_MIN_RANDOM_CHAR;

        /// <summary>
        /// Maximum value for random character generation.
        /// </summary>
        public int MaxRandomCharValue { get; set; } = DEFAULT_MAX_RANDOM_CHAR;

        /// <summary>
        /// Size of WAV file header in bytes.
        /// </summary>
        public int WavHeaderSize { get; set; } = DEFAULT_WAV_HEADER_SIZE;

        /// <summary>
        /// Multiplier for fitness calculation in mating pool generation.
        /// </summary>
        public double FitnessMultiplier { get; set; } = DEFAULT_FITNESS_MULTIPLIER;

        /// <summary>
        /// Milestones for outputting waves at specific fitness percentages.
        /// </summary>
        public List<int> Milestones { get; set; } = new List<int> { 2, 5, 10, 15, 25, 35, 50, 65, 75, 85, 90, 95, 97 };

        /// <summary>
        /// Validates the configuration values.
        /// </summary>
        /// <returns>True if all values are valid, false otherwise.</returns>
        public bool IsValid()
        {
            return PopulationSize > 0 &&
                   MutationFactor >= 0 &&
                   DesiredLatency > 0 &&
                   NotificationCountDivisor > 0 &&
                   MinRandomCharValue >= 0 &&
                   MaxRandomCharValue > MinRandomCharValue &&
                   WavHeaderSize > 0 &&
                   FitnessMultiplier > 0;
        }

        /// <summary>
        /// Creates a configuration with default values.
        /// </summary>
        /// <returns>A new configuration instance with default values.</returns>
        public static GeneticAlgorithmConfig CreateDefault()
        {
            return new GeneticAlgorithmConfig();
        }

        /// <summary>
        /// Creates a configuration for quick testing with smaller values.
        /// </summary>
        /// <returns>A new configuration instance optimized for testing.</returns>
        public static GeneticAlgorithmConfig CreateForTesting()
        {
            return new GeneticAlgorithmConfig
            {
                PopulationSize = 50,
                MutationFactor = 5,
                Milestones = new List<int> { 10, 25, 50, 75, 90 }
            };
        }
    }
}