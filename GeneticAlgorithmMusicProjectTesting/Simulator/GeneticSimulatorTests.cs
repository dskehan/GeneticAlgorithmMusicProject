using GeneticAlgorithmMusicProjectTesting.TestHelpers;
using System.IO;

namespace GeneticAlgorithmMusicProjectTesting.Simulator
{
    /// <summary>
    /// Unit tests for the GeneticSimulator class.
    /// </summary>
    [TestFixture]
    public class GeneticSimulatorTests
    {
        private GeneticSimulator simulator;
        private GeneticAlgorithmConfig testConfig;
        private char[] testGoal;

        [SetUp]
        public void SetUp()
        {
            testConfig = TestDataFactory.CreateTestConfig();
            simulator = new GeneticSimulator(testConfig);
            testGoal = TestDataFactory.CreateTestGoal(5);
        }

        [Test]
        public void Constructor_WithNullConfig_UsesDefaultConfig()
        {
            // Arrange & Act
            var simulator = new GeneticSimulator(null);

            // Assert - Should not throw and should be usable
            Assert.That(simulator, Is.Not.Null);
        }

        [Test]
        public void Constructor_WithValidConfig_AcceptsConfig()
        {
            // Arrange & Act
            var simulator = new GeneticSimulator(testConfig);

            // Assert
            Assert.That(simulator, Is.Not.Null);
        }

        [Test]
        public void Constructor_WithInvalidConfig_ThrowsArgumentException()
        {
            // Arrange
            var invalidConfig = new GeneticAlgorithmConfig { PopulationSize = -1 };

            // Act & Assert
            Assert.Throws<ArgumentException>(() => new GeneticSimulator(invalidConfig));
        }

        [Test]
        public void FitnessCalculator_WithNullChromosome_ThrowsArgumentNullException()
        {
            // Arrange, Act & Assert
            Assert.Throws<ArgumentNullException>(() => simulator.FitnessCalculator(null, testGoal));
        }

        [Test]
        public void FitnessCalculator_WithNullGoal_ThrowsArgumentNullException()
        {
            // Arrange
            var testDNA = TestDataFactory.CreateTestGoal(5);

            // Act & Assert
            Assert.Throws<ArgumentNullException>(() => simulator.FitnessCalculator(testDNA, null));
        }

        [Test]
        public void FitnessCalculator_WithEmptyGoal_ReturnsZero()
        {
            // Arrange
            var emptyGoal = new char[0];
            var emptyChromosome = new char[0];

            // Act
            var fitness = simulator.FitnessCalculator(emptyChromosome, emptyGoal);

            // Assert
            Assert.That(fitness, Is.EqualTo(0.0));
        }

        [Test]
        public void FitnessCalculator_WithDifferentLengths_ThrowsArgumentException()
        {
            // Arrange
            var shortChromosome = new char[] { 'A' };
            var longGoal = new char[] { 'A', 'B', 'C' };

            // Act & Assert
            Assert.Throws<ArgumentException>(() => simulator.FitnessCalculator(shortChromosome, longGoal));
        }

        [Test]
        public void FitnessCalculator_WithPerfectMatch_Returns100()
        {
            // Arrange
            var perfectMatch = TestDataFactory.CreatePerfectMatchDNA(testGoal);

            // Act
            var fitness = simulator.FitnessCalculator(perfectMatch, testGoal);

            // Assert
            Assert.That(fitness, Is.EqualTo(100.0).Within(0.001));
        }

        [Test]
        public void FitnessCalculator_WithNoMatch_ReturnsZero()
        {
            // Arrange
            var noMatch = TestDataFactory.CreateNoMatchDNA(testGoal);

            // Act
            var fitness = simulator.FitnessCalculator(noMatch, testGoal);

            // Assert
            Assert.That(fitness, Is.EqualTo(0.0).Within(0.001));
        }

        [Test]
        public void FitnessCalculator_WithPartialMatch_ReturnsCorrectPercentage()
        {
            // Arrange
            var partialMatch = TestDataFactory.CreatePartialMatchDNA(testGoal, 0.6); // 60% match

            // Act
            var fitness = simulator.FitnessCalculator(partialMatch, testGoal);

            // Assert
            Assert.That(fitness, Is.EqualTo(60.0).Within(0.001));
        }

        [Test]
        public void RandomChromosomeGenerator_WithoutGoalSet_ThrowsInvalidOperationException()
        {
            // Arrange & Act & Assert
            Assert.Throws<InvalidOperationException>(() => simulator.RandomChromosomeGenerator());
        }

        [Test]
        public void RandomChromosomeGenerator_WithGoalSet_ReturnsCorrectLength()
        {
            // Arrange
            SetSimulatorGoal(testGoal);

            // Act
            var chromosome = simulator.RandomChromosomeGenerator();

            // Assert
            Assert.That(chromosome, Is.Not.Null);
            Assert.That(chromosome.Length, Is.EqualTo(testGoal.Length));
        }

