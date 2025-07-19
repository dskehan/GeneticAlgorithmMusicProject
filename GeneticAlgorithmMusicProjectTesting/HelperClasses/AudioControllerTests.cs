using GeneticAlgorithmMusicProjectTesting.TestHelpers;
using System.IO;

namespace GeneticAlgorithmMusicProjectTesting.HelperClasses
{
    /// <summary>
    /// Unit tests for the AudioController class.
    /// </summary>
    [TestFixture]
    public class AudioControllerTests
    {
        private string testWavFile;

        [SetUp]
        public void SetUp()
        {
            testWavFile = TestDataFactory.CreateTestWavFile();
        }

        [TearDown]
        public void TearDown()
        {
            TestDataFactory.CleanupTestFile(testWavFile);
        }

        [Test]
        public void Constructor_WithNullFilePath_ThrowsArgumentException()
        {
            // Arrange, Act & Assert
            Assert.Throws<ArgumentException>(() => new AudioController(null));
        }

        [Test]
        public void Constructor_WithEmptyFilePath_ThrowsArgumentException()
        {
            // Arrange, Act & Assert
            Assert.Throws<ArgumentException>(() => new AudioController(""));
        }

        [Test]
        public void Constructor_WithWhitespaceFilePath_ThrowsArgumentException()
        {
            // Arrange, Act & Assert
            Assert.Throws<ArgumentException>(() => new AudioController("   "));
        }

        [Test]
        public void Constructor_WithNonExistentFile_ThrowsFileNotFoundException()
        {
            // Arrange, Act & Assert
            Assert.Throws<FileNotFoundException>(() => new AudioController("nonexistent.wav"));
        }

        [Test]
        public void Constructor_WithValidFile_CreatesInstance()
        {
            // Arrange & Act
            using (var controller = new AudioController(testWavFile))
            {
                // Assert
                Assert.That(controller, Is.Not.Null);
                Assert.That(controller.PlaybackWaveOutEvent, Is.Not.Null);
                Assert.That(controller.MediaPlayer, Is.Not.Null);
            }
        }

        [Test]
        public void Constructor_InitializesPropertiesAsNotNull()
        {
            // Arrange & Act
            using (var controller = new AudioController(testWavFile))
            {
                // Assert
                Assert.That(controller.PlaybackWaveOutEvent, Is.Not.Null);
                Assert.That(controller.MediaPlayer, Is.Not.Null);
            }
        }

        [Test]
        public void GetSongLengthInMilliseconds_WithValidFile_ReturnsPositiveValue()
        {
            // Arrange
            using (var controller = new AudioController(testWavFile))
            {
                // Act
                var length = controller.GetSongLengthInMilliseconds();

                // Assert
                Assert.That(length, Is.GreaterThanOrEqualTo(0));
            }
        }

        [Test]
        public void GetSongLengthInMilliseconds_WithDisposedController_ReturnsZero()
        {
            // Arrange
            var controller = new AudioController(testWavFile);
            controller.Dispose();

            // Act
            var length = controller.GetSongLengthInMilliseconds();

            // Assert
            Assert.That(length, Is.EqualTo(0));
        }

        [Test]
        public void PlayAudio_WithValidController_DoesNotThrow()
        {
            // Arrange
            using (var controller = new AudioController(testWavFile))
            {
                // Act & Assert
                Assert.DoesNotThrow(() => controller.PlayAudio());
            }
        }

        [Test]
        public void PauseAudio_WithValidController_DoesNotThrow()
        {
            // Arrange
            using (var controller = new AudioController(testWavFile))
            {
                // Act & Assert
                Assert.DoesNotThrow(() => controller.PauseAudio());
            }
        }

        [Test]
        public void StopAudio_WithValidController_DoesNotThrow()
        {
            // Arrange
            using (var controller = new AudioController(testWavFile))
            {
                // Act & Assert
                Assert.DoesNotThrow(() => controller.StopAudio());
            }
        }

        [Test]
        public void RepositionAudioTime_WithValidTime_DoesNotThrow()
        {
            // Arrange
            using (var controller = new AudioController(testWavFile))
            {
                // Act & Assert
                Assert.DoesNotThrow(() => controller.RepositionAudioTime(0));
            }
        }

        [Test]
        public void RepositionAudioTime_WithNegativeTime_TriggersErrorEvent()
        {
            // Arrange
            using (var controller = new AudioController(testWavFile))
            {
                string errorMessage = null;
                controller.ErrorOccurred += (sender, message) => errorMessage = message;

                // Act
                controller.RepositionAudioTime(-5);

                // Assert
                Assert.That(errorMessage, Is.Not.Null);
                Assert.That(errorMessage, Does.Contain("cannot be negative"));
            }
        }

