namespace GeneticAlgorithmMusicProjectTesting.HelperClasses
{
    /// <summary>
    /// Unit tests for the GeneticAlgorithmConfig class.
    /// </summary>
    [TestFixture]
    public class GeneticAlgorithmConfigTests
    {
        [Test]
        public void Constructor_DefaultValues_SetsExpectedValues()
        {
            // Arrange & Act
            var config = new GeneticAlgorithmConfig();

            // Assert
            Assert.That(config.PopulationSize, Is.EqualTo(GeneticAlgorithmConfig.DEFAULT_POPULATION_SIZE));
            Assert.That(config.MutationFactor, Is.EqualTo(GeneticAlgorithmConfig.DEFAULT_MUTATION_FACTOR));
            Assert.That(config.DesiredLatency, Is.EqualTo(GeneticAlgorithmConfig.DEFAULT_DESIRED_LATENCY));
            Assert.That(config.NotificationCountDivisor, Is.EqualTo(GeneticAlgorithmConfig.DEFAULT_NOTIFICATION_COUNT_DIVISOR));
            Assert.That(config.MinRandomCharValue, Is.EqualTo(GeneticAlgorithmConfig.DEFAULT_MIN_RANDOM_CHAR));
            Assert.That(config.MaxRandomCharValue, Is.EqualTo(GeneticAlgorithmConfig.DEFAULT_MAX_RANDOM_CHAR));
            Assert.That(config.WavHeaderSize, Is.EqualTo(GeneticAlgorithmConfig.DEFAULT_WAV_HEADER_SIZE));
            Assert.That(config.FitnessMultiplier, Is.EqualTo(GeneticAlgorithmConfig.DEFAULT_FITNESS_MULTIPLIER));
        }

        [Test]
        public void Constructor_DefaultValues_HasDefaultMilestones()
        {
            // Arrange & Act
            var config = new GeneticAlgorithmConfig();

            // Assert
            Assert.That(config.Milestones, Is.Not.Null);
            Assert.That(config.Milestones.Count, Is.GreaterThan(0));
            Assert.That(config.Milestones, Does.Contain(2));
            Assert.That(config.Milestones, Does.Contain(50));
            Assert.That(config.Milestones, Does.Contain(97));
        }

        [Test]
        public void IsValid_WithDefaultValues_ReturnsTrue()
        {
            // Arrange
            var config = new GeneticAlgorithmConfig();

            // Act
            var isValid = config.IsValid();

            // Assert
            Assert.That(isValid, Is.True);
        }

        [Test]
        public void IsValid_WithZeroPopulationSize_ReturnsFalse()
        {
            // Arrange
            var config = new GeneticAlgorithmConfig { PopulationSize = 0 };

            // Act
            var isValid = config.IsValid();

            // Assert
            Assert.That(isValid, Is.False);
        }

        [Test]
        public void IsValid_WithNegativePopulationSize_ReturnsFalse()
        {
            // Arrange
            var config = new GeneticAlgorithmConfig { PopulationSize = -10 };

            // Act
            var isValid = config.IsValid();

            // Assert
            Assert.That(isValid, Is.False);
        }

        [Test]
        public void IsValid_WithNegativeMutationFactor_ReturnsFalse()
        {
            // Arrange
            var config = new GeneticAlgorithmConfig { MutationFactor = -1 };

            // Act
            var isValid = config.IsValid();

            // Assert
            Assert.That(isValid, Is.False);
        }

        [Test]
        public void IsValid_WithZeroMutationFactor_ReturnsTrue()
        {
            // Arrange
            var config = new GeneticAlgorithmConfig { MutationFactor = 0 };

            // Act
            var isValid = config.IsValid();

            // Assert
            Assert.That(isValid, Is.True);
        }

