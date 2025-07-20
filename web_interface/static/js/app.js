/**
 * Genetic Algorithm Music Evolution - Frontend JavaScript
 * 
 * Handles user interface interactions, WebSocket communication,
 * file uploads, and real-time evolution monitoring.
 */

class EvolutionApp {
    constructor() {
        this.websocket = null;
        this.currentJobId = null;
        this.fitnessChart = null;
        this.selectedFile = null;
        this.presets = {};
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupDragAndDrop();
        this.setupParameterSliders();
        this.loadPresets();
        this.loadRecentJobs();
        this.initializeChart();
    }
    
    setupEventListeners() {
        // Form submission
        document.getElementById('evolutionForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.startEvolution();
        });
        
        // File input change
        document.getElementById('audioFile').addEventListener('change', (e) => {
            this.handleFileSelect(e.target.files[0]);
        });
        
        // Preset selection
        document.getElementById('presetSelect').addEventListener('change', (e) => {
            this.applyPreset(e.target.value);
        });
        
        // Job controls
        document.getElementById('pauseBtn').addEventListener('click', () => {
            this.controlJob('pause');
        });
        
        document.getElementById('stopBtn').addEventListener('click', () => {
            this.controlJob('stop');
        });
        
        // Upload zone click
        document.getElementById('uploadZone').addEventListener('click', () => {
            document.getElementById('audioFile').click();
        });
    }
    
    setupDragAndDrop() {
        const uploadZone = document.getElementById('uploadZone');
        
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadZone.addEventListener(eventName, this.preventDefaults, false);
        });
        
        ['dragenter', 'dragover'].forEach(eventName => {
            uploadZone.addEventListener(eventName, () => {
                uploadZone.classList.add('dragover');
            }, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            uploadZone.addEventListener(eventName, () => {
                uploadZone.classList.remove('dragover');
            }, false);
        });
        
        uploadZone.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileSelect(files[0]);
            }
        }, false);
    }
    
    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    setupParameterSliders() {
        const sliders = [
            { id: 'populationSize', display: 'populationValue' },
            { id: 'maxGenerations', display: 'generationsValue' },
            { id: 'mutationRate', display: 'mutationValue', formatter: (v) => `${(v * 100).toFixed(1)}%` },
            { id: 'fitnessThreshold', display: 'fitnessValue', formatter: (v) => `${v}%` }
        ];
        
        sliders.forEach(slider => {
            const element = document.getElementById(slider.id);
            const display = document.getElementById(slider.display);
            
            element.addEventListener('input', () => {
                const value = parseFloat(element.value);
                const displayValue = slider.formatter ? slider.formatter(value) : value;
                display.textContent = displayValue;
            });
        });
    }
    
    async loadPresets() {
        try {
            const response = await fetch('/api/v1/presets');
            this.presets = await response.json();
        } catch (error) {
            console.error('Failed to load presets:', error);
        }
    }
    
    applyPreset(presetName) {
        if (presetName === 'custom' || !this.presets[presetName]) {
            return;
        }
        
        const preset = this.presets[presetName];
        
        // Update form values
        document.getElementById('populationSize').value = preset.population_size;
        document.getElementById('maxGenerations').value = preset.max_generations;
        document.getElementById('mutationRate').value = preset.mutation_rate;
        document.getElementById('fitnessThreshold').value = preset.fitness_threshold;
        
        // Update displays
        document.getElementById('populationValue').textContent = preset.population_size;
        document.getElementById('generationsValue').textContent = preset.max_generations;
        document.getElementById('mutationValue').textContent = `${(preset.mutation_rate * 100).toFixed(1)}%`;
        document.getElementById('fitnessValue').textContent = `${preset.fitness_threshold}%`;
        
        // Show advanced params if not custom
        if (presetName !== 'custom') {
            const advancedParams = document.getElementById('advancedParams');
            if (!advancedParams.classList.contains('show')) {
                const collapse = new bootstrap.Collapse(advancedParams);
                collapse.show();
            }
        }
    }
    
    handleFileSelect(file) {
        if (!file) return;
        
        // Validate file type
        const allowedTypes = ['audio/wav', 'audio/mpeg', 'audio/flac', 'audio/ogg'];
        const allowedExtensions = ['.wav', '.mp3', '.flac', '.ogg'];
        
        const isValidType = allowedTypes.includes(file.type) || 
                           allowedExtensions.some(ext => file.name.toLowerCase().endsWith(ext));
        
        if (!isValidType) {
            this.showAlert('Please select a valid audio file (WAV, MP3, FLAC, or OGG)', 'danger');
            return;
        }
        
        this.selectedFile = file;
        
        // Update UI
        document.getElementById('fileName').textContent = `${file.name} (${this.formatFileSize(file.size)})`;
        document.getElementById('fileInfo').style.display = 'block';
        document.getElementById('uploadZone').style.display = 'none';
        
        // Enable start button
        document.getElementById('startBtn').disabled = false;
    }
    
    clearFile() {
        this.selectedFile = null;
        document.getElementById('fileInfo').style.display = 'none';
        document.getElementById('uploadZone').style.display = 'block';
        document.getElementById('startBtn').disabled = true;
        document.getElementById('audioFile').value = '';
    }
    
    async startEvolution() {
        if (!this.selectedFile) {
            this.showAlert('Please select an audio file first', 'warning');
            return;
        }
        
        const formData = new FormData();
        formData.append('audio_file', this.selectedFile);
        formData.append('population_size', document.getElementById('populationSize').value);
        formData.append('mutation_rate', document.getElementById('mutationRate').value);
        formData.append('max_generations', document.getElementById('maxGenerations').value);
        formData.append('fitness_threshold', document.getElementById('fitnessThreshold').value);
        formData.append('crossover_rate', '0.8');
        formData.append('elite_size', '0.1');
        formData.append('fitness_function', 'byte_similarity');
        formData.append('save_generations', '10,25,50,75,90,95');
        
        try {
            // Disable form
            this.setFormEnabled(false);
            
            const response = await fetch('/api/v1/evolve', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            this.currentJobId = result.job_id;
            
            // Switch to active status view
            this.showEvolutionStatus();
            
            // Connect WebSocket
            this.connectWebSocket(result.job_id);
            
            this.showAlert(`Evolution started! Job ID: ${result.job_id}`, 'success');
            
        } catch (error) {
            console.error('Evolution start error:', error);
            this.showAlert(`Failed to start evolution: ${error.message}`, 'danger');
            this.setFormEnabled(true);
        }
    }
    
    connectWebSocket(jobId) {
        if (this.websocket) {
            this.websocket.close();
        }
        
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/evolution/${jobId}`;
        
        this.websocket = new WebSocket(wsUrl);
        
        this.websocket.onopen = () => {
            console.log('WebSocket connected');
        };
        
        this.websocket.onmessage = (event) => {
            const message = JSON.parse(event.data);
            this.handleWebSocketMessage(message);
        };
        
        this.websocket.onclose = () => {
            console.log('WebSocket disconnected');
            setTimeout(() => {
                if (this.currentJobId) {
                    this.connectWebSocket(this.currentJobId);
                }
            }, 5000); // Reconnect after 5 seconds
        };
        
        this.websocket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }
    
    handleWebSocketMessage(message) {
        if (message.type === 'evolution_update') {
            this.updateEvolutionStatus(message.data);
        }
    }
    
    updateEvolutionStatus(data) {
        // Update progress bar
        const progress = Math.round(data.progress || 0);
        document.getElementById('progressBar').style.width = `${progress}%`;
        document.getElementById('progressPercent').textContent = `${progress}%`;
        
        // Update statistics
        document.getElementById('currentGeneration').textContent = data.generation || 0;
        document.getElementById('bestFitness').textContent = `${(data.best_fitness || 0).toFixed(1)}%`;
        
        // Update status message
        const statusText = this.getStatusText(data.status);
        document.getElementById('statusText').textContent = statusText;
        
        // Update chart
        if (data.generation && data.best_fitness) {
            this.updateChart(data.generation, data.best_fitness, data.avg_fitness);
        }
        
        // Handle completion
        if (data.status === 'completed') {
            this.handleEvolutionComplete(data);
        } else if (data.status === 'error') {
            this.handleEvolutionError(data);
        }
    }
    
    getStatusText(status) {
        const statusMessages = {
            'initializing': 'Initializing evolution...',
            'loading_audio': 'Loading audio file...',
            'creating_population': 'Creating initial population...',
            'evolving': 'Evolution in progress...',
            'completed': 'Evolution completed successfully!',
            'error': 'Evolution encountered an error',
            'paused': 'Evolution paused',
            'stopped': 'Evolution stopped',
            'fitness_threshold_reached': 'Fitness threshold reached!',
            'converged': 'Population has converged'
        };
        
        return statusMessages[status] || 'Unknown status';
    }
    
    async handleEvolutionComplete(data) {
        this.showAlert('Evolution completed successfully!', 'success');
        
        // Load results
        try {
            const response = await fetch(`/api/v1/results/${this.currentJobId}`);
            const results = await response.json();
            
            this.showResults(results);
        } catch (error) {
            console.error('Failed to load results:', error);
        }
        
        this.resetForm();
    }
    
    handleEvolutionError(data) {
        this.showAlert(`Evolution failed: ${data.error || 'Unknown error'}`, 'danger');
        this.resetForm();
    }
    
    showResults(results) {
        const modal = new bootstrap.Modal(document.getElementById('resultsModal'));
        const content = document.getElementById('resultsContent');
        
        let html = `
            <div class="mb-3">
                <h6>Evolution Statistics</h6>
                <div class="row">
                    <div class="col-md-6">
                        <strong>Final Fitness:</strong> ${results.final_fitness.toFixed(2)}%
                    </div>
                    <div class="col-md-6">
                        <strong>Generations:</strong> ${results.generations}
                    </div>
                </div>
            </div>
            
            <h6>Download Results</h6>
        `;
        
        results.files.forEach(file => {
            html += `
                <div class="file-download">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <strong>${file.filename}</strong><br>
                            <small class="text-muted">${this.formatFileSize(file.size)}</small>
                        </div>
                        <div>
                            <a href="${file.download_url}" class="btn btn-success btn-sm" download>
                                <i class="bi bi-download"></i> Download
                            </a>
                            <button class="btn btn-info btn-sm ms-2" onclick="app.playAudio('${file.download_url}')">
                                <i class="bi bi-play"></i> Play
                            </button>
                        </div>
                    </div>
                </div>
            `;
        });
        
        content.innerHTML = html;
        modal.show();
    }
    
    async playAudio(url) {
        // Create temporary audio element
        const audio = new Audio(url);
        audio.controls = true;
        audio.autoplay = true;
        
        // Add to a temporary container
        const container = document.createElement('div');
        container.className = 'audio-player mt-2';
        container.appendChild(audio);
        
        // Add to modal content
        document.getElementById('resultsContent').appendChild(container);
        
        // Remove after playing
        audio.addEventListener('ended', () => {
            container.remove();
        });
    }
    
    controlJob(action) {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(action);
        }
    }
    
    showEvolutionStatus() {
        document.getElementById('statusIdle').style.display = 'none';
        document.getElementById('statusActive').style.display = 'block';
        document.getElementById('visualizationSection').style.display = 'block';
    }
    
    resetForm() {
        // Re-enable form
        this.setFormEnabled(true);
        
        // Reset UI
        document.getElementById('statusIdle').style.display = 'block';
        document.getElementById('statusActive').style.display = 'none';
        
        // Clear job ID
        this.currentJobId = null;
        
        // Close WebSocket
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }
        
        // Refresh jobs list
        this.loadRecentJobs();
    }
    
    setFormEnabled(enabled) {
        const elements = [
            'audioFile', 'presetSelect', 'populationSize', 
            'maxGenerations', 'mutationRate', 'fitnessThreshold', 'startBtn'
        ];
        
        elements.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.disabled = !enabled;
            }
        });
    }
    
    initializeChart() {
        const ctx = document.getElementById('fitnessChart').getContext('2d');
        
        this.fitnessChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Best Fitness',
                    data: [],
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    tension: 0.4,
                    pointRadius: 3,
                    pointHoverRadius: 6
                }, {
                    label: 'Average Fitness',
                    data: [],
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    tension: 0.4,
                    pointRadius: 2,
                    pointHoverRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    legend: {
                        labels: {
                            color: '#fff'
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Generation',
                            color: '#fff'
                        },
                        ticks: {
                            color: '#ccc'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Fitness (%)',
                            color: '#fff'
                        },
                        ticks: {
                            color: '#ccc'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        min: 0,
                        max: 100
                    }
                }
            }
        });
    }
    
    updateChart(generation, bestFitness, avgFitness) {
        this.fitnessChart.data.labels.push(generation);
        this.fitnessChart.data.datasets[0].data.push(bestFitness);
        this.fitnessChart.data.datasets[1].data.push(avgFitness || 0);
        
        // Keep only last 50 points for performance
        if (this.fitnessChart.data.labels.length > 50) {
            this.fitnessChart.data.labels.shift();
            this.fitnessChart.data.datasets[0].data.shift();
            this.fitnessChart.data.datasets[1].data.shift();
        }
        
        this.fitnessChart.update('none'); // No animation for real-time updates
    }
    
    async loadRecentJobs() {
        try {
            const response = await fetch('/api/v1/jobs?limit=10');
            const data = await response.json();
            
            this.displayJobsList(data.jobs);
        } catch (error) {
            console.error('Failed to load jobs:', error);
            document.getElementById('jobsList').innerHTML = `
                <div class="text-center text-muted">
                    <i class="bi bi-exclamation-triangle"></i>
                    Failed to load jobs
                </div>
            `;
        }
    }
    
    displayJobsList(jobs) {
        const container = document.getElementById('jobsList');
        
        if (!jobs || jobs.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted py-3">
                    <i class="bi bi-inbox"></i>
                    No evolution jobs yet
                </div>
            `;
            return;
        }
        
        let html = '';
        jobs.forEach(job => {
            const statusClass = job.status.replace('_', '-');
            const timeAgo = this.timeAgo(new Date(job.start_time));
            
            html += `
                <div class="job-item fade-in">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <div class="d-flex align-items-center mb-2">
                                <span class="job-status ${statusClass}">${job.status}</span>
                                <small class="text-muted ms-2">${timeAgo}</small>
                            </div>
                            <div class="small text-muted">
                                Job ID: ${job.job_id}<br>
                                Best Fitness: ${job.best_fitness.toFixed(1)}%
                            </div>
                        </div>
                        <div>
                            ${job.status === 'completed' ? 
                                `<button class="btn btn-success btn-sm" onclick="app.loadJobResults('${job.job_id}')">
                                    <i class="bi bi-download"></i> Results
                                </button>` : 
                                `<div class="progress" style="width: 100px; height: 6px;">
                                    <div class="progress-bar" style="width: ${job.progress}%"></div>
                                </div>`
                            }
                        </div>
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = html;
    }
    
    async loadJobResults(jobId) {
        try {
            const response = await fetch(`/api/v1/results/${jobId}`);
            const results = await response.json();
            
            this.showResults(results);
        } catch (error) {
            console.error('Failed to load job results:', error);
            this.showAlert('Failed to load job results', 'danger');
        }
    }
    
    showAlert(message, type = 'info') {
        // Create alert element
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alert.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alert);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }
    
    formatFileSize(bytes) {
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        if (bytes === 0) return '0 Bytes';
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return `${Math.round(bytes / Math.pow(1024, i) * 100) / 100} ${sizes[i]}`;
    }
    
    timeAgo(date) {
        const now = new Date();
        const diff = now - date;
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);
        
        if (days > 0) return `${days} day${days > 1 ? 's' : ''} ago`;
        if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
        if (minutes > 0) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
        return 'Just now';
    }
}

// Global functions
function refreshJobs() {
    app.loadRecentJobs();
}

function clearFile() {
    app.clearFile();
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new EvolutionApp();
});

// Global error handler
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
});

// Handle WebSocket connection issues
window.addEventListener('online', () => {
    if (window.app && window.app.currentJobId && !window.app.websocket) {
        window.app.connectWebSocket(window.app.currentJobId);
    }
});

window.addEventListener('offline', () => {
    window.app?.showAlert('Connection lost. Reconnecting when back online...', 'warning');
});