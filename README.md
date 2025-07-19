# Genetic Algorithm Music Project (Python)

A Python implementation of a genetic algorithm that evolves audio files using evolutionary computation principles. This project demonstrates how genetic algorithms can be applied to audio manipulation and generation.

## 🎵 Overview

This application uses genetic algorithms to evolve WAV audio files by treating audio data as chromosomes and applying genetic operations like selection, crossover, and mutation to generate new audio variations that converge toward a target audio file.

## ✨ Features

- **Genetic Algorithm Core**: Complete genetic algorithm implementation with configurable parameters
- **Audio Processing**: WAV file reading, writing, and manipulation using Python audio libraries
- **Configurable Evolution**: Customizable population size, mutation rates, and fitness functions
- **Audio Playback**: Built-in audio playback capabilities for listening to evolved generations
- **Progress Tracking**: Real-time evolution progress monitoring and statistics
- **Batch Processing**: Process multiple audio files simultaneously
- **Visualization**: Plot fitness evolution and population statistics
- **CLI Interface**: Command-line interface for batch processing
- **GUI Interface**: User-friendly graphical interface using tkinter
- **Comprehensive Testing**: Full test suite with pytest

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd genetic_algorithm_music_python

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

### Basic Usage

#### Command Line Interface

```bash
# Evolve a single audio file
python -m genetic_music.cli evolve input.wav --output output_dir --generations 100

# Use custom parameters
python -m genetic_music.cli evolve input.wav \
    --population-size 500 \
    --mutation-rate 0.05 \
    --output output_dir \
    --generations 50
```

#### Graphical Interface

```bash
# Launch the GUI
python -m genetic_music.gui
```

#### Python API

```python
from genetic_music import GeneticSimulator, AudioConfig

# Create configuration
config = AudioConfig(
    population_size=200,
    mutation_rate=0.02,
    fitness_threshold=95.0
)

# Initialize simulator
simulator = GeneticSimulator(config)

# Load and evolve audio
result = simulator.evolve("input.wav", generations=100)

# Save the best result
result.save_best("evolved_audio.wav")
```

## 📁 Project Structure

```
genetic_algorithm_music_python/
├── src/genetic_music/           # Main package
│   ├── __init__.py
│   ├── simulator/              # Genetic algorithm core
│   │   ├── __init__.py
│   │   ├── chromosome.py       # Audio chromosome representation
│   │   ├── genetic_simulator.py # Main GA implementation
│   │   ├── population.py       # Population management
│   │   └── operators.py        # Genetic operators
│   ├── audio/                  # Audio processing
│   │   ├── __init__.py
│   │   ├── processor.py        # Audio file I/O
│   │   ├── player.py          # Audio playback
│   │   └── analyzer.py        # Audio analysis tools
│   ├── config/                 # Configuration management
│   │   ├── __init__.py
│   │   ├── audio_config.py     # Audio-specific config
│   │   └── ga_config.py        # GA parameters config
│   ├── gui/                    # Graphical interface
│   │   ├── __init__.py
│   │   ├── main_window.py      # Main GUI window
│   │   ├── controls.py         # GUI controls
│   │   └── visualizer.py       # Audio visualization
│   ├── cli.py                  # Command-line interface
│   └── utils.py               # Utility functions
├── tests/                      # Test suite
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── conftest.py            # Test configuration
├── examples/                   # Example scripts
├── docs/                       # Documentation
├── requirements.txt            # Dependencies
├── setup.py                   # Package setup
├── pytest.ini                # Test configuration
└── .gitignore                 # Git ignore rules
```

## 🔧 Configuration

### Genetic Algorithm Parameters

```python
# Default configuration
config = GAConfig(
    population_size=200,         # Number of individuals per generation
    mutation_rate=0.02,          # Probability of mutation (0.0-1.0)
    crossover_rate=0.8,          # Probability of crossover (0.0-1.0)
    elite_size=0.1,              # Percentage of elite individuals to preserve
    tournament_size=3,           # Tournament selection size
    max_generations=100,         # Maximum number of generations
    fitness_threshold=95.0,      # Stop when fitness reaches this value
    convergence_threshold=10     # Stop after N generations without improvement
)
```