        [Test]
        public void IsValid_WithZeroDesiredLatency_ReturnsFalse()
        {
            // Arrange
            var config = new GeneticAlgorithmConfig { DesiredLatency = 0 };

            // Act
            var isValid = config.IsValid();

            // Assert
            Assert.That(isValid, Is.False);
        }

        [Test]
        public void IsValid_WithZeroNotificationCountDivisor_ReturnsFalse()
        {
            // Arrange
            var config = new GeneticAlgorithmConfig { NotificationCountDivisor = 0 };

            // Act
            var isValid = config.IsValid();

            // Assert
            Assert.That(isValid, Is.False);
        }

        [Test]
        public void IsValid_WithNegativeMinRandomCharValue_ReturnsFalse()
        {
            // Arrange
            var config = new GeneticAlgorithmConfig { MinRandomCharValue = -1 };

            // Act
            var isValid = config.IsValid();

            // Assert
            Assert.That(isValid, Is.False);
        }

        [Test]
        public void IsValid_WithMaxRandomCharValueLessThanMin_ReturnsFalse()
        {
            // Arrange
            var config = new GeneticAlgorithmConfig 
            { 
                MinRandomCharValue = 100,
                MaxRandomCharValue = 50 
            };

            // Act
            var isValid = config.IsValid();

            // Assert
            Assert.That(isValid, Is.False);
        }

        [Test]
        public void IsValid_WithMaxRandomCharValueEqualToMin_ReturnsFalse()
        {
            // Arrange
            var config = new GeneticAlgorithmConfig 
            { 
                MinRandomCharValue = 100,
                MaxRandomCharValue = 100 
            };

            // Act
            var isValid = config.IsValid();

            // Assert
            Assert.That(isValid, Is.False);
        }

        [Test]
        public void IsValid_WithZeroWavHeaderSize_ReturnsFalse()
        {
            // Arrange
            var config = new GeneticAlgorithmConfig { WavHeaderSize = 0 };

            // Act
            var isValid = config.IsValid();

            // Assert
            Assert.That(isValid, Is.False);
        }

        [Test]
        public void IsValid_WithZeroFitnessMultiplier_ReturnsFalse()
        {
            // Arrange
            var config = new GeneticAlgorithmConfig { FitnessMultiplier = 0.0 };

            // Act
            var isValid = config.IsValid();

            // Assert
            Assert.That(isValid, Is.False);
        }

        [Test]
        public void IsValid_WithNegativeFitnessMultiplier_ReturnsFalse()
        {
            // Arrange
            var config = new GeneticAlgorithmConfig { FitnessMultiplier = -1.0 };

            // Act
            var isValid = config.IsValid();

            // Assert
            Assert.That(isValid, Is.False);
        }

        [Test]
        public void CreateDefault_ReturnsValidConfiguration()
        {
            // Arrange & Act
            var config = GeneticAlgorithmConfig.CreateDefault();

            // Assert
            Assert.That(config, Is.Not.Null);
            Assert.That(config.IsValid(), Is.True);
            Assert.That(config.PopulationSize, Is.EqualTo(GeneticAlgorithmConfig.DEFAULT_POPULATION_SIZE));
        }

        [Test]
        public void CreateForTesting_ReturnsValidConfiguration()
        {
            // Arrange & Act
            var config = GeneticAlgorithmConfig.CreateForTesting();

            // Assert
            Assert.That(config, Is.Not.Null);
            Assert.That(config.IsValid(), Is.True);
            Assert.That(config.PopulationSize, Is.LessThan(GeneticAlgorithmConfig.DEFAULT_POPULATION_SIZE));
            Assert.That(config.MutationFactor, Is.LessThan(GeneticAlgorithmConfig.DEFAULT_MUTATION_FACTOR));
        }

        [Test]
        public void CreateForTesting_HasFewerMilestones()
        {
            // Arrange
            var defaultConfig = GeneticAlgorithmConfig.CreateDefault();

            // Act
            var testConfig = GeneticAlgorithmConfig.CreateForTesting();

            // Assert
            Assert.That(testConfig.Milestones.Count, Is.LessThan(defaultConfig.Milestones.Count));
        }

