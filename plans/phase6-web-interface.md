# Phase 6: Interactive Web Interface

## Overview

Implement comprehensive web interface using FastAPI and modern frontend technologies. Provide drag-and-drop file uploads, real-time analysis, visual dashboards, and mobile-responsive design for enhanced user experience.

## Prerequisites

- Phase 1 (Encryption) completed
- Phase 2 (Graph Database) completed
- Phase 3 (Resume Optimization) completed
- Phase 4 (Industry Analysis) completed
- Phase 5 (Interview Preparation) completed
- All backend functionality working

## Implementation Steps

### 1. Create FastAPI Web Application (`src/web_interface.py`)

**New file**: `src/web_interface.py`

Implement main web application:

**Core functionality**:
- FastAPI application setup
- API endpoints for all features
- WebSocket support for real-time updates
- File upload handling
- Authentication and session management

**Key components**:
```python
from fastapi import FastAPI, UploadFile, File, WebSocket, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
import asyncio
import json

app = FastAPI(title="Job Application Agent", version="1.0.0")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="web/static"), name="static")
templates = Jinja2Templates(directory="web/templates")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    # Main dashboard page
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.post("/api/analyze")
async def analyze_job_application(
    job_file: UploadFile = File(...),
    resume_file: UploadFile = File(...),
    options: dict = None
):
    # API endpoint for job application analysis
    # Returns: analysis results as JSON

@app.post("/api/upload")
async def upload_files(
    job_file: UploadFile = File(...),
    resume_file: UploadFile = File(...)
):
    # Handle file uploads
    # Returns: file IDs and processing status

@app.websocket("/ws/analysis/{session_id}")
async def websocket_analysis(websocket: WebSocket, session_id: str):
    # WebSocket for real-time analysis updates
    # Provides live progress updates during analysis

@app.get("/api/analytics")
async def get_analytics(user_id: str = None):
    # Get user analytics and insights
    # Returns: comprehensive analytics data

@app.get("/api/applications")
async def get_applications(user_id: str = None):
    # Get tracked applications
    # Returns: list of applications with status

@app.post("/api/applications/{app_id}/status")
async def update_application_status(app_id: str, status: str):
    # Update application status
    # Returns: success confirmation
```

### 2. Create Frontend Components (`web/static/js/`)

**New directory**: `web/static/js/`

Implement modern JavaScript frontend:

**Main application** (`web/static/js/app.js`):
```javascript
class JobApplicationAgent {
    constructor() {
        this.socket = null;
        this.currentSession = null;
        this.initializeEventListeners();
    }
    
    initializeEventListeners() {
        // File upload handlers
        this.setupFileUpload();
        // Analysis form handlers
        this.setupAnalysisForm();
        // Dashboard interactions
        this.setupDashboard();
        // Real-time updates
        this.setupWebSocket();
    }
    
    setupFileUpload() {
        const dropZone = document.getElementById('drop-zone');
        dropZone.addEventListener('dragover', this.handleDragOver.bind(this));
        dropZone.addEventListener('drop', this.handleDrop.bind(this));
        dropZone.addEventListener('dragleave', this.handleDragLeave.bind(this));
    }
    
    async startAnalysis(jobFile, resumeFile, options = {}) {
        // Start analysis with real-time updates
        const formData = new FormData();
        formData.append('job_file', jobFile);
        formData.append('resume_file', resumeFile);
        formData.append('options', JSON.stringify(options));
        
        const response = await fetch('/api/analyze', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        this.currentSession = result.session_id;
        this.connectWebSocket(result.session_id);
        
        return result;
    }
    
    connectWebSocket(sessionId) {
        this.socket = new WebSocket(`ws://localhost:8000/ws/analysis/${sessionId}`);
        
        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.updateProgress(data);
        };
        
        this.socket.onclose = () => {
            console.log('WebSocket connection closed');
        };
    }
    
    updateProgress(data) {
        // Update progress bar and status
        const progressBar = document.getElementById('progress-bar');
        const statusText = document.getElementById('status-text');
        
        progressBar.style.width = `${data.progress}%`;
        statusText.textContent = data.status;
        
        if (data.complete) {
            this.displayResults(data.results);
        }
    }
    
    displayResults(results) {
        // Display analysis results with visualizations
        this.renderScoreChart(results.overall_score);
        this.renderKeywordAnalysis(results.keyword_analysis);
        this.renderRecommendations(results.recommendations);
        this.renderIndustryInsights(results.industry_analysis);
    }
}
```

**Dashboard components** (`web/static/js/dashboard.js`):
```javascript
class Dashboard {
    constructor() {
        this.charts = {};
        this.initializeCharts();
        this.loadAnalytics();
    }
    
