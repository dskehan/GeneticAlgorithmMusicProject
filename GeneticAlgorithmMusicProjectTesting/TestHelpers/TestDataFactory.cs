using System.IO;

namespace GeneticAlgorithmMusicProjectTesting.TestHelpers
{
    /// <summary>
    /// Factory class for creating test data and helper methods for unit tests.
    /// </summary>
    public static class TestDataFactory
    {
        /// <summary>
        /// Creates a simple test goal sequence.
        /// </summary>
        /// <param name="length">Length of the goal sequence.</param>
        /// <returns>A char array representing a test goal.</returns>
        public static char[] CreateTestGoal(int length = 10)
        {
            char[] goal = new char[length];
            for (int i = 0; i < length; i++)
            {
                goal[i] = (char)('A' + (i % 26));
            }
            return goal;
        }

        /// <summary>
        /// Creates a test DNA sequence that matches the goal.
        /// </summary>
        /// <param name="goal">The goal sequence to match.</param>
        /// <returns>A char array that exactly matches the goal.</returns>
        public static char[] CreatePerfectMatchDNA(char[] goal)
        {
            return (char[])goal.Clone();
        }

        /// <summary>
        /// Creates a test DNA sequence that partially matches the goal.
        /// </summary>
        /// <param name="goal">The goal sequence.</param>
        /// <param name="matchPercentage">Percentage of positions that should match (0.0 to 1.0).</param>
        /// <returns>A char array that partially matches the goal.</returns>
        public static char[] CreatePartialMatchDNA(char[] goal, double matchPercentage = 0.5)
        {
            char[] dna = new char[goal.Length];
            int matchCount = (int)(goal.Length * matchPercentage);
            
            for (int i = 0; i < goal.Length; i++)
            {
                if (i < matchCount)
                {
                    dna[i] = goal[i]; // Match
                }
                else
                {
                    dna[i] = (char)('Z' - (i % 26)); // Different character
                }
            }
            return dna;
        }

        /// <summary>
        /// Creates a test DNA sequence that doesn't match the goal at all.
        /// </summary>
        /// <param name="goal">The goal sequence.</param>
        /// <returns>A char array that doesn't match the goal.</returns>
        public static char[] CreateNoMatchDNA(char[] goal)
        {
            char[] dna = new char[goal.Length];
            for (int i = 0; i < goal.Length; i++)
            {
                dna[i] = (char)('Z' - (i % 26)); // Ensure it's different
            }
            return dna;
        }

        /// <summary>
        /// Creates a temporary WAV file for testing.
        /// </summary>
        /// <returns>Path to the temporary WAV file.</returns>
        public static string CreateTestWavFile()
        {
            string tempPath = Path.GetTempFileName();
            string wavPath = Path.ChangeExtension(tempPath, ".wav");
            
            // Create a minimal WAV file structure
            byte[] wavHeader = CreateMinimalWavHeader();
            byte[] audioData = new byte[100]; // Small amount of test audio data
            
            // Fill audio data with test pattern
            for (int i = 0; i < audioData.Length; i++)
            {
                audioData[i] = (byte)(i % 256);
            }
            
            using (var fileStream = new FileStream(wavPath, FileMode.Create))
            {
                fileStream.Write(wavHeader, 0, wavHeader.Length);
                fileStream.Write(audioData, 0, audioData.Length);
            }
            
            return wavPath;
        }

        /// <summary>
        /// Creates a minimal WAV file header for testing.
        /// </summary>
        /// <returns>Byte array representing a minimal WAV header.</returns>
        private static byte[] CreateMinimalWavHeader()
        {
            // This is a simplified WAV header for testing purposes
            byte[] header = new byte[44];
            
            // "RIFF" chunk descriptor
            header[0] = (byte)'R';
            header[1] = (byte)'I';
            header[2] = (byte)'F';
            header[3] = (byte)'F';
            
            // File size (will be updated)
            BitConverter.GetBytes(100 + 36).CopyTo(header, 4);
            
            // "WAVE" format
            header[8] = (byte)'W';
            header[9] = (byte)'A';
            header[10] = (byte)'V';
            header[11] = (byte)'E';
            
            // "fmt " sub-chunk
            header[12] = (byte)'f';
            header[13] = (byte)'m';
            header[14] = (byte)'t';
            header[15] = (byte)' ';
            
            // Sub-chunk size (16 for PCM)
            BitConverter.GetBytes(16).CopyTo(header, 16);
            
            // Audio format (1 for PCM)
            BitConverter.GetBytes((short)1).CopyTo(header, 20);
            
            // Number of channels (1 for mono)
            BitConverter.GetBytes((short)1).CopyTo(header, 22);
            
            // Sample rate (44100 Hz)
            BitConverter.GetBytes(44100).CopyTo(header, 24);
            
            // Byte rate
            BitConverter.GetBytes(44100 * 1 * 1).CopyTo(header, 28);
            
            // Block align
            BitConverter.GetBytes((short)(1 * 1)).CopyTo(header, 32);
            
            // Bits per sample
            BitConverter.GetBytes((short)8).CopyTo(header, 34);
            
            // "data" sub-chunk
            header[36] = (byte)'d';
            header[37] = (byte)'a';
            header[38] = (byte)'t';
            header[39] = (byte)'a';
            
            // Data size
            BitConverter.GetBytes(100).CopyTo(header, 40);
            
            return header;
        }

        /// <summary>
        /// Cleans up a temporary test file.
        /// </summary>
        /// <param name="filePath">Path to the file to delete.</param>
        public static void CleanupTestFile(string filePath)
        {
            try
            {
                if (File.Exists(filePath))
                {
                    File.Delete(filePath);
                }
            }
            catch
            {
                // Ignore cleanup errors in tests
            }
        }

        /// <summary>
        /// Creates a test configuration with known values.
        /// </summary>
        /// <returns>A GeneticAlgorithmConfig instance for testing.</returns>
        public static GeneticAlgorithmConfig CreateTestConfig()
        {
            return new GeneticAlgorithmConfig
            {
                PopulationSize = 10,
                MutationFactor = 2,
                Milestones = new List<int> { 25, 50, 75, 90 }
            };
        }
    }
}