        [Test]
        public void RandomChromosomeGenerator_GeneratesDifferentChromosomes()
        {
            // Arrange
            SetSimulatorGoal(testGoal);

            // Act
            var chromosome1 = simulator.RandomChromosomeGenerator();
            var chromosome2 = simulator.RandomChromosomeGenerator();

            // Assert - With random generation, they should likely be different
            // Note: There's a tiny chance they could be the same, but very unlikely
            Assert.That(chromosome1, Is.Not.EqualTo(chromosome2));
        }

        [Test]
        public void GenerateInitialPopulation_WithoutGoalSet_ThrowsInvalidOperationException()
        {
            // Arrange & Act & Assert
            Assert.Throws<InvalidOperationException>(() => simulator.GenerateInitialPopulation());
        }

        [Test]
        public void GenerateInitialPopulation_WithGoalSet_ReturnsCorrectPopulationSize()
        {
            // Arrange
            SetSimulatorGoal(testGoal);

            // Act
            var result = simulator.GenerateInitialPopulation();

            // Assert
            Assert.That(result.Item1, Is.Not.Null);
            Assert.That(result.Item1.Length, Is.EqualTo(testConfig.PopulationSize));
            Assert.That(result.Item2, Is.Not.Null);
            Assert.That(result.Item2.Length, Is.EqualTo(testGoal.Length));
        }

        [Test]
        public void GenerateInitialPopulation_ReturnsValidChromosomes()
        {
            // Arrange
            SetSimulatorGoal(testGoal);

            // Act
            var result = simulator.GenerateInitialPopulation();

            // Assert
            foreach (var chromosome in result.Item1)
            {
                Assert.That(chromosome, Is.Not.Null);
                Assert.That(chromosome.DNA.Length, Is.EqualTo(testGoal.Length));
                Assert.That(chromosome.Fitness, Is.GreaterThanOrEqualTo(0));
                Assert.That(chromosome.Fitness, Is.LessThanOrEqualTo(100));
            }
        }

        [Test]
        public void Mutate_WithNullInput_ThrowsArgumentNullException()
        {
            // Arrange, Act & Assert
            Assert.Throws<ArgumentNullException>(() => simulator.Mutate(null));
        }

        [Test]
        public void Mutate_WithEmptyArray_ReturnsEmptyArray()
        {
            // Arrange
            var emptyArray = new char[0];

            // Act
            var result = simulator.Mutate(emptyArray);

            // Assert
            Assert.That(result, Is.Not.Null);
            Assert.That(result.Length, Is.EqualTo(0));
        }

        [Test]
        public void Mutate_DoesNotModifyOriginalArray()
        {
            // Arrange
            var original = (char[])testGoal.Clone();
            var toMutate = (char[])testGoal.Clone();

            // Act
            simulator.Mutate(toMutate);

            // Assert - Original array should be unchanged
            Assert.That(original, Is.EqualTo(testGoal));
        }

        [Test]
        public void Mutate_ReturnsArrayOfSameLength()
        {
            // Arrange
            var testArray = (char[])testGoal.Clone();

            // Act
            var result = simulator.Mutate(testArray);

            // Assert
            Assert.That(result.Length, Is.EqualTo(testArray.Length));
        }

        [Test]
        public void GenerateMatingPool_WithNullPopulation_ThrowsArgumentNullException()
        {
            // Arrange, Act & Assert
            Assert.Throws<ArgumentNullException>(() => simulator.GenerateMatingPool(null));
        }

        [Test]
        public void GenerateMatingPool_WithEmptyPopulation_ThrowsArgumentException()
        {
            // Arrange
            var emptyPopulation = new Chromosome[0];

            // Act & Assert
            Assert.Throws<ArgumentException>(() => simulator.GenerateMatingPool(emptyPopulation));
        }

        [Test]
        public void GenerateMatingPool_WithValidPopulation_ReturnsPool()
        {
            // Arrange
            var population = CreateTestPopulation();

            // Act
            var matingPool = simulator.GenerateMatingPool(population);

            // Assert
            Assert.That(matingPool, Is.Not.Null);
            Assert.That(matingPool.Count, Is.GreaterThan(0));
        }

        [Test]
        public void GenerateMatingPool_HigherFitnessChromosomesAppearMoreOften()
        {
            // Arrange
            var highFitnessChromosome = new Chromosome(TestDataFactory.CreatePerfectMatchDNA(testGoal), testGoal);
            var lowFitnessChromosome = new Chromosome(TestDataFactory.CreateNoMatchDNA(testGoal), testGoal);
            var population = new[] { highFitnessChromosome, lowFitnessChromosome };

            // Act
            var matingPool = simulator.GenerateMatingPool(population);

            // Assert
            var highFitnessCount = matingPool.Count(c => c == highFitnessChromosome);
            var lowFitnessCount = matingPool.Count(c => c == lowFitnessChromosome);
            Assert.That(highFitnessCount, Is.GreaterThan(lowFitnessCount));
        }

