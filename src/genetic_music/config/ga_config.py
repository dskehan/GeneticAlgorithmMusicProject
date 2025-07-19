"""Genetic Algorithm configuration management."""

from typing import List, Optional
from dataclasses import dataclass, field
from pathlib import Path
import toml


@dataclass
class GAConfig:
    """Configuration class for genetic algorithm parameters."""
    
    # Population parameters
    population_size: int = 500
    elite_size: float = 0.1  # Percentage of population to preserve as elites
    
    # Genetic operators
    mutation_rate: float = 0.02  # Probability of mutation (0.0-1.0)
    crossover_rate: float = 0.8  # Probability of crossover (0.0-1.0)
    
    # Selection parameters
    tournament_size: int = 3
    selection_method: str = "tournament"  # "tournament", "roulette", "rank"
    
    # Termination criteria
    max_generations: int = 100
    fitness_threshold: float = 95.0  # Stop when fitness reaches this value
    convergence_threshold: int = 10  # Stop after N generations without improvement
    stagnation_limit: int = 20  # Stop if no improvement for N generations
    
    # Output configuration
    output_every_generation: bool = False
    milestone_generations: List[int] = field(
        default_factory=lambda: [2, 5, 10, 15, 25, 35, 50, 65, 75, 85, 90, 95, 97]
    )
    save_best_only: bool = True
    
    # Performance parameters
    parallel_fitness: bool = True
    max_workers: Optional[int] = None  # None = auto-detect
    
    # Randomization
    random_seed: Optional[int] = None
    
    # Audio-specific parameters
    audio_chunk_size: int = 1024
    fitness_function: str = "byte_similarity"  # "byte_similarity", "spectral", "perceptual"
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self.validate()
    
    def validate(self) -> None:
        """Validate configuration parameters."""
        errors = []
        
        # Population validation
        if self.population_size <= 0:
            errors.append("Population size must be positive")
        
        if not 0.0 <= self.elite_size <= 1.0:
            errors.append("Elite size must be between 0.0 and 1.0")
        
        # Rate validation
        if not 0.0 <= self.mutation_rate <= 1.0:
            errors.append("Mutation rate must be between 0.0 and 1.0")
        
        if not 0.0 <= self.crossover_rate <= 1.0:
            errors.append("Crossover rate must be between 0.0 and 1.0")
        
        # Selection validation
        if self.tournament_size <= 0:
            errors.append("Tournament size must be positive")
        
        if self.tournament_size > self.population_size:
            errors.append("Tournament size cannot exceed population size")
        
        # Termination validation
        if self.max_generations <= 0:
            errors.append("Max generations must be positive")
        
        if not 0.0 <= self.fitness_threshold <= 100.0:
            errors.append("Fitness threshold must be between 0.0 and 100.0")
        
        if self.convergence_threshold <= 0:
            errors.append("Convergence threshold must be positive")
        
        # Audio validation
        if self.audio_chunk_size <= 0:
            errors.append("Audio chunk size must be positive")
        
        if self.fitness_function not in ["byte_similarity", "spectral", "perceptual"]:
            errors.append("Invalid fitness function")
        
        if errors:
            raise ValueError(f"Invalid configuration: {'; '.join(errors)}")
    
    @classmethod
    def create_default(cls) -> "GAConfig":
        """Create a configuration with default values."""
        return cls()
    
    @classmethod
    def create_for_testing(cls) -> "GAConfig":
        """Create a configuration optimized for testing with smaller values."""
        return cls(
            population_size=50,
            max_generations=10,
            mutation_rate=0.05,
            milestone_generations=[10, 25, 50, 75, 90],
            convergence_threshold=5,
            stagnation_limit=10,
        )
    
    @classmethod
    def create_fast(cls) -> "GAConfig":
        """Create a configuration optimized for fast execution."""
        return cls(
            population_size=100,
            max_generations=50,
            mutation_rate=0.01,
            elite_size=0.2,
            convergence_threshold=5,
            parallel_fitness=True,
        )
    
    @classmethod
    def create_thorough(cls) -> "GAConfig":
        """Create a configuration for thorough, high-quality evolution."""
        return cls(
            population_size=1000,
            max_generations=500,
            mutation_rate=0.005,
            elite_size=0.05,
            convergence_threshold=25,
            stagnation_limit=50,
            fitness_threshold=99.0,
        )
    
    @classmethod
    def from_file(cls, file_path: Path) -> "GAConfig":
        """Load configuration from a TOML file."""
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = toml.load(f)
        
        # Extract GA config section
        ga_data = data.get('genetic_algorithm', {})
        return cls(**ga_data)
    
    def to_file(self, file_path: Path) -> None:
        """Save configuration to a TOML file."""
        config_data = {
            'genetic_algorithm': {
                'population_size': self.population_size,
                'elite_size': self.elite_size,
                'mutation_rate': self.mutation_rate,
                'crossover_rate': self.crossover_rate,
                'tournament_size': self.tournament_size,
                'selection_method': self.selection_method,
                'max_generations': self.max_generations,
                'fitness_threshold': self.fitness_threshold,
                'convergence_threshold': self.convergence_threshold,
                'stagnation_limit': self.stagnation_limit,
                'output_every_generation': self.output_every_generation,
                'milestone_generations': self.milestone_generations,
                'save_best_only': self.save_best_only,
                'parallel_fitness': self.parallel_fitness,
                'max_workers': self.max_workers,
                'random_seed': self.random_seed,
                'audio_chunk_size': self.audio_chunk_size,
                'fitness_function': self.fitness_function,
            }
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            toml.dump(config_data, f)
    
    def copy(self, **changes) -> "GAConfig":
        """Create a copy of the configuration with specified changes."""
        import copy
        new_config = copy.deepcopy(self)
        for key, value in changes.items():
            if hasattr(new_config, key):
                setattr(new_config, key, value)
            else:
                raise AttributeError(f"GAConfig has no attribute '{key}'")
        new_config.validate()
        return new_config
    
    def __str__(self) -> str:
        """String representation of the configuration."""
        return (
            f"GAConfig(population={self.population_size}, "
            f"generations={self.max_generations}, "
            f"mutation_rate={self.mutation_rate}, "
            f"fitness_threshold={self.fitness_threshold})"
        )