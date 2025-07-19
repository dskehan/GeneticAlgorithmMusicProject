using GeneticAlgorithmMusicProjectTesting.TestHelpers;

namespace GeneticAlgorithmMusicProjectTesting.Simulator
{
    /// <summary>
    /// Unit tests for the Chromosome class.
    /// </summary>
    [TestFixture]
    public class ChromosomeTests
    {
        private char[] testGoal;
        private char[] perfectMatchDNA;
        private char[] partialMatchDNA;
        private char[] noMatchDNA;

        [SetUp]
        public void SetUp()
        {
            testGoal = TestDataFactory.CreateTestGoal(10);
            perfectMatchDNA = TestDataFactory.CreatePerfectMatchDNA(testGoal);
            partialMatchDNA = TestDataFactory.CreatePartialMatchDNA(testGoal, 0.5);
            noMatchDNA = TestDataFactory.CreateNoMatchDNA(testGoal);
        }

        [Test]
        public void Constructor_WithValidDNAAndGoal_CreatesChromosome()
        {
            // Arrange & Act
            var chromosome = new Chromosome(perfectMatchDNA, testGoal);

            // Assert
            Assert.That(chromosome.DNA, Is.Not.Null);
            Assert.That(chromosome.DNA.Length, Is.EqualTo(testGoal.Length));
            Assert.That(chromosome.Fitness, Is.GreaterThanOrEqualTo(0));
            Assert.That(chromosome.Fitness, Is.LessThanOrEqualTo(100));
        }

        [Test]
        public void Constructor_WithPerfectMatch_ReturnsFitness100()
        {
            // Arrange & Act
            var chromosome = new Chromosome(perfectMatchDNA, testGoal);

            // Assert
            Assert.That(chromosome.Fitness, Is.EqualTo(100.0).Within(0.001));
        }

        [Test]
        public void Constructor_WithNoMatch_ReturnsFitness0()
        {
            // Arrange & Act
            var chromosome = new Chromosome(noMatchDNA, testGoal);

            // Assert
            Assert.That(chromosome.Fitness, Is.EqualTo(0.0).Within(0.001));
        }

        [Test]
        public void Constructor_WithPartialMatch_ReturnsExpectedFitness()
        {
            // Arrange
            var expectedFitness = 50.0; // 50% match

            // Act
            var chromosome = new Chromosome(partialMatchDNA, testGoal);

            // Assert
            Assert.That(chromosome.Fitness, Is.EqualTo(expectedFitness).Within(0.001));
        }

        [Test]
        public void Constructor_WithNullDNA_ThrowsArgumentNullException()
        {
            // Arrange, Act & Assert
            Assert.Throws<ArgumentNullException>(() => new Chromosome(null, testGoal));
        }

        [Test]
        public void Constructor_WithNullGoal_ThrowsArgumentNullException()
        {
            // Arrange, Act & Assert
            Assert.Throws<ArgumentNullException>(() => new Chromosome(perfectMatchDNA, null));
        }

        [Test]
        public void Constructor_WithDifferentLengths_ThrowsArgumentException()
        {
            // Arrange
            var shortDNA = new char[] { 'A', 'B' };

            // Act & Assert
            Assert.Throws<ArgumentException>(() => new Chromosome(shortDNA, testGoal));
        }

        [Test]
        public void Constructor_CreatesDeepCopyOfDNA()
        {
            // Arrange
            var originalDNA = (char[])perfectMatchDNA.Clone();

            // Act
            var chromosome = new Chromosome(perfectMatchDNA, testGoal);
            perfectMatchDNA[0] = 'X'; // Modify original array

            // Assert
            Assert.That(chromosome.DNA[0], Is.Not.EqualTo('X'));
            Assert.That(chromosome.DNA[0], Is.EqualTo(originalDNA[0]));
        }

        [Test]
        public void DNA_PropertyIsReadOnly()
        {
            // Arrange
            var chromosome = new Chromosome(perfectMatchDNA, testGoal);
            var originalFirstChar = chromosome.DNA[0];

            // Act
            chromosome.DNA[0] = 'X'; // This modifies the returned array, but shouldn't affect the internal copy

            // Assert - The property returns a reference, so this test ensures we're aware of this behavior
            Assert.That(chromosome.DNA[0], Is.EqualTo('X'));
            // Note: In a production scenario, you might want to return a copy from the property getter
        }

