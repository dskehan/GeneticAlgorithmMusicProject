"""
Evolution Service

Handles background genetic algorithm evolution with real-time progress updates.
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import numpy as np

import sys
sys.path.append('../../src')
from genetic_music import GAConfig, AudioConfig
from genetic_music.audio import AudioProcessor
from genetic_music.simulator import AudioChromosome


class EvolutionService:
    """Service for managing genetic algorithm evolution jobs."""
    
    def __init__(self):
        self.active_jobs: Dict[str, Dict] = {}
        self.job_history: Dict[str, Dict] = {}
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
    
    async def run_evolution(self, job_id: str, file_path: str, params: Any, websocket_manager: Any):
        """Run genetic algorithm evolution in the background."""
        
        # Initialize job status
        self.active_jobs[job_id] = {
            "status": "initializing",
            "progress": 0.0,
            "generation": 0,
            "best_fitness": 0.0,
            "avg_fitness": 0.0,
            "start_time": datetime.now(),
            "file_path": file_path,
            "params": params,
            "paused": False,
            "stopped": False
        }
        
        try:
            await self._broadcast_update(job_id, websocket_manager)
            
            # Load audio file
            await self._update_status(job_id, "loading_audio", websocket_manager)
            
            # Create audio processor
            audio_config = AudioConfig.create_fast()
            processor = AudioProcessor(audio_config)
            
            # Load the audio file
            audio_data, header_data = processor.load_wav_file(file_path)
            
            await self._update_status(job_id, "creating_population", websocket_manager)
            
            # Create GA configuration
            ga_config = GAConfig(
                population_size=params.population_size,
                mutation_rate=params.mutation_rate,
                crossover_rate=params.crossover_rate,
                max_generations=params.max_generations,
                fitness_threshold=params.fitness_threshold,
                elite_size=params.elite_size
            )
            
            # Initialize population
            population = []
            for i in range(ga_config.population_size):
                chromosome = AudioChromosome.create_random(len(audio_data), random_state=i)
                chromosome.calculate_fitness(audio_data)
                population.append(chromosome)
            
            # Calculate initial statistics
            fitnesses = [chromo.fitness for chromo in population]
            best_fitness = max(fitnesses)
            avg_fitness = sum(fitnesses) / len(fitnesses)
            
            self.active_jobs[job_id].update({
                "status": "evolving",
                "best_fitness": best_fitness,
                "avg_fitness": avg_fitness,
                "population_size": len(population)
            })
            
            await self._broadcast_update(job_id, websocket_manager)
            
            # Create results directory for this job
            job_results_dir = self.results_dir / job_id
            job_results_dir.mkdir(exist_ok=True)
            
            # Evolution loop
            generation = 0
            stagnant_generations = 0
            best_ever_fitness = best_fitness
            
            while generation < ga_config.max_generations:
                generation += 1
                
                # Check for pause/stop
                if self.active_jobs[job_id]["stopped"]:
                    break
                
                while self.active_jobs[job_id]["paused"]:
                    await asyncio.sleep(0.1)
                
                # Selection and reproduction
                population = await self._evolve_generation(
                    population, audio_data, ga_config, params
                )
                
                # Calculate statistics
                fitnesses = [chromo.fitness for chromo in population]
                best_fitness = max(fitnesses)
                avg_fitness = sum(fitnesses) / len(fitnesses)
                
                # Check for improvement
                if best_fitness > best_ever_fitness:
                    best_ever_fitness = best_fitness
                    stagnant_generations = 0
                else:
                    stagnant_generations += 1
                
                # Update progress
                progress = generation / ga_config.max_generations * 100
                
                self.active_jobs[job_id].update({
                    "generation": generation,
                    "progress": progress,
                    "best_fitness": best_fitness,
                    "avg_fitness": avg_fitness,
                    "stagnant_generations": stagnant_generations
                })
                
                # Broadcast update
                await self._broadcast_update(job_id, websocket_manager)
                
                # Save generation if requested
                if generation in params.save_generations:
                    await self._save_generation(
                        job_id, generation, population, audio_data, 
                        header_data, processor, job_results_dir
                    )
                
                # Check termination conditions
                if best_fitness >= ga_config.fitness_threshold:
                    await self._update_status(job_id, "fitness_threshold_reached", websocket_manager)
                    break
                
                if stagnant_generations >= 20:  # Convergence detection
                    await self._update_status(job_id, "converged", websocket_manager)
                    break
                
                # Small delay to prevent overwhelming
                await asyncio.sleep(0.01)
            
            # Save final results
            await self._save_final_results(
                job_id, population, audio_data, header_data, 
                processor, job_results_dir, generation
            )
            
            # Mark as completed
            self.active_jobs[job_id].update({
                "status": "completed",
                "end_time": datetime.now(),
                "final_generation": generation,
                "final_best_fitness": best_fitness
            })
            
            # Move to history
            self.job_history[job_id] = self.active_jobs.pop(job_id)
            
            await self._broadcast_update(job_id, websocket_manager)
            
        except Exception as e:
            # Handle errors
            self.active_jobs[job_id].update({
                "status": "error",
                "error": str(e),
                "end_time": datetime.now()
            })
            
            self.job_history[job_id] = self.active_jobs.pop(job_id)
            await self._broadcast_update(job_id, websocket_manager)
    
    async def _evolve_generation(self, population: List, audio_data: np.ndarray, 
                                ga_config: GAConfig, params: Any) -> List:
        """Evolve one generation of the population."""
        
        # Sort by fitness (descending)
        population.sort(key=lambda x: x.fitness, reverse=True)
        
        # Elite selection
        elite_count = int(len(population) * ga_config.elite_size)
        elites = population[:elite_count]
        
        # Generate offspring
        offspring = []
        while len(offspring) < len(population) - elite_count:
            # Tournament selection
            parent1 = self._tournament_selection(population, tournament_size=3)
            parent2 = self._tournament_selection(population, tournament_size=3)
            
            # Crossover
            if np.random.random() < ga_config.crossover_rate:
                child1, child2 = parent1.crossover(parent2, "single_point")
            else:
                child1, child2 = parent1.copy(), parent2.copy()
            
            # Mutation
            if np.random.random() < ga_config.mutation_rate:
                child1 = child1.mutate(ga_config.mutation_rate)
            if np.random.random() < ga_config.mutation_rate:
                child2 = child2.mutate(ga_config.mutation_rate)
            
            # Calculate fitness
            child1.calculate_fitness(audio_data)
            child2.calculate_fitness(audio_data)
            
            offspring.extend([child1, child2])
        
        # Combine elites and offspring
        new_population = elites + offspring[:len(population) - elite_count]
        
        return new_population
    
    def _tournament_selection(self, population: List, tournament_size: int = 3) -> AudioChromosome:
        """Select a parent using tournament selection."""
        tournament = np.random.choice(population, size=tournament_size, replace=False)
        return max(tournament, key=lambda x: x.fitness)
    
    async def _save_generation(self, job_id: str, generation: int, population: List,
                              audio_data: np.ndarray, header_data: np.ndarray,
                              processor: AudioProcessor, results_dir: Path):
        """Save the best individual from a generation."""
        
        best_individual = max(population, key=lambda x: x.fitness)
        
        filename = f"generation_{generation:04d}_fitness_{best_individual.fitness:.2f}.wav"
        file_path = results_dir / filename
        
        processor.save_wav_file(best_individual.dna, header_data, file_path)
    
    async def _save_final_results(self, job_id: str, population: List, 
                                 audio_data: np.ndarray, header_data: np.ndarray,
                                 processor: AudioProcessor, results_dir: Path, 
                                 final_generation: int):
        """Save final evolution results."""
        
        # Save best individual
        best_individual = max(population, key=lambda x: x.fitness)
        best_filename = f"best_result_fitness_{best_individual.fitness:.2f}.wav"
        processor.save_wav_file(best_individual.dna, header_data, results_dir / best_filename)
        
        # Save statistics
        fitnesses = [chromo.fitness for chromo in population]
        stats = {
            "job_id": job_id,
            "final_generation": final_generation,
            "best_fitness": max(fitnesses),
            "avg_fitness": sum(fitnesses) / len(fitnesses),
            "population_size": len(population),
            "fitness_distribution": {
                "min": min(fitnesses),
                "max": max(fitnesses),
                "median": float(np.median(fitnesses)),
                "std": float(np.std(fitnesses))
            }
        }
        
        with open(results_dir / "evolution_stats.json", 'w') as f:
            json.dump(stats, f, indent=2)
    
    async def _update_status(self, job_id: str, status: str, websocket_manager: Any):
        """Update job status and broadcast."""
        if job_id in self.active_jobs:
            self.active_jobs[job_id]["status"] = status
            await self._broadcast_update(job_id, websocket_manager)
    
    async def _broadcast_update(self, job_id: str, websocket_manager: Any):
        """Broadcast job update to connected WebSocket clients."""
        if job_id in self.active_jobs:
            update_data = self.active_jobs[job_id].copy()
        elif job_id in self.job_history:
            update_data = self.job_history[job_id].copy()
        else:
            return
        
        # Convert datetime objects to strings
        if "start_time" in update_data:
            update_data["start_time"] = update_data["start_time"].isoformat()
        if "end_time" in update_data:
            update_data["end_time"] = update_data["end_time"].isoformat()
        
        # Remove file objects that can't be serialized
        update_data.pop("params", None)
        
        await websocket_manager.broadcast_to_job(job_id, update_data)
    
    async def get_job_status(self, job_id: str) -> Optional[Dict]:
        """Get the current status of a job."""
        if job_id in self.active_jobs:
            status = self.active_jobs[job_id].copy()
        elif job_id in self.job_history:
            status = self.job_history[job_id].copy()
        else:
            return None
        
        # Convert datetime objects
        if "start_time" in status:
            status["start_time"] = status["start_time"].isoformat()
        if "end_time" in status:
            status["end_time"] = status["end_time"].isoformat()
        
        status.pop("params", None)
        return status
    
    async def get_job_results(self, job_id: str) -> Optional[Dict]:
        """Get the results of a completed job."""
        if job_id not in self.job_history:
            return None
        
        job_data = self.job_history[job_id]
        if job_data["status"] != "completed":
            return None
        
        # List result files
        results_dir = self.results_dir / job_id
        if not results_dir.exists():
            return None
        
        files = []
        for file_path in results_dir.iterdir():
            if file_path.is_file():
                files.append({
                    "filename": file_path.name,
                    "size": file_path.stat().st_size,
                    "download_url": f"/api/v1/download/{job_id}/{file_path.name}"
                })
        
        return {
            "job_id": job_id,
            "status": job_data["status"],
            "files": files,
            "final_fitness": job_data.get("final_best_fitness", 0),
            "generations": job_data.get("final_generation", 0)
        }
    
    async def list_jobs(self, limit: int = 50, offset: int = 0) -> List[Dict]:
        """List all jobs (active and completed)."""
        all_jobs = []
        
        # Add active jobs
        for job_id, job_data in self.active_jobs.items():
            job_summary = {
                "job_id": job_id,
                "status": job_data["status"],
                "progress": job_data.get("progress", 0),
                "start_time": job_data["start_time"].isoformat(),
                "best_fitness": job_data.get("best_fitness", 0)
            }
            all_jobs.append(job_summary)
        
        # Add completed jobs
        for job_id, job_data in self.job_history.items():
            job_summary = {
                "job_id": job_id,
                "status": job_data["status"],
                "progress": 100 if job_data["status"] == "completed" else 0,
                "start_time": job_data["start_time"].isoformat(),
                "best_fitness": job_data.get("final_best_fitness", job_data.get("best_fitness", 0))
            }
            if "end_time" in job_data:
                job_summary["end_time"] = job_data["end_time"].isoformat()
            all_jobs.append(job_summary)
        
        # Sort by start time (newest first)
        all_jobs.sort(key=lambda x: x["start_time"], reverse=True)
        
        return all_jobs[offset:offset + limit]
    
    async def pause_job(self, job_id: str) -> bool:
        """Pause a running job."""
        if job_id in self.active_jobs:
            self.active_jobs[job_id]["paused"] = True
            return True
        return False
    
    async def resume_job(self, job_id: str) -> bool:
        """Resume a paused job."""
        if job_id in self.active_jobs:
            self.active_jobs[job_id]["paused"] = False
            return True
        return False
    
    async def stop_job(self, job_id: str) -> bool:
        """Stop a running job."""
        if job_id in self.active_jobs:
            self.active_jobs[job_id]["stopped"] = True
            return True
        return False
    
    async def delete_job(self, job_id: str) -> bool:
        """Delete a job and its results."""
        # Remove from active jobs
        if job_id in self.active_jobs:
            self.active_jobs[job_id]["stopped"] = True
            del self.active_jobs[job_id]
        
        # Remove from history
        if job_id in self.job_history:
            del self.job_history[job_id]
        
        # Delete result files
        results_dir = self.results_dir / job_id
        if results_dir.exists():
            import shutil
            shutil.rmtree(results_dir)
        
        return True
    
    async def cleanup(self):
        """Clean up service resources."""
        # Stop all active jobs
        for job_id in list(self.active_jobs.keys()):
            await self.stop_job(job_id)