        [Test]
        public void Properties_CanBeModified()
        {
            // Arrange
            var config = new GeneticAlgorithmConfig();
            var newPopulationSize = 1000;
            var newMutationFactor = 25;

            // Act
            config.PopulationSize = newPopulationSize;
            config.MutationFactor = newMutationFactor;

            // Assert
            Assert.That(config.PopulationSize, Is.EqualTo(newPopulationSize));
            Assert.That(config.MutationFactor, Is.EqualTo(newMutationFactor));
        }

        [Test]
        public void Milestones_CanBeModified()
        {
            // Arrange
            var config = new GeneticAlgorithmConfig();
            var newMilestones = new List<int> { 10, 20, 30 };

            // Act
            config.Milestones = newMilestones;

            // Assert
            Assert.That(config.Milestones, Is.EqualTo(newMilestones));
            Assert.That(config.Milestones.Count, Is.EqualTo(3));
        }

        [Test]
        public void Milestones_CanBeAddedTo()
        {
            // Arrange
            var config = new GeneticAlgorithmConfig();
            var originalCount = config.Milestones.Count;

            // Act
            config.Milestones.Add(99);

            // Assert
            Assert.That(config.Milestones.Count, Is.EqualTo(originalCount + 1));
            Assert.That(config.Milestones, Does.Contain(99));
        }

        [Test]
        public void DefaultConstants_HaveExpectedValues()
        {
            // Assert - Verify the default constants haven't changed unexpectedly
            Assert.That(GeneticAlgorithmConfig.DEFAULT_POPULATION_SIZE, Is.EqualTo(500));
            Assert.That(GeneticAlgorithmConfig.DEFAULT_MUTATION_FACTOR, Is.EqualTo(50));
            Assert.That(GeneticAlgorithmConfig.DEFAULT_DESIRED_LATENCY, Is.EqualTo(200));
            Assert.That(GeneticAlgorithmConfig.DEFAULT_NOTIFICATION_COUNT_DIVISOR, Is.EqualTo(100));
            Assert.That(GeneticAlgorithmConfig.DEFAULT_MIN_RANDOM_CHAR, Is.EqualTo(0));
            Assert.That(GeneticAlgorithmConfig.DEFAULT_MAX_RANDOM_CHAR, Is.EqualTo(255));
            Assert.That(GeneticAlgorithmConfig.DEFAULT_WAV_HEADER_SIZE, Is.EqualTo(44));
            Assert.That(GeneticAlgorithmConfig.DEFAULT_FITNESS_MULTIPLIER, Is.EqualTo(10.0));
        }

        [Test]
        public void IsValid_WithAllValidBoundaryValues_ReturnsTrue()
        {
            // Arrange
            var config = new GeneticAlgorithmConfig
            {
                PopulationSize = 1,
                MutationFactor = 0,
                DesiredLatency = 1,
                NotificationCountDivisor = 1,
                MinRandomCharValue = 0,
                MaxRandomCharValue = 1,
                WavHeaderSize = 1,
                FitnessMultiplier = 0.001
            };

            // Act
            var isValid = config.IsValid();

            // Assert
            Assert.That(isValid, Is.True);
        }

        [Test]
        public void IsValid_WithLargeValues_ReturnsTrue()
        {
            // Arrange
            var config = new GeneticAlgorithmConfig
            {
                PopulationSize = 10000,
                MutationFactor = 1000,
                DesiredLatency = 5000,
                NotificationCountDivisor = 1000,
                MinRandomCharValue = 0,
                MaxRandomCharValue = 65535,
                WavHeaderSize = 1000,
                FitnessMultiplier = 100.0
            };

            // Act
            var isValid = config.IsValid();

            // Assert
            Assert.That(isValid, Is.True);
        }
    }
}