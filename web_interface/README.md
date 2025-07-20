# 🎵 Genetic Algorithm Music Evolution - Web Interface

A modern, real-time web interface for evolving audio files using genetic algorithms. Built with FastAPI, WebSockets, and Bootstrap for a beautiful, responsive user experience.

## 🌟 Features

### 🚀 **Modern Web Interface**
- **Drag & Drop** file upload with visual feedback
- **Real-time progress** monitoring via WebSockets
- **Interactive parameter** controls with sliders
- **Beautiful dark theme** with gradient UI elements
- **Responsive design** that works on all devices

### 🧬 **Genetic Algorithm Features**
- **Multiple fitness functions**: Byte similarity, spectral, perceptual
- **Configurable parameters**: Population size, mutation rate, generations
- **Evolution presets**: Fast, Balanced, Thorough, Experimental
- **Real-time visualization** of fitness progression
- **Background processing** with job management

### 📊 **Real-time Monitoring**
- **Live fitness charts** showing evolution progress
- **WebSocket updates** for instant feedback
- **Job controls**: Pause, resume, stop evolution
- **Progress tracking** with estimated completion times
- **Error handling** with detailed messages

### 💾 **Results Management**
- **Automatic result saving** at specified generations
- **Download interface** for evolved audio files
- **In-browser audio playback** for quick preview
- **Job history** with status tracking
- **File management** with organized storage

## 🏗️ Architecture

```
web_interface/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── services/              # Backend services
│   ├── evolution_service.py    # Genetic algorithm processing
│   └── websocket_manager.py   # Real-time communication
├── models/                # Data models
│   └── evolution_models.py    # Pydantic models
├── templates/             # HTML templates
│   └── index.html            # Main web interface
├── static/                # Static assets
│   ├── css/
│   │   └── style.css         # Custom styling
│   └── js/
│       └── app.js            # Frontend JavaScript
├── uploads/               # Uploaded audio files
└── results/               # Evolution results
```

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- The main genetic algorithm package (from `../src/`)

### 1. Install Dependencies
```bash
cd web_interface
pip install -r requirements.txt
```

### 2. Set Up the Main Package
Ensure the genetic algorithm package is available:
```bash
# From the project root
cd src
pip install -e .
```

### 3. Run the Application
```bash
cd web_interface
python main.py
```

The web interface will be available at: **http://localhost:8000**

## 🚀 Usage

### 1. **Upload Audio File**
- Drag and drop an audio file onto the upload zone
- Or click to browse and select a file
- Supported formats: WAV, MP3, FLAC, OGG (WAV recommended)

### 2. **Configure Evolution**
- Choose a preset or use custom parameters
- Adjust population size, mutation rate, generations
- Set fitness threshold for early termination

### 3. **Start Evolution**
- Click "Start Evolution" to begin
- Watch real-time progress updates
- Monitor fitness charts and statistics

### 4. **Control Evolution**
- Pause/resume jobs as needed
- Stop evolution early if desired
- Multiple jobs can run simultaneously

### 5. **Download Results**
- Access results when evolution completes
- Download evolved audio files
- Play files directly in the browser

## 🎛️ Configuration Options

### **Evolution Presets**
- **🚀 Fast**: 100 population, 50 generations (testing)
- **⚖️ Balanced**: 200 population, 100 generations (recommended)
- **🎯 Thorough**: 500 population, 300 generations (high quality)
- **🔬 Experimental**: 1000 population, 1000 generations (maximum)

### **Advanced Parameters**
- **Population Size**: 50-1000 individuals
- **Mutation Rate**: 0.1%-10% mutation probability
- **Max Generations**: 10-500 evolution cycles
- **Fitness Threshold**: 80%-99% target fitness
- **Crossover Rate**: 10%-100% breeding probability
- **Elite Size**: 0%-50% top performers preserved

### **Fitness Functions**
- **Byte Similarity**: Direct byte-level comparison
- **Spectral**: Frequency domain analysis
- **Perceptual**: Human hearing-based evaluation

## 🔧 API Endpoints