        [Test]
        public void ErrorOccurred_EventIsTriggeredOnErrors()
        {
            // Arrange
            using (var controller = new AudioController(testWavFile))
            {
                string errorMessage = null;
                bool eventTriggered = false;
                controller.ErrorOccurred += (sender, message) => 
                {
                    errorMessage = message;
                    eventTriggered = true;
                };

                // Act - Trigger an error by calling with invalid parameters
                controller.RepositionAudioTime(-1);

                // Assert
                Assert.That(eventTriggered, Is.True);
                Assert.That(errorMessage, Is.Not.Null);
            }
        }

        [Test]
        public void Dispose_CanBeCalledMultipleTimes()
        {
            // Arrange
            var controller = new AudioController(testWavFile);

            // Act & Assert - Should not throw
            Assert.DoesNotThrow(() => controller.Dispose());
            Assert.DoesNotThrow(() => controller.Dispose());
        }

        [Test]
        public void DisposeAudio_CallsDispose()
        {
            // Arrange
            var controller = new AudioController(testWavFile);

            // Act & Assert
            Assert.DoesNotThrow(() => controller.DisposeAudio());
            
            // Verify that the controller is disposed by checking that operations fail gracefully
            var length = controller.GetSongLengthInMilliseconds();
            Assert.That(length, Is.EqualTo(0));
        }

        [Test]
        public void Properties_AreReadOnlyAfterConstruction()
        {
            // Arrange & Act
            using (var controller = new AudioController(testWavFile))
            {
                // Assert - Properties should have private setters
                var playbackProperty = typeof(AudioController).GetProperty("PlaybackWaveOutEvent");
                var mediaProperty = typeof(AudioController).GetProperty("MediaPlayer");
                
                Assert.That(playbackProperty?.SetMethod?.IsPrivate, Is.True);
                Assert.That(mediaProperty?.SetMethod?.IsPrivate, Is.True);
            }
        }

        [Test]
        public void SequentialOperations_WorkCorrectly()
        {
            // Arrange
            using (var controller = new AudioController(testWavFile))
            {
                // Act & Assert - Sequential operations should not throw
                Assert.DoesNotThrow(() => controller.PlayAudio());
                Assert.DoesNotThrow(() => controller.PauseAudio());
                Assert.DoesNotThrow(() => controller.StopAudio());
                Assert.DoesNotThrow(() => controller.RepositionAudioTime(0));
            }
        }

        [Test]
        public void Constructor_WithLargeFile_HandlesGracefully()
        {
            // Arrange - Create a larger test file
            var largeTestFile = Path.GetTempFileName();
            var largeTestWavFile = Path.ChangeExtension(largeTestFile, ".wav");
            
            try
            {
                // Create a larger WAV file (1KB of audio data)
                byte[] header = new byte[44]; // Standard WAV header
                byte[] audioData = new byte[1024];
                
                using (var fs = new FileStream(largeTestWavFile, FileMode.Create))
                {
                    fs.Write(header, 0, header.Length);
                    fs.Write(audioData, 0, audioData.Length);
                }

                // Act & Assert
                Assert.DoesNotThrow(() =>
                {
                    using (var controller = new AudioController(largeTestWavFile))
                    {
                        Assert.That(controller, Is.Not.Null);
                    }
                });
            }
            finally
            {
                // Cleanup
                TestDataFactory.CleanupTestFile(largeTestWavFile);
            }
        }

        [Test]
        public void PlayAudio_AfterDispose_TriggersErrorEvent()
        {
            // Arrange
            var controller = new AudioController(testWavFile);
            string errorMessage = null;
            controller.ErrorOccurred += (sender, message) => errorMessage = message;
            
            controller.Dispose();

            // Act
            controller.PlayAudio();

            // Assert
            Assert.That(errorMessage, Is.Not.Null);
            Assert.That(errorMessage, Does.Contain("not initialized"));
        }

        [Test]
        public void PauseAudio_BeforePlay_DoesNotThrow()
        {
            // Arrange
            using (var controller = new AudioController(testWavFile))
            {
                // Act & Assert - Should handle gracefully
                Assert.DoesNotThrow(() => controller.PauseAudio());
            }
        }

        [Test]
        public void StopAudio_BeforePlay_DoesNotThrow()
        {
            // Arrange
            using (var controller = new AudioController(testWavFile))
            {
                // Act & Assert - Should handle gracefully
                Assert.DoesNotThrow(() => controller.StopAudio());
            }
        }
    }
}