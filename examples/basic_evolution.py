#!/usr/bin/env python3
"""
Basic Evolution Example

This example demonstrates how to use the genetic algorithm music project
to evolve an audio file towards a target.
"""

import sys
import time
from pathlib import Path

# Add the src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from genetic_music import GAConfig, AudioConfig, GeneticSimulator
from genetic_music.audio import AudioProcessor
from genetic_music.simulator import AudioChromosome
import numpy as np


def create_test_audio_file(filename: str = "test_target.wav", duration: float = 1.0):
    """Create a simple test audio file for demonstration."""
    
    # Create audio configuration
    audio_config = AudioConfig.create_default()
    processor = AudioProcessor(audio_config)
    
    # Generate a simple sine wave
    sample_rate = audio_config.sample_rate
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    frequency = 440.0  # A4 note
    
    # Generate sine wave
    audio_data = np.sin(frequency * 2 * np.pi * t) * 0.5
    
    # Save the test file
    processor.save_audio_with_soundfile(audio_data, filename)
    print(f"Created test audio file: {filename}")
    
    return filename


def basic_evolution_example():
    """Demonstrate basic genetic algorithm evolution of audio."""
    
    print("🎵 Genetic Algorithm Music Evolution Example")
    print("=" * 50)
    
    # Step 1: Create configurations
    print("\n1. Setting up configurations...")
    
    # Create a fast configuration for demo purposes
    ga_config = GAConfig.create_fast()
    audio_config = AudioConfig.create_fast()
    
    print(f"   GA Config: {ga_config}")
    print(f"   Audio Config: {audio_config}")
    
    # Step 2: Create or use a test audio file
    print("\n2. Preparing audio file...")
    
    test_file = "test_target.wav"
    if not Path(test_file).exists():
        create_test_audio_file(test_file, duration=0.5)  # Short for demo
    
    # Step 3: Load the target audio
    print("\n3. Loading target audio...")
    
    processor = AudioProcessor(audio_config)
    try:
        audio_data, header_data = processor.load_wav_file(test_file)
        print(f"   Loaded {len(audio_data)} bytes of audio data")
        print(f"   Header size: {len(header_data)} bytes")
    except Exception as e:
        print(f"   Error loading audio: {e}")
        print("   Creating synthetic data for demonstration...")
        # Create synthetic data
        audio_data = np.random.randint(0, 256, size=1000, dtype=np.uint8)
        header_data = np.random.randint(0, 256, size=44, dtype=np.uint8)
    
    # Step 4: Create target chromosome
    print("\n4. Creating target chromosome...")
    
    target_chromosome = AudioChromosome.from_audio_data(audio_data)
    target_chromosome.calculate_fitness(audio_data)  # Perfect fitness = 100%
    print(f"   Target chromosome: {target_chromosome}")
    
    # Step 5: Create initial population
    print("\n5. Generating initial population...")
    
    population = []
    for i in range(ga_config.population_size):
        # Create random chromosome of same length as target
        random_chromosome = AudioChromosome.create_random(
            len(audio_data), 
            random_state=i  # For reproducibility
        )
        random_chromosome.calculate_fitness(audio_data)
        population.append(random_chromosome)
    
    # Calculate initial statistics
    fitnesses = [chromo.fitness for chromo in population]
    best_fitness = max(fitnesses)
    avg_fitness = sum(fitnesses) / len(fitnesses)
    
    print(f"   Population size: {len(population)}")
    print(f"   Initial best fitness: {best_fitness:.2f}%")
    print(f"   Initial average fitness: {avg_fitness:.2f}%")
    
    # Step 6: Simple evolution loop (demonstration)
    print("\n6. Running evolution...")
    
    start_time = time.time()
    
    for generation in range(min(10, ga_config.max_generations)):  # Limited for demo
        # Simple selection: keep best half
        population.sort(key=lambda x: x.fitness, reverse=True)
        survivors = population[:len(population)//2]
        
        # Simple reproduction: create offspring
        offspring = []
        while len(offspring) < len(population) - len(survivors):
            # Select two random parents from survivors
            parent1 = np.random.choice(survivors)
            parent2 = np.random.choice(survivors)
            
            # Create offspring through mutation (simplified)
            child = parent1.mutate(ga_config.mutation_rate)
            child.calculate_fitness(audio_data)
            offspring.append(child)
        
        # New population
        population = survivors + offspring
        
        # Calculate statistics
        fitnesses = [chromo.fitness for chromo in population]
        best_fitness = max(fitnesses)
        avg_fitness = sum(fitnesses) / len(fitnesses)
        
        print(f"   Generation {generation + 1:2d}: "
              f"Best={best_fitness:6.2f}%, Avg={avg_fitness:6.2f}%")
        
        # Early termination if we reach the threshold
        if best_fitness >= ga_config.fitness_threshold:
            print(f"   🎉 Reached fitness threshold of {ga_config.fitness_threshold}%!")
            break
    
    elapsed_time = time.time() - start_time
    
    # Step 7: Results
    print("\n7. Evolution Results")
    print("-" * 30)
    
    best_chromosome = max(population, key=lambda x: x.fitness)
    print(f"   Final best fitness: {best_chromosome.fitness:.2f}%")
    print(f"   Evolution time: {elapsed_time:.2f} seconds")
    print(f"   Generations completed: {generation + 1}")
    
    # Step 8: Save result (optional)
    print("\n8. Saving results...")
    
    try:
        output_path = Path("evolved_result.wav")
        processor.save_wav_file(best_chromosome.dna, header_data, output_path)
        print(f"   Saved evolved audio to: {output_path}")
    except Exception as e:
        print(f"   Error saving result: {e}")
    
    print("\n✨ Evolution complete!")
    
    # Clean up test file
    try:
        Path(test_file).unlink(missing_ok=True)
        print(f"   Cleaned up test file: {test_file}")
    except Exception:
        pass


def chromosome_demonstration():
    """Demonstrate chromosome operations."""
    
    print("\n" + "=" * 50)
    print("🧬 Chromosome Operations Demonstration")
    print("=" * 50)
    
    # Create test chromosomes
    print("\n1. Creating test chromosomes...")
    
    # Create some test data
    data1 = np.array([100, 150, 200, 50, 75], dtype=np.uint8)
    data2 = np.array([100, 140, 200, 60, 75], dtype=np.uint8)
    goal = np.array([100, 150, 200, 50, 75], dtype=np.uint8)
    
    chromo1 = AudioChromosome.from_audio_data(data1, goal)
    chromo2 = AudioChromosome.from_audio_data(data2, goal)
    
    print(f"   Chromosome 1: {chromo1}")
    print(f"   Chromosome 2: {chromo2}")
    
    # Demonstrate fitness calculation
    print("\n2. Fitness calculation...")
    print(f"   Chromosome 1 fitness: {chromo1.fitness:.2f}%")
    print(f"   Chromosome 2 fitness: {chromo2.fitness:.2f}%")
    
    # Demonstrate similarity
    similarity = chromo1.get_similarity_to(chromo2)
    print(f"   Similarity between chromosomes: {similarity:.2f}%")
    
    # Demonstrate mutation
    print("\n3. Mutation demonstration...")
    mutated = chromo1.mutate(mutation_rate=0.4, random_state=42)
    mutated.calculate_fitness(goal)
    
    print(f"   Original:  {chromo1}")
    print(f"   Mutated:   {mutated}")
    
    # Demonstrate crossover
    print("\n4. Crossover demonstration...")
    offspring1, offspring2 = chromo1.crossover(chromo2, random_state=42)
    offspring1.calculate_fitness(goal)
    offspring2.calculate_fitness(goal)
    
    print(f"   Parent 1:   {chromo1}")
    print(f"   Parent 2:   {chromo2}")
    print(f"   Offspring 1: {offspring1}")
    print(f"   Offspring 2: {offspring2}")


if __name__ == "__main__":
    try:
        basic_evolution_example()
        chromosome_demonstration()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Evolution interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during evolution: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎵 Thank you for trying the Genetic Algorithm Music Project!")