### Audio Parameters

```python
# Audio processing configuration
audio_config = AudioConfig(
    sample_rate=44100,           # Audio sample rate
    bit_depth=16,                # Audio bit depth
    channels=1,                  # Number of audio channels (1=mono, 2=stereo)
    chunk_size=1024,             # Audio processing chunk size
    output_format='wav',         # Output audio format
    normalize=True               # Normalize audio levels
)
```

## 🧬 How It Works

### 1. **Chromosome Representation**
Audio data is represented as chromosomes where each byte of the audio file (excluding the header) becomes a gene in the chromosome.

### 2. **Fitness Function**
Fitness is calculated by comparing the evolved audio chromosome with the target audio:
- **Exact Match**: Percentage of bytes that exactly match the target
- **Similarity Score**: Advanced similarity metrics using audio features
- **Perceptual Distance**: Psychoacoustic similarity measures

### 3. **Genetic Operations**
- **Selection**: Tournament selection chooses parents based on fitness
- **Crossover**: Single-point or uniform crossover combines parent chromosomes
- **Mutation**: Random bit-flipping with configurable mutation rate
- **Elitism**: Best individuals survive to the next generation

### 4. **Evolution Process**
```
1. Load target audio file
2. Generate initial random population
3. Evaluate fitness of each individual
4. Select parents for reproduction
5. Apply crossover and mutation
6. Replace old population with offspring
7. Repeat until convergence or max generations
```

## 📊 Monitoring and Visualization

### Real-time Statistics
- Current generation number
- Best fitness score
- Average population fitness
- Convergence rate
- Estimated time to completion

### Visualization Features
- Fitness evolution graphs
- Population diversity charts
- Audio waveform comparisons
- Spectrogram analysis

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=genetic_music

# Run specific test categories
pytest tests/unit/
pytest tests/integration/

# Run with verbose output
pytest -v
```

## 📚 Examples

### Basic Evolution Example

```python
from genetic_music import GeneticSimulator, GAConfig, AudioConfig

# Configure the genetic algorithm
ga_config = GAConfig(
    population_size=100,
    mutation_rate=0.01,
    max_generations=50
)

audio_config = AudioConfig(
    sample_rate=22050,  # Lower sample rate for faster processing
    channels=1
)

# Create and run simulator
simulator = GeneticSimulator(ga_config, audio_config)
result = simulator.evolve("target_audio.wav")

# Access results
print(f"Best fitness: {result.best_fitness:.2f}%")
print(f"Generations: {result.generations}")
print(f"Time elapsed: {result.time_elapsed:.2f}s")

# Save evolved audio
result.save_best("evolved_result.wav")
```

### Batch Processing Example

```python
from genetic_music import BatchProcessor

# Process multiple files
processor = BatchProcessor(
    input_dir="audio_samples/",
    output_dir="evolved_samples/",
    config=config
)

results = processor.process_all(max_workers=4)
```

## 🎛️ Advanced Features

### Custom Fitness Functions

```python
def custom_fitness_function(evolved_audio, target_audio):
    """Custom fitness function using spectral similarity."""
    # Implement your custom fitness calculation
    return similarity_score

simulator = GeneticSimulator(config, fitness_function=custom_fitness_function)
```

### Audio Effects Integration

```python
# Apply effects during evolution
config.enable_effects([
    'reverb',
    'chorus',
    'distortion'
])
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- [Original C# Implementation](../genetic-algorithm-music-csharp)
- [Genetic Algorithm Papers](docs/references.md)
- [Audio Processing Libraries](docs/audio-libraries.md)

## 📧 Support

For questions, bug reports, or feature requests, please open an issue on GitHub.

## 🏆 Acknowledgments

- Inspired by genetic algorithm research in audio processing
- Built with Python's rich ecosystem of audio and scientific libraries
- Thanks to the open-source community for excellent tools and libraries