    initializeCharts() {
        // Initialize Chart.js charts
        this.charts.scoreChart = new Chart(document.getElementById('score-chart'), {
            type: 'doughnut',
            data: {
                labels: ['Keyword Match', 'ATS Score', 'Industry Fit'],
                datasets: [{
                    data: [0, 0, 0],
                    backgroundColor: ['#4CAF50', '#2196F3', '#FF9800']
                }]
            }
        });
        
        this.charts.timelineChart = new Chart(document.getElementById('timeline-chart'), {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Application Success Rate',
                    data: [],
                    borderColor: '#4CAF50',
                    tension: 0.1
                }]
            }
        });
    }
    
    async loadAnalytics() {
        const response = await fetch('/api/analytics');
        const data = await response.json();
        
        this.updateScoreChart(data.overall_scores);
        this.updateTimelineChart(data.timeline_data);
        this.updateApplicationStats(data.application_stats);
    }
    
    updateScoreChart(scores) {
        this.charts.scoreChart.data.datasets[0].data = [
            scores.keyword_match,
            scores.ats_score,
            scores.industry_fit
        ];
        this.charts.scoreChart.update();
    }
}
```

### 3. Create HTML Templates (`web/templates/`)

**New directory**: `web/templates/`

Implement responsive HTML templates:

**Main dashboard** (`web/templates/dashboard.html`):
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Job Application Agent</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="/static/css/style.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">Job Application Agent</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="#analytics">Analytics</a>
                <a class="nav-link" href="#applications">Applications</a>
                <a class="nav-link" href="#settings">Settings</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <!-- File Upload Section -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h4>Upload Files for Analysis</h4>
                    </div>
                    <div class="card-body">
                        <div id="drop-zone" class="drop-zone">
                            <div class="drop-zone-content">
                                <i class="fas fa-cloud-upload-alt fa-3x mb-3"></i>
                                <p>Drag and drop your job description and resume here</p>
                                <p class="text-muted">or click to browse files</p>
                            </div>
                        </div>
                        <div class="mt-3">
                            <input type="file" id="job-file" accept=".pdf,.docx,.txt" class="form-control mb-2">
                            <input type="file" id="resume-file" accept=".pdf,.docx,.txt" class="form-control">
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Analysis Options -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h4>Analysis Options</h4>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-4">
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="optimize-resume" checked>
                                    <label class="form-check-label" for="optimize-resume">
                                        Resume Optimization
                                    </label>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="industry-analysis" checked>
                                    <label class="form-check-label" for="industry-analysis">
                                        Industry Analysis
                                    </label>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="interview-prep" checked>
                                    <label class="form-check-label" for="interview-prep">
                                        Interview Preparation
                                    </label>
                                </div>
                            </div>
                        </div>
                        <div class="mt-3">
                            <button id="start-analysis" class="btn btn-primary btn-lg">
                                <i class="fas fa-play me-2"></i>Start Analysis
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Progress Section -->
        <div id="progress-section" class="row mb-4" style="display: none;">
            <div class="col-12">
                <div class="card">
                    <div class="card-body">
                        <h5 id="status-text">Initializing analysis...</h5>
                        <div class="progress mb-3">
                            <div id="progress-bar" class="progress-bar" role="progressbar" style="width: 0%"></div>
                        </div>
                        <div id="progress-details" class="text-muted"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Results Section -->
        <div id="results-section" class="row" style="display: none;">
            <!-- Score Overview -->
            <div class="col-md-4 mb-4">
                <div class="card">
                    <div class="card-header">
                        <h5>Overall Score</h5>
                    </div>
                    <div class="card-body text-center">
                        <canvas id="score-chart" width="200" height="200"></canvas>
                        <h3 id="overall-score" class="mt-3">0%</h3>
                    </div>
                </div>
            </div>

            <!-- Keyword Analysis -->
            <div class="col-md-8 mb-4">
                <div class="card">
                    <div class="card-header">
                        <h5>Keyword Analysis</h5>
                    </div>
                    <div class="card-body">
                        <div id="keyword-chart"></div>
                    </div>
                </div>
            </div>

            <!-- Recommendations -->
            <div class="col-12 mb-4">
                <div class="card">
                    <div class="card-header">
                        <h5>Recommendations</h5>
                    </div>
                    <div class="card-body">
                        <div id="recommendations-list"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="/static/js/app.js"></script>
    <script src="/static/js/dashboard.js"></script>
</body>
</html>
```

