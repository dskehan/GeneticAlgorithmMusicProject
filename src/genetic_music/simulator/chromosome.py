"""Audio chromosome implementation for genetic algorithm."""

from typing import Optional, Union, List
import numpy as np
from dataclasses import dataclass
import copy


@dataclass
class AudioChromosome:
    """
    Represents an audio chromosome in the genetic algorithm.
    
    The chromosome encodes audio data as a sequence of bytes that can be
    evolved through genetic operations.
    """
    
    dna: np.ndarray  # Audio data as numpy array
    fitness: float = 0.0
    
    def __post_init__(self):
        """Validate and process the chromosome after initialization."""
        if not isinstance(self.dna, np.ndarray):
            self.dna = np.array(self.dna, dtype=np.uint8)
        
        if self.dna.dtype != np.uint8:
            self.dna = self.dna.astype(np.uint8)
    
    @classmethod
    def from_audio_data(cls, audio_data: Union[np.ndarray, bytes, List[int]], 
                       goal: Optional[np.ndarray] = None) -> "AudioChromosome":
        """
        Create a chromosome from audio data.
        
        Args:
            audio_data: Audio data as numpy array, bytes, or list
            goal: Optional goal sequence for immediate fitness calculation
            
        Returns:
            AudioChromosome instance
        """
        if isinstance(audio_data, bytes):
            dna = np.frombuffer(audio_data, dtype=np.uint8)
        elif isinstance(audio_data, list):
            dna = np.array(audio_data, dtype=np.uint8)
        else:
            dna = np.array(audio_data, dtype=np.uint8)
        
        chromosome = cls(dna=dna)
        
        if goal is not None:
            chromosome.calculate_fitness(goal)
        
        return chromosome
    
    @classmethod
    def create_random(cls, length: int, random_state: Optional[int] = None) -> "AudioChromosome":
        """
        Create a random chromosome of specified length.
        
        Args:
            length: Length of the chromosome
            random_state: Random seed for reproducibility
            
        Returns:
            Random AudioChromosome instance
        """
        if random_state is not None:
            np.random.seed(random_state)
        
        dna = np.random.randint(0, 256, size=length, dtype=np.uint8)
        return cls(dna=dna)
    
    def calculate_fitness(self, goal: np.ndarray) -> float:
        """
        Calculate fitness by comparing with goal sequence.
        
        Args:
            goal: Target sequence to compare against
            
        Returns:
            Fitness value as percentage (0.0-100.0)
            
        Raises:
            ValueError: If sequences have different lengths
        """
        if not isinstance(goal, np.ndarray):
            goal = np.array(goal, dtype=np.uint8)
        
        if len(self.dna) != len(goal):
            raise ValueError(
                f"Chromosome length ({len(self.dna)}) must match goal length ({len(goal)})"
            )
        
        if len(goal) == 0:
            self.fitness = 0.0
            return self.fitness
        
        # Calculate exact byte matches
        matches = np.sum(self.dna == goal)
        self.fitness = (matches / len(goal)) * 100.0
        
        return self.fitness
    
    def calculate_spectral_fitness(self, goal: np.ndarray, fft_size: int = 1024) -> float:
        """
        Calculate fitness based on spectral similarity.
        
        Args:
            goal: Target sequence
            fft_size: FFT window size
            
        Returns:
            Spectral fitness value
        """
        if len(self.dna) != len(goal):
            raise ValueError("Chromosome and goal must have same length")
        
        # Convert to float for FFT
        dna_float = self.dna.astype(np.float32) / 255.0
        goal_float = goal.astype(np.float32) / 255.0
        
        # Calculate spectrograms
        dna_fft = np.abs(np.fft.fft(dna_float, n=fft_size))
        goal_fft = np.abs(np.fft.fft(goal_float, n=fft_size))
        
        # Calculate similarity using normalized cross-correlation
        correlation = np.corrcoef(dna_fft, goal_fft)[0, 1]
        
        # Handle NaN case (when one signal is constant)
        if np.isnan(correlation):
            correlation = 0.0
        
        # Convert to percentage and ensure positive
        self.fitness = max(0.0, correlation * 100.0)
        return self.fitness
    
    def mutate(self, mutation_rate: float, random_state: Optional[int] = None) -> "AudioChromosome":
        """
        Create a mutated copy of the chromosome.
        
        Args:
            mutation_rate: Probability of mutation per gene (0.0-1.0)
            random_state: Random seed for reproducibility
            
        Returns:
            New mutated AudioChromosome
        """
        if not 0.0 <= mutation_rate <= 1.0:
            raise ValueError("Mutation rate must be between 0.0 and 1.0")
        
        if random_state is not None:
            np.random.seed(random_state)
        
        # Create a copy of the DNA
        mutated_dna = self.dna.copy()
        
        if len(mutated_dna) == 0:
            return AudioChromosome(dna=mutated_dna, fitness=self.fitness)
        
        # Determine which genes to mutate
        mutation_mask = np.random.random(len(mutated_dna)) < mutation_rate
        
        # Apply mutations (random byte values)
        num_mutations = np.sum(mutation_mask)
        if num_mutations > 0:
            mutated_dna[mutation_mask] = np.random.randint(0, 256, size=num_mutations, dtype=np.uint8)
        
        return AudioChromosome(dna=mutated_dna)
    
    def crossover(self, other: "AudioChromosome", crossover_type: str = "single_point",
                  random_state: Optional[int] = None) -> tuple["AudioChromosome", "AudioChromosome"]:
        """
        Perform crossover with another chromosome.
        
        Args:
            other: Other parent chromosome
            crossover_type: Type of crossover ("single_point", "two_point", "uniform")
            random_state: Random seed for reproducibility
            
        Returns:
            Tuple of two offspring chromosomes
        """
        if len(self.dna) != len(other.dna):
            raise ValueError("Chromosomes must have the same length for crossover")
        
        if random_state is not None:
            np.random.seed(random_state)
        
        length = len(self.dna)
        
        if crossover_type == "single_point":
            if length <= 1:
                # Can't crossover with length <= 1, return copies
                return self.copy(), other.copy()
            
            crossover_point = np.random.randint(1, length)
            
            offspring1_dna = np.concatenate([
                self.dna[:crossover_point],
                other.dna[crossover_point:]
            ])
            offspring2_dna = np.concatenate([
                other.dna[:crossover_point],
                self.dna[crossover_point:]
            ])
            
        elif crossover_type == "two_point":
            if length <= 2:
                return self.copy(), other.copy()
            
            point1, point2 = sorted(np.random.choice(range(1, length), size=2, replace=False))
            
            offspring1_dna = np.concatenate([
                self.dna[:point1],
                other.dna[point1:point2],
                self.dna[point2:]
            ])
            offspring2_dna = np.concatenate([
                other.dna[:point1],
                self.dna[point1:point2],
                other.dna[point2:]
            ])
            
        elif crossover_type == "uniform":
            mask = np.random.random(length) < 0.5
            
            offspring1_dna = np.where(mask, self.dna, other.dna)
            offspring2_dna = np.where(mask, other.dna, self.dna)
            
        else:
            raise ValueError(f"Unknown crossover type: {crossover_type}")
        
        return (
            AudioChromosome(dna=offspring1_dna),
            AudioChromosome(dna=offspring2_dna)
        )
    
    def copy(self) -> "AudioChromosome":
        """Create a deep copy of the chromosome."""
        return AudioChromosome(dna=self.dna.copy(), fitness=self.fitness)
    
    def to_bytes(self) -> bytes:
        """Convert chromosome DNA to bytes."""
        return self.dna.tobytes()
    
    def to_audio_data(self) -> np.ndarray:
        """Convert chromosome to audio data format."""
        return self.dna.copy()
    
    def __len__(self) -> int:
        """Return the length of the chromosome."""
        return len(self.dna)
    
    def __eq__(self, other) -> bool:
        """Check equality with another chromosome."""
        if not isinstance(other, AudioChromosome):
            return False
        return np.array_equal(self.dna, other.dna)
    
    def __str__(self) -> str:
        """String representation of the chromosome."""
        return f"AudioChromosome(length={len(self.dna)}, fitness={self.fitness:.2f}%)"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return (
            f"AudioChromosome(dna={self.dna[:10]}{'...' if len(self.dna) > 10 else ''}, "
            f"fitness={self.fitness:.2f}%, length={len(self.dna)})"
        )
    
    def get_similarity_to(self, other: "AudioChromosome") -> float:
        """
        Calculate similarity percentage to another chromosome.
        
        Args:
            other: Other chromosome to compare with
            
        Returns:
            Similarity percentage (0.0-100.0)
        """
        if len(self.dna) != len(other.dna):
            return 0.0
        
        if len(self.dna) == 0:
            return 100.0
        
        matches = np.sum(self.dna == other.dna)
        return (matches / len(self.dna)) * 100.0
    
    def get_diversity_measure(self) -> float:
        """
        Calculate diversity measure of the chromosome.
        
        Returns:
            Diversity value (higher = more diverse)
        """
        if len(self.dna) == 0:
            return 0.0
        
        # Calculate entropy as a diversity measure
        unique_values, counts = np.unique(self.dna, return_counts=True)
        probabilities = counts / len(self.dna)
        entropy = -np.sum(probabilities * np.log2(probabilities + 1e-8))
        
        # Normalize to 0-1 range (max entropy for 8-bit values is log2(256) = 8)
        return entropy / 8.0