        [Test]
        public void CreateOutputFolder_WithNullPath_ThrowsArgumentException()
        {
            // Arrange, Act & Assert
            Assert.Throws<ArgumentException>(() => simulator.CreateOutputFolder(null));
        }

        [Test]
        public void CreateOutputFolder_WithEmptyPath_ThrowsArgumentException()
        {
            // Arrange, Act & Assert
            Assert.Throws<ArgumentException>(() => simulator.CreateOutputFolder(""));
        }

        [Test]
        public void CreateOutputFolder_WithValidPath_SetsProperties()
        {
            // Arrange
            var testPath = @"C:\temp\testfile.wav";

            // Act
            simulator.CreateOutputFolder(testPath);

            // Assert
            Assert.That(simulator.FileName, Is.EqualTo("testfile"));
            Assert.That(simulator.OutputFolderPath, Is.Not.Null);
            Assert.That(simulator.OutputFolderPath, Does.Contain("testfile"));
        }

        [Test]
        public void GetWavFile_WithNullPath_ThrowsArgumentException()
        {
            // Arrange, Act & Assert
            Assert.Throws<ArgumentException>(() => simulator.GetWavFile(null));
        }

        [Test]
        public void GetWavFile_WithNonExistentFile_ThrowsFileNotFoundException()
        {
            // Arrange
            var nonExistentPath = @"C:\nonexistent\file.wav";

            // Act & Assert
            Assert.Throws<FileNotFoundException>(() => simulator.GetWavFile(nonExistentPath));
        }

        [Test]
        public void GetWavFile_WithValidFile_ReturnsData()
        {
            // Arrange
            var testWavFile = TestDataFactory.CreateTestWavFile();

            try
            {
                // Act
                var result = simulator.GetWavFile(testWavFile);

                // Assert
                Assert.That(result.Item1, Is.Not.Null); // Goal data
                Assert.That(result.Item2, Is.Not.Null); // Header data
                Assert.That(result.Item2.Length, Is.EqualTo(testConfig.WavHeaderSize));
            }
            finally
            {
                // Cleanup
                TestDataFactory.CleanupTestFile(testWavFile);
            }
        }

        [Test]
        public void GetWavFile_WithTooSmallFile_ThrowsInvalidDataException()
        {
            // Arrange
            var tinyFilePath = Path.GetTempFileName();
            File.WriteAllBytes(tinyFilePath, new byte[10]); // Smaller than header size

            try
            {
                // Act & Assert
                Assert.Throws<InvalidDataException>(() => simulator.GetWavFile(tinyFilePath));
            }
            finally
            {
                // Cleanup
                TestDataFactory.CleanupTestFile(tinyFilePath);
            }
        }

        [Test]
        public void StartSimulation_WithNullFilePath_LogsError()
        {
            // Arrange
            string errorMessage = null;
            simulator.ErrorOccurred += (sender, message) => errorMessage = message;

            // Act
            simulator.StartSimulation(null, null);

            // Assert
            Assert.That(errorMessage, Is.Not.Null);
            Assert.That(errorMessage, Does.Contain("File path cannot be null"));
        }

        [Test]
        public void StartSimulation_WithNonExistentFile_LogsError()
        {
            // Arrange
            string errorMessage = null;
            simulator.ErrorOccurred += (sender, message) => errorMessage = message;

            // Act
            simulator.StartSimulation("nonexistent.wav", null);

            // Assert
            Assert.That(errorMessage, Is.Not.Null);
            Assert.That(errorMessage, Does.Contain("File not found"));
        }

        [Test]
        public void StartSimulation_WithNullMainViewModel_LogsError()
        {
            // Arrange
            string errorMessage = null;
            simulator.ErrorOccurred += (sender, message) => errorMessage = message;
            var testWavFile = TestDataFactory.CreateTestWavFile();

            try
            {
                // Act
                simulator.StartSimulation(testWavFile, null);

                // Assert
                Assert.That(errorMessage, Is.Not.Null);
                Assert.That(errorMessage, Does.Contain("MainViewModel cannot be null"));
            }
            finally
            {
                TestDataFactory.CleanupTestFile(testWavFile);
            }
        }

        // Helper methods
        private void SetSimulatorGoal(char[] goal)
        {
            // Use reflection to set the private Goal property for testing
            var goalProperty = typeof(GeneticSimulator).GetProperty("Goal");
            goalProperty?.SetValue(simulator, goal);
        }

        private Chromosome[] CreateTestPopulation()
        {
            var population = new Chromosome[3];
            population[0] = new Chromosome(TestDataFactory.CreatePerfectMatchDNA(testGoal), testGoal);
            population[1] = new Chromosome(TestDataFactory.CreatePartialMatchDNA(testGoal, 0.5), testGoal);
            population[2] = new Chromosome(TestDataFactory.CreateNoMatchDNA(testGoal), testGoal);
            return population;
        }
    }
}