### 4. Create CSS Styles (`web/static/css/`)

**New directory**: `web/static/css/`

Implement modern, responsive styles:

**Main styles** (`web/static/css/style.css`):
```css
:root {
    --primary-color: #007bff;
    --success-color: #28a745;
    --warning-color: #ffc107;
    --danger-color: #dc3545;
    --dark-color: #343a40;
    --light-color: #f8f9fa;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: var(--light-color);
}

.drop-zone {
    border: 2px dashed #ccc;
    border-radius: 10px;
    padding: 40px;
    text-align: center;
    transition: all 0.3s ease;
    cursor: pointer;
}

.drop-zone:hover {
    border-color: var(--primary-color);
    background-color: rgba(0, 123, 255, 0.05);
}

.drop-zone.dragover {
    border-color: var(--success-color);
    background-color: rgba(40, 167, 69, 0.1);
}

.drop-zone-content {
    color: #666;
}

.progress {
    height: 20px;
    border-radius: 10px;
}

.progress-bar {
    border-radius: 10px;
    transition: width 0.3s ease;
}

.card {
    border: none;
    border-radius: 15px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    margin-bottom: 20px;
}

.card-header {
    background: linear-gradient(135deg, var(--primary-color), #0056b3);
    color: white;
    border-radius: 15px 15px 0 0;
    border: none;
}

.btn {
    border-radius: 25px;
    padding: 10px 30px;
    font-weight: 500;
    transition: all 0.3s ease;
}

.btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.chart-container {
    position: relative;
    height: 300px;
    margin: 20px 0;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
    .container {
        padding: 10px;
    }
    
    .drop-zone {
        padding: 20px;
    }
    
    .card {
        margin-bottom: 15px;
    }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
    body {
        background-color: #1a1a1a;
        color: #ffffff;
    }
    
    .card {
        background-color: #2d2d2d;
        color: #ffffff;
    }
    
    .drop-zone {
        background-color: #2d2d2d;
        border-color: #555;
    }
}
```

### 5. Create API Endpoints (`src/web_api.py`)

**New file**: `src/web_api.py`

Implement comprehensive API endpoints:

