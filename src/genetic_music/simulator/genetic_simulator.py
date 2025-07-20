"""
Genetic Simulator

Main class for running genetic algorithm evolution on audio data.
"""

import asyncio
import time
from typing import List, Optional, Dict, Any, Callable
from pathlib import Path
import numpy as np

from ..config.ga_config import GAConfig
from ..config.audio_config import AudioConfig
from ..audio.processor import AudioProcessor
from .chromosome import AudioChromosome


class GeneticSimulator:
    """
    Main genetic algorithm simulator for evolving audio data.
    
    This class orchestrates the entire evolution process, managing the population,
    selection, crossover, mutation, and fitness evaluation.
    """
    
    def __init__(self, ga_config: GAConfig, audio_config: AudioConfig):
        """
        Initialize the genetic simulator.
        
        Args:
            ga_config: Genetic algorithm configuration
            audio_config: Audio processing configuration
        """
        self.ga_config = ga_config
        self.audio_config = audio_config
        self.audio_processor = AudioProcessor(audio_config)
        
        # Evolution state
        self.population: List[AudioChromosome] = []
        self.generation = 0
        self.best_fitness_history: List[float] = []
        self.avg_fitness_history: List[float] = []
        self.best_chromosome: Optional[AudioChromosome] = None
        
        # Control flags
        self.is_running = False
        self.is_paused = False
        self.should_stop = False
        
        # Callbacks for monitoring
        self.progress_callback: Optional[Callable] = None
        self.generation_callback: Optional[Callable] = None
    
    def set_progress_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Set callback function for progress updates."""
        self.progress_callback = callback
    
    def set_generation_callback(self, callback: Callable[[int, List[AudioChromosome]], None]):
        """Set callback function for generation updates."""
        self.generation_callback = callback
    
    def initialize_population(self, target_audio: np.ndarray) -> None:
        """
        Initialize the population with random chromosomes.
        
        Args:
            target_audio: Target audio data to evolve towards
        """
        self.population = []
        
        for i in range(self.ga_config.population_size):
            chromosome = AudioChromosome.create_random(
                len(target_audio), 
                random_state=i
            )
            chromosome.calculate_fitness(target_audio)
            self.population.append(chromosome)
        
        self._update_statistics()
        print(f"Initialized population with {len(self.population)} individuals")
    
    def evolve(self, target_audio: np.ndarray, target_header: np.ndarray) -> Dict[str, Any]:
        """
        Run the complete evolution process.
        
        Args:
            target_audio: Target audio data
            target_header: WAV header data
            
        Returns:
            Dictionary with evolution results
        """
        print(f"Starting evolution with {self.ga_config.population_size} individuals")
        print(f"Target: {self.ga_config.max_generations} generations, {self.ga_config.fitness_threshold}% fitness threshold")
        
        # Initialize if not already done
        if not self.population:
            self.initialize_population(target_audio)
        
        start_time = time.time()
        self.is_running = True
        self.should_stop = False
        stagnant_generations = 0
        best_fitness = 0.0
        
        try:
            for gen in range(self.ga_config.max_generations):
                if self.should_stop:
                    break
                
                # Handle pause
                while self.is_paused and not self.should_stop:
                    time.sleep(0.1)
                
                self.generation = gen + 1
                
                # Evolve one generation
                self.population = self._evolve_generation(target_audio)
                self._update_statistics()
                
                current_best = max(chromo.fitness for chromo in self.population)
                
                # Check for improvement
                if current_best > best_fitness:
                    best_fitness = current_best
                    stagnant_generations = 0
                else:
                    stagnant_generations += 1
                
                # Progress callback
                if self.progress_callback:
                    progress_data = {
                        "generation": self.generation,
                        "progress": (self.generation / self.ga_config.max_generations) * 100,
                        "best_fitness": self.best_fitness_history[-1],
                        "avg_fitness": self.avg_fitness_history[-1],
                        "population_size": len(self.population),
                        "stagnant_generations": stagnant_generations
                    }
                    self.progress_callback(progress_data)
                
                # Generation callback
                if self.generation_callback:
                    self.generation_callback(self.generation, self.population.copy())
                
                # Check termination conditions
                if current_best >= self.ga_config.fitness_threshold:
                    print(f"Fitness threshold reached: {current_best:.2f}%")
                    break
                
                if stagnant_generations >= 20:
                    print(f"Population converged after {stagnant_generations} stagnant generations")
                    break
                
                # Print progress
                if self.generation % 10 == 0:
                    print(f"Generation {self.generation}: Best={current_best:.2f}%, Avg={self.avg_fitness_history[-1]:.2f}%")
        
        finally:
            self.is_running = False
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Final results
        results = {
            "generations_completed": self.generation,
            "final_best_fitness": self.best_fitness_history[-1] if self.best_fitness_history else 0,
            "final_avg_fitness": self.avg_fitness_history[-1] if self.avg_fitness_history else 0,
            "total_time": duration,
            "best_chromosome": self.best_chromosome,
            "fitness_history": {
                "best": self.best_fitness_history,
                "average": self.avg_fitness_history
            },
            "population_final": self.population
        }
        
        print(f"Evolution completed in {duration:.2f}s")
        print(f"Final best fitness: {results['final_best_fitness']:.2f}%")
        
        return results
    
    async def evolve_async(self, target_audio: np.ndarray, target_header: np.ndarray) -> Dict[str, Any]:
        """
        Asynchronous version of evolve method.
        
        Args:
            target_audio: Target audio data
            target_header: WAV header data
            
        Returns:
            Dictionary with evolution results
        """
        # Run evolution in a thread to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.evolve, target_audio, target_header)
    
    def _evolve_generation(self, target_audio: np.ndarray) -> List[AudioChromosome]:
        """
        Evolve one generation of the population.
        
        Args:
            target_audio: Target audio data for fitness calculation
            
        Returns:
            New population for the next generation
        """
        # Sort population by fitness (descending)
        self.population.sort(key=lambda x: x.fitness, reverse=True)
        
        # Elite selection
        elite_count = int(len(self.population) * self.ga_config.elite_size)
        elites = self.population[:elite_count]
        
        # Generate offspring
        offspring = []
        while len(offspring) < len(self.population) - elite_count:
            # Tournament selection
            parent1 = self._tournament_selection()
            parent2 = self._tournament_selection()
            
            # Crossover
            if np.random.random() < self.ga_config.crossover_rate:
                child1, child2 = parent1.crossover(parent2, "single_point")
            else:
                child1, child2 = parent1.copy(), parent2.copy()
            
            # Mutation
            if np.random.random() < self.ga_config.mutation_rate:
                child1 = child1.mutate(self.ga_config.mutation_rate)
            if np.random.random() < self.ga_config.mutation_rate:
                child2 = child2.mutate(self.ga_config.mutation_rate)
            
            # Calculate fitness
            child1.calculate_fitness(target_audio)
            child2.calculate_fitness(target_audio)
            
            offspring.extend([child1, child2])
        
        # Combine elites and offspring
        new_population = elites + offspring[:len(self.population) - elite_count]
        
        return new_population
    
    def _tournament_selection(self, tournament_size: int = 3) -> AudioChromosome:
        """
        Select a parent using tournament selection.
        
        Args:
            tournament_size: Number of individuals in tournament
            
        Returns:
            Selected chromosome
        """
        tournament = np.random.choice(self.population, size=tournament_size, replace=False)
        return max(tournament, key=lambda x: x.fitness)
    
    def _update_statistics(self):
        """Update fitness statistics and best chromosome."""
        if not self.population:
            return
        
        fitnesses = [chromo.fitness for chromo in self.population]
        best_fitness = max(fitnesses)
        avg_fitness = sum(fitnesses) / len(fitnesses)
        
        self.best_fitness_history.append(best_fitness)
        self.avg_fitness_history.append(avg_fitness)
        
        # Update best chromosome
        best_chromo = max(self.population, key=lambda x: x.fitness)
        if self.best_chromosome is None or best_chromo.fitness > self.best_chromosome.fitness:
            self.best_chromosome = best_chromo.copy()
    
    def pause(self):
        """Pause the evolution process."""
        self.is_paused = True
        print("Evolution paused")
    
    def resume(self):
        """Resume the evolution process."""
        self.is_paused = False
        print("Evolution resumed")
    
    def stop(self):
        """Stop the evolution process."""
        self.should_stop = True
        self.is_running = False
        print("Evolution stopped")
    
    def get_best_chromosome(self) -> Optional[AudioChromosome]:
        """Get the best chromosome found so far."""
        return self.best_chromosome
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get current evolution statistics."""
        return {
            "generation": self.generation,
            "population_size": len(self.population),
            "best_fitness": self.best_fitness_history[-1] if self.best_fitness_history else 0,
            "avg_fitness": self.avg_fitness_history[-1] if self.avg_fitness_history else 0,
            "best_fitness_history": self.best_fitness_history,
            "avg_fitness_history": self.avg_fitness_history,
            "is_running": self.is_running,
            "is_paused": self.is_paused
        }
    
    def save_best_result(self, output_path: Path, header_data: np.ndarray):
        """
        Save the best chromosome as an audio file.
        
        Args:
            output_path: Path to save the audio file
            header_data: WAV header data
        """
        if self.best_chromosome is None:
            raise ValueError("No best chromosome available")
        
        self.audio_processor.save_wav_file(
            self.best_chromosome.dna, 
            header_data, 
            output_path
        )
        print(f"Best result saved to: {output_path}")
    
    def save_generation_results(self, output_dir: Path, generation: int, 
                              header_data: np.ndarray, count: int = 5):
        """
        Save the top chromosomes from a generation.
        
        Args:
            output_dir: Directory to save files
            generation: Generation number
            header_data: WAV header data
            count: Number of top chromosomes to save
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Sort by fitness and take top N
        sorted_population = sorted(self.population, key=lambda x: x.fitness, reverse=True)
        top_chromosomes = sorted_population[:count]
        
        for i, chromo in enumerate(top_chromosomes):
            filename = f"gen_{generation:04d}_rank_{i+1:02d}_fitness_{chromo.fitness:.2f}.wav"
            file_path = output_dir / filename
            
            self.audio_processor.save_wav_file(chromo.dna, header_data, file_path)
        
        print(f"Saved top {len(top_chromosomes)} chromosomes from generation {generation}")