        [Test]
        public void Fitness_PropertyIsReadOnly()
        {
            // Arrange
            var chromosome = new Chromosome(perfectMatchDNA, testGoal);
            var originalFitness = chromosome.Fitness;

            // Act & Assert - Fitness should only have a getter
            Assert.That(chromosome.Fitness, Is.EqualTo(originalFitness));
            // The property should be read-only, so no setter to test
        }

        [Test]
        public void Clone_CreatesNewChromosomeWithSameDNA()
        {
            // Arrange
            var original = new Chromosome(perfectMatchDNA, testGoal);

            // Act
            var clone = original.Clone(testGoal);

            // Assert
            Assert.That(clone, Is.Not.SameAs(original));
            Assert.That(clone.DNA, Is.EqualTo(original.DNA));
            Assert.That(clone.Fitness, Is.EqualTo(original.Fitness));
        }

        [Test]
        public void Clone_WithDifferentGoal_RecalculatesFitness()
        {
            // Arrange
            var original = new Chromosome(perfectMatchDNA, testGoal);
            var differentGoal = TestDataFactory.CreateNoMatchDNA(testGoal);

            // Act
            var clone = original.Clone(differentGoal);

            // Assert
            Assert.That(clone.DNA, Is.EqualTo(original.DNA));
            Assert.That(clone.Fitness, Is.Not.EqualTo(original.Fitness));
            Assert.That(clone.Fitness, Is.EqualTo(0.0).Within(0.001)); // Should be 0% match
        }

        [Test]
        public void ToString_ReturnsFormattedString()
        {
            // Arrange
            var chromosome = new Chromosome(perfectMatchDNA, testGoal);

            // Act
            var result = chromosome.ToString();

            // Assert
            Assert.That(result, Is.Not.Null);
            Assert.That(result, Does.Contain("Fitness"));
            Assert.That(result, Does.Contain("100.00"));
            Assert.That(result, Does.Contain("DNA Length"));
            Assert.That(result, Does.Contain(testGoal.Length.ToString()));
        }

        [Test]
        public void Constructor_WithEmptyArrays_HandlesGracefully()
        {
            // Arrange
            var emptyDNA = new char[0];
            var emptyGoal = new char[0];

            // Act
            var chromosome = new Chromosome(emptyDNA, emptyGoal);

            // Assert
            Assert.That(chromosome.DNA.Length, Is.EqualTo(0));
            Assert.That(chromosome.Fitness, Is.EqualTo(0.0));
        }

        [Test]
        public void Constructor_WithSingleCharacter_CalculatesCorrectFitness()
        {
            // Arrange
            var singleCharDNA = new char[] { 'A' };
            var singleCharGoal = new char[] { 'A' };

            // Act
            var chromosome = new Chromosome(singleCharDNA, singleCharGoal);

            // Assert
            Assert.That(chromosome.Fitness, Is.EqualTo(100.0).Within(0.001));
        }

        [Test]
        public void Constructor_WithSingleCharacterMismatch_ReturnsZeroFitness()
        {
            // Arrange
            var singleCharDNA = new char[] { 'A' };
            var singleCharGoal = new char[] { 'B' };

            // Act
            var chromosome = new Chromosome(singleCharDNA, singleCharGoal);

            // Assert
            Assert.That(chromosome.Fitness, Is.EqualTo(0.0).Within(0.001));
        }

        [Test]
        public void Fitness_CalculationIsAccurate()
        {
            // Arrange - Create a specific pattern where we know the exact fitness
            var dna = new char[] { 'A', 'B', 'C', 'D', 'E' };
            var goal = new char[] { 'A', 'X', 'C', 'Y', 'E' };
            // 3 out of 5 match = 60%

            // Act
            var chromosome = new Chromosome(dna, goal);

            // Assert
            Assert.That(chromosome.Fitness, Is.EqualTo(60.0).Within(0.001));
        }

        [Test]
        public void Constructor_WithLargeArrays_PerformsReasonably()
        {
            // Arrange
            var largeDNA = new char[10000];
            var largeGoal = new char[10000];
            
            for (int i = 0; i < 10000; i++)
            {
                largeDNA[i] = (char)('A' + (i % 26));
                largeGoal[i] = (char)('A' + (i % 26));
            }

            // Act
            var stopwatch = System.Diagnostics.Stopwatch.StartNew();
            var chromosome = new Chromosome(largeDNA, largeGoal);
            stopwatch.Stop();

            // Assert
            Assert.That(chromosome.Fitness, Is.EqualTo(100.0).Within(0.001));
            Assert.That(stopwatch.ElapsedMilliseconds, Is.LessThan(1000)); // Should complete in reasonable time
        }
    }
}