```python
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
import asyncio
import json
from typing import List, Optional

router = APIRouter()

@router.post("/api/analyze")
async def analyze_job_application(
    job_file: UploadFile = File(...),
    resume_file: UploadFile = File(...),
    options: dict = None,
    background_tasks: BackgroundTasks = None
):
    """Analyze job application with real-time updates"""
    try:
        # Validate file types
        if not job_file.content_type.startswith(('text/', 'application/pdf')):
            raise HTTPException(400, "Invalid job file type")
        if not resume_file.content_type.startswith(('text/', 'application/pdf')):
            raise HTTPException(400, "Invalid resume file type")
        
        # Start analysis in background
        session_id = generate_session_id()
        background_tasks.add_task(
            run_analysis_with_updates,
            session_id,
            job_file,
            resume_file,
            options or {}
        )
        
        return {
            "session_id": session_id,
            "status": "started",
            "message": "Analysis started successfully"
        }
    except Exception as e:
        raise HTTPException(500, f"Analysis failed: {str(e)}")

@router.get("/api/analytics")
async def get_analytics(user_id: str = None):
    """Get comprehensive analytics data"""
    try:
        from src.graph_analytics import GraphAnalytics
        from src.knowledge_graph import Neo4jKnowledgeGraph
        
        kg = Neo4jKnowledgeGraph(Config.NEO4J_URI, Config.NEO4J_USER, Config.NEO4J_PASSWORD)
        analytics = GraphAnalytics(kg)
        
        user_id = user_id or Config.USER_ID
        analytics_data = analytics.get_comprehensive_analytics(user_id)
        
        kg.close()
        return analytics_data
    except Exception as e:
        raise HTTPException(500, f"Failed to get analytics: {str(e)}")

@router.get("/api/applications")
async def get_applications(user_id: str = None, status: str = None):
    """Get tracked applications with optional filtering"""
    try:
        from src.knowledge_graph import Neo4jKnowledgeGraph
        
        kg = Neo4jKnowledgeGraph(Config.NEO4J_URI, Config.NEO4J_USER, Config.NEO4J_PASSWORD)
        applications = kg.get_application_history(user_id or Config.USER_ID)
        
        if status:
            applications = [app for app in applications if app.get('status') == status]
        
        kg.close()
        return {"applications": applications}
    except Exception as e:
        raise HTTPException(500, f"Failed to get applications: {str(e)}")

@router.post("/api/applications/{app_id}/status")
async def update_application_status(app_id: str, status: str):
    """Update application status"""
    try:
        from src.knowledge_graph import Neo4jKnowledgeGraph
        
        valid_statuses = ['Applied', 'Interview', 'Rejected', 'Offer', 'Accepted']
        if status not in valid_statuses:
            raise HTTPException(400, f"Invalid status. Must be one of: {valid_statuses}")
        
        kg = Neo4jKnowledgeGraph(Config.NEO4J_URI, Config.NEO4J_USER, Config.NEO4J_PASSWORD)
        success = kg.update_application_status(app_id, status)
        
        kg.close()
        
        if success:
            return {"message": "Status updated successfully"}
        else:
            raise HTTPException(404, "Application not found")
    except Exception as e:
        raise HTTPException(500, f"Failed to update status: {str(e)}")

@router.get("/api/export/{format}")
async def export_data(format: str, user_id: str = None):
    """Export data in specified format (csv, json, pdf)"""
    try:
        from src.dashboard import ApplicationDashboard
        from src.knowledge_graph import Neo4jKnowledgeGraph
        
        kg = Neo4jKnowledgeGraph(Config.NEO4J_URI, Config.NEO4J_USER, Config.NEO4J_PASSWORD)
        analytics = GraphAnalytics(kg)
        dashboard = ApplicationDashboard(analytics)
        
        user_id = user_id or Config.USER_ID
        
        if format == "csv":
            output_path = f"/tmp/export_{user_id}.csv"
            dashboard.export_to_csv(analytics.get_application_history(user_id), output_path)
            return StreamingResponse(
                open(output_path, 'rb'),
                media_type='text/csv',
                headers={"Content-Disposition": f"attachment; filename=applications_{user_id}.csv"}
            )
        elif format == "json":
            data = analytics.get_comprehensive_analytics(user_id)
            return JSONResponse(content=data)
        elif format == "pdf":
            # Generate PDF report
            output_path = f"/tmp/report_{user_id}.pdf"
            dashboard.generate_pdf_report(user_id, output_path)
            return StreamingResponse(
                open(output_path, 'rb'),
                media_type='application/pdf',
                headers={"Content-Disposition": f"attachment; filename=report_{user_id}.pdf"}
            )
        else:
            raise HTTPException(400, "Invalid format. Must be csv, json, or pdf")
    except Exception as e:
        raise HTTPException(500, f"Export failed: {str(e)}")

async def run_analysis_with_updates(session_id: str, job_file: UploadFile, resume_file: UploadFile, options: dict):
    """Run analysis with WebSocket updates"""
    try:
        # This would integrate with existing analyzer
        # and send updates via WebSocket
        pass
    except Exception as e:
        # Send error update via WebSocket
        pass
```

### 6. Create WebSocket Handler (`src/websocket_handler.py`)

**New file**: `src/websocket_handler.py`

Implement real-time communication:

```python
from fastapi import WebSocket
import json
import asyncio
from typing import Dict

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
    
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
    
    async def send_update(self, session_id: str, data: dict):
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            try:
                await websocket.send_text(json.dumps(data))
            except:
                self.disconnect(session_id)
    
    async def send_progress(self, session_id: str, progress: int, status: str):
        await self.send_update(session_id, {
            "type": "progress",
            "progress": progress,
            "status": status
        })
    
    async def send_complete(self, session_id: str, results: dict):
        await self.send_update(session_id, {
            "type": "complete",
            "results": results
        })
    
    async def send_error(self, session_id: str, error: str):
        await self.send_update(session_id, {
            "type": "error",
            "error": error
        })

# Global WebSocket manager
websocket_manager = WebSocketManager()
```

### 7. Update Main Application (`main.py`)

**Modify existing**: `main.py`

Add web server mode:

```python
parser.add_argument(
    "--web-server",
    action="store_true",
    help="Start web server mode"
)

parser.add_argument(
    "--host",
    default="127.0.0.1",
    help="Host for web server (default: 127.0.0.1)"
)

parser.add_argument(
    "--port",
    type=int,
    default=8000,
    help="Port for web server (default: 8000)"
)

# Add web server handler
if args.web_server:
    import uvicorn
    from src.web_interface import app
    
    console.print(f"[green]Starting web server on http://{args.host}:{args.port}[/green]")
    console.print("[blue]Press Ctrl+C to stop[/blue]")
    
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level="info"
    )
    return 0
```

### 8. Update Configuration (`config.py`)

**Modify existing**: `config.py`

Add web interface configuration:

```python
# Web Interface settings
WEB_SERVER_ENABLED = os.getenv("WEB_SERVER_ENABLED", "true").lower() == "true"
WEB_HOST = os.getenv("WEB_HOST", "127.0.0.1")
WEB_PORT = int(os.getenv("WEB_PORT", "8000"))
WEB_DEBUG = os.getenv("WEB_DEBUG", "false").lower() == "true"

# Static files and templates
STATIC_DIR = os.getenv("STATIC_DIR", "web/static")
TEMPLATES_DIR = os.getenv("TEMPLATES_DIR", "web/templates")

# WebSocket settings
WEBSOCKET_TIMEOUT = int(os.getenv("WEBSOCKET_TIMEOUT", "300"))  # seconds
MAX_CONNECTIONS = int(os.getenv("MAX_CONNECTIONS", "100"))

# Security settings
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
```

### 9. Create Docker Configuration (`Dockerfile`)

**New file**: `Dockerfile`

Containerize the web application:

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e .

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p web/static web/templates data/industries data/questions

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["python", "main.py", "--web-server", "--host", "0.0.0.0", "--port", "8000"]
```

**Docker Compose** (`docker-compose.yml`):
```yaml
version: '3.8'

services:
  job-agent:
    build: .
    ports:
      - "8000:8000"
    environment:
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USER=neo4j
      - NEO4J_PASSWORD=password
    depends_on:
      - neo4j
    volumes:
      - ./data:/app/data
      - ./web:/app/web

  neo4j:
    image: neo4j:latest
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      - NEO4J_AUTH=neo4j/password
    volumes:
      - neo4j_data:/data

volumes:
  neo4j_data:
```

### 10. Update Documentation

**Modify**: `README.md`

Add new sections:

**Web Interface** (new major section):
- Explain web server mode
- Document `--web-server` command
- Document `--host` and `--port` options
- Show web interface features
- Explain real-time updates
- Document dashboard components

**API Endpoints** (new section):
- Document all API endpoints
- Show request/response examples
- Explain WebSocket usage
- Document authentication (if implemented)

**Deployment** (new section):
- Docker deployment instructions
- Docker Compose setup
- Environment configuration
- Production deployment considerations

**Environment Variables** (update existing):
```
WEB_SERVER_ENABLED=true
WEB_HOST=127.0.0.1
WEB_PORT=8000
WEB_DEBUG=false
STATIC_DIR=web/static
TEMPLATES_DIR=web/templates
WEBSOCKET_TIMEOUT=300
MAX_CONNECTIONS=100
CORS_ORIGINS=*
SECRET_KEY=your-secret-key-here
```

**Update**: `.env.example`

Add web interface configuration template.

### 11. Update Dependencies

**Modify**: `pyproject.toml`

Add to dependencies:
```toml
"fastapi>=0.100.0",  # Web framework
"uvicorn>=0.23.0",  # ASGI server
"jinja2>=3.1.0",  # Template engine
"python-multipart>=0.0.6",  # File uploads
"websockets>=11.0.0",  # WebSocket support
"python-jose>=3.3.0",  # JWT tokens (if auth needed)
"passlib>=1.7.4",  # Password hashing (if auth needed)
"bcrypt>=4.0.0",  # Password hashing (if auth needed)
```

## Testing Strategy

1. Test web server startup and shutdown
2. Test file upload functionality
3. Test real-time WebSocket updates
4. Test all API endpoints
5. Test dashboard visualizations
6. Test mobile responsiveness
7. Test dark/light mode switching
8. Test Docker deployment
9. Test performance with multiple users
10. Test error handling and recovery

## Integration Points

**With all previous phases**:
- Seamless integration with all backend functionality
- Real-time updates for all analysis types
- Visual representation of all data
- Export functionality for all features

**With existing CLI**:
- Web interface provides same functionality as CLI
- CLI can still be used for automation
- Web interface adds visual and interactive elements

## Security Considerations

- Input validation for all file uploads
- CORS configuration for cross-origin requests
- Rate limiting for API endpoints
- Secure file handling and storage
- WebSocket connection security
- Authentication and session management (if implemented)
- HTTPS support for production

## Performance Considerations

- Async/await for all I/O operations
- Connection pooling for database
- Caching for static assets
- WebSocket connection management
- File upload size limits
- Background task processing
- CDN for static assets (production)

## Files to Create/Modify

**New Files**:
- `src/web_interface.py` (Main FastAPI application)
- `src/web_api.py` (API endpoints)
- `src/websocket_handler.py` (WebSocket management)
- `web/templates/dashboard.html` (Main dashboard template)
- `web/static/js/app.js` (Main JavaScript application)
- `web/static/js/dashboard.js` (Dashboard components)
- `web/static/css/style.css` (Main stylesheet)
- `Dockerfile` (Docker configuration)
- `docker-compose.yml` (Docker Compose setup)

**Modified Files**:
- `main.py` (Add web server mode)
- `config.py` (Add web configuration)
- `README.md` (Add web interface documentation)
- `.env.example` (Add web variables)
- `pyproject.toml` (Add web dependencies)

## Success Criteria

- Web interface loads and functions correctly
- File upload works with drag-and-drop
- Real-time updates work during analysis
- All dashboard components display correctly
- Mobile responsiveness works on all devices
- API endpoints return correct data
- WebSocket connections are stable
- Docker deployment works
- Performance is acceptable (< 3s page load)
- Documentation is complete with examples

## Future Enhancements (Phase 6.5)

- User authentication and accounts
- Multi-user support with data isolation
- Advanced visualizations and charts
- Real-time collaboration features
- Mobile app (React Native/Flutter)
- Progressive Web App (PWA) support
- Advanced analytics and reporting
- Integration with external job boards
- Social features and sharing
- Advanced customization options

## To-dos

- [ ] Create src/web_interface.py with FastAPI application setup
- [ ] Create src/web_api.py with comprehensive API endpoints
- [ ] Create src/websocket_handler.py for real-time communication
- [ ] Create web/templates/dashboard.html with responsive design
- [ ] Create web/static/js/app.js with modern JavaScript frontend
- [ ] Create web/static/js/dashboard.js with dashboard components
- [ ] Create web/static/css/style.css with responsive styling
- [ ] Create Dockerfile and docker-compose.yml for containerization
- [ ] Update main.py to add web server mode
- [ ] Add web interface configuration options to config.py
- [ ] Update README.md with web interface documentation
- [ ] Add FastAPI, uvicorn, and web dependencies to pyproject.toml