### **Evolution Management**
- `POST /api/v1/evolve` - Start evolution job
- `GET /api/v1/status/{job_id}` - Get job status
- `GET /api/v1/results/{job_id}` - Get job results
- `DELETE /api/v1/jobs/{job_id}` - Delete job

### **Job Management**
- `GET /api/v1/jobs` - List all jobs
- `GET /api/v1/presets` - Get parameter presets
- `GET /api/v1/health` - System health check

### **File Operations**
- `GET /api/v1/download/{job_id}/{filename}` - Download result file

### **WebSocket**
- `WS /ws/evolution/{job_id}` - Real-time job updates

## 📡 WebSocket Messages

### **Client → Server**
```json
"pause"   // Pause evolution
"resume"  // Resume evolution  
"stop"    // Stop evolution
```

### **Server → Client**
```json
{
  "type": "evolution_update",
  "job_id": "uuid",
  "data": {
    "status": "evolving",
    "progress": 45.2,
    "generation": 45,
    "best_fitness": 87.3,
    "avg_fitness": 82.1,
    "population_size": 200
  }
}
```

## 🎨 User Interface

### **Main Interface**
- **Upload Section**: Drag & drop file upload with validation
- **Parameters**: Preset selection and advanced controls
- **Status Panel**: Real-time progress and job controls
- **Visualization**: Live fitness charts and statistics

### **Results Modal**
- **Statistics**: Final fitness and generation counts
- **File Downloads**: List of generated audio files
- **Audio Player**: In-browser playback capability

### **Job History**
- **Recent Jobs**: List of past evolution sessions
- **Status Indicators**: Visual job status badges
- **Quick Actions**: Download results, view details

## 🔐 Security Considerations

### **File Upload Security**
- File type validation (audio formats only)
- File size limits (configurable)
- Secure file storage with UUID naming
- Automatic cleanup of old files

### **API Security**
- Input validation with Pydantic models
- Error handling with sanitized messages
- CORS configuration for development
- Rate limiting (recommended for production)

## 🚀 Production Deployment

### **Environment Setup**
```bash
# Set production environment
export ENVIRONMENT=production

# Configure file storage
export UPLOAD_DIR=/var/uploads
export RESULTS_DIR=/var/results

# Set security headers
export CORS_ORIGINS=["https://yourdomain.com"]
```

### **Using Docker**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **Reverse Proxy (nginx)**
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## 🧪 Development

### **Running in Development**
```bash
# Install development dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Access API documentation
open http://localhost:8000/api/docs
```

### **Testing**
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/
```

## 🔍 Monitoring

### **Health Check**
```bash
curl http://localhost:8000/api/v1/health
```

### **Job Status**
```bash
curl http://localhost:8000/api/v1/jobs
```

### **WebSocket Test**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/evolution/job-id');
ws.onmessage = (event) => console.log(JSON.parse(event.data));
```

## 🎵 Example Usage

1. **Upload a WAV file** containing a short musical phrase
2. **Select "Balanced" preset** for good quality results
3. **Start evolution** and watch the fitness improve
4. **Monitor progress** via real-time charts
5. **Download results** when evolution completes
6. **Compare original vs evolved** audio files

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and test thoroughly
4. Submit a pull request with detailed description

## 📜 License

This project is part of the Genetic Algorithm Music Evolution suite.

## 🆘 Troubleshooting

### **Common Issues**

**File Upload Fails**
- Check file format (WAV, MP3, FLAC, OGG)
- Verify file size limits
- Ensure proper MIME type

**WebSocket Connection Issues**
- Check firewall settings
- Verify proxy configuration
- Test with different browsers

**Evolution Doesn't Start**
- Check Python path and dependencies
- Verify genetic algorithm package installation
- Review server logs for errors

**Slow Performance**
- Reduce population size
- Lower max generations
- Use faster fitness function

### **Getting Help**
- Check the console logs (F12 in browser)
- Review FastAPI logs in terminal
- Test API endpoints directly
- Verify file permissions for uploads/results

---

## 🎉 **Ready to Evolve Your Music!**

The web interface provides a powerful, user-friendly way to experiment with genetic algorithm music evolution. Upload your audio files and discover what artificial evolution can create! 🧬🎵