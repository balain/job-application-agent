# Web Interface & Real-time Collaboration

## Overview

Develop a modern web interface using FastAPI and React to provide an intuitive, real-time experience for job application analysis. This focuses on creating a responsive web application with real-time updates, file uploads, and collaborative features.

## Prerequisites

- Structured output parsing implemented
- Application tracking database implemented
- ATS optimization implemented
- LangChain integration implemented
- Existing CLI functionality working

## Implementation Steps

### 1. Create FastAPI Backend (`src/web_api.py`)

**New file**: `src/web_api.py`

Implement FastAPI web server:

```python
from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
import json
import uuid
from datetime import datetime
import os
from pathlib import Path

from .analyzer import JobApplicationAnalyzer
from .llm_provider import LLMProviderFactory
from .database_manager import DatabaseManager
from .application_tracker import ApplicationTracker
from config import Config

app = FastAPI(title="Job Application Agent API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
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
            try:
                await self.active_connections[session_id].send_text(json.dumps(data))
            except:
                self.disconnect(session_id)

manager = ConnectionManager()

# Pydantic models for API
class AnalysisRequest(BaseModel):
    job_description: str
    resume_text: str
    track_application: bool = True

class AnalysisResponse(BaseModel):
    session_id: str
    status: str
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class ApplicationUpdate(BaseModel):
    application_id: int
    status: str
    notes: Optional[str] = None
    interview_date: Optional[str] = None

# Initialize components
db_manager = DatabaseManager()
tracker = ApplicationTracker(db_manager)
llm_provider = LLMProviderFactory.create_provider(Config.DEFAULT_LLM_PROVIDER)
analyzer = JobApplicationAnalyzer(llm_provider)

@app.get("/")
async def read_root():
    """Serve the main web interface"""
    return HTMLResponse(content=open("web/index.html").read())

@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_application(request: AnalysisRequest):
    """Analyze job application"""
    session_id = str(uuid.uuid4())
    
    try:
        # Perform analysis
        results = analyzer.analyze_application(
            request.job_description,
            request.resume_text
        )
        
        # Track application if requested
        if request.track_application:
            app_id = tracker.track_application(
                job_description=request.job_description,
                resume_text=request.resume_text,
                analysis_results=results,
                person_name=Config.USER_NAME or "User",
                person_email=Config.USER_EMAIL or "user@example.com"
            )
            results['application_id'] = app_id
        
        return AnalysisResponse(
            session_id=session_id,
            status="success",
            results=results
        )
    
    except Exception as e:
        return AnalysisResponse(
            session_id=session_id,
            status="error",
            error=str(e)
        )

@app.post("/api/analyze-file")
async def analyze_from_files(
    job_file: UploadFile = File(...),
    resume_file: UploadFile = File(...),
    track_application: bool = True
):
    """Analyze application from uploaded files"""
    session_id = str(uuid.uuid4())
    
    try:
        # Read file contents
        job_content = await job_file.read()
        resume_content = await resume_file.read()
        
        # Convert to text (handle different formats)
        job_text = _extract_text_from_file(job_content, job_file.filename)
        resume_text = _extract_text_from_file(resume_content, resume_file.filename)
        
        # Perform analysis
        results = analyzer.analyze_application(job_text, resume_text)
        
        # Track application if requested
        if track_application:
            app_id = tracker.track_application(
                job_description=job_text,
                resume_text=resume_text,
                analysis_results=results,
                person_name=Config.USER_NAME or "User",
                person_email=Config.USER_EMAIL or "user@example.com"
            )
            results['application_id'] = app_id
        
        return AnalysisResponse(
            session_id=session_id,
            status="success",
            results=results
        )
    
    except Exception as e:
        return AnalysisResponse(
            session_id=session_id,
            status="error",
            error=str(e)
        )

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket, session_id)
    
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(session_id)

@app.get("/api/applications")
async def get_applications():
    """Get all tracked applications"""
    try:
        applications = tracker.get_application_history(
            Config.USER_EMAIL or "user@example.com"
        )
        return {"applications": applications}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/applications/{application_id}")
async def update_application(application_id: int, update: ApplicationUpdate):
    """Update application status"""
    try:
        interview_date = None
        if update.interview_date:
            interview_date = datetime.fromisoformat(update.interview_date)
        
        tracker.update_application_status(
            application_id,
            update.status,
            update.notes,
            interview_date
        )
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics")
async def get_analytics():
    """Get application analytics"""
    try:
        dashboard = tracker.get_analytics_dashboard(
            Config.USER_EMAIL or "user@example.com"
        )
        return dashboard
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ats-check")
async def check_ats_compatibility(resume_text: str, job_description: str = None):
    """Check ATS compatibility"""
    try:
        from .ats_analyzer import ATSAnalyzer
        from .resume_scorer import ResumeScorer
        
        ats_analyzer = ATSAnalyzer()
        scorer = ResumeScorer()
        
        ats_report = ats_analyzer.analyze_resume(resume_text, job_description)
        resume_score = scorer.score_resume(resume_text, job_description)
        
        return {
            "ats_report": {
                "overall_score": ats_report.overall_score,
                "formatting_score": ats_report.formatting_score,
                "structure_score": ats_report.structure_score,
                "keyword_score": ats_report.keyword_score,
                "ats_friendly": ats_report.ats_friendly,
                "issues": ats_report.issues,
                "recommendations": ats_report.recommendations
            },
            "resume_score": {
                "overall_score": resume_score.overall_score,
                "ats_score": resume_score.ats_score,
                "content_score": resume_score.content_score,
                "format_score": resume_score.format_score,
                "keyword_score": resume_score.keyword_score,
                "experience_score": resume_score.experience_score,
                "education_score": resume_score.education_score,
                "skills_score": resume_score.skills_score,
                "achievements_score": resume_score.achievements_score,
                "recommendations": resume_score.recommendations
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def _extract_text_from_file(content: bytes, filename: str) -> str:
    """Extract text from uploaded file"""
    file_ext = Path(filename).suffix.lower()
    
    if file_ext == '.txt':
        return content.decode('utf-8')
    elif file_ext == '.pdf':
        import PyPDF2
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    elif file_ext in ['.doc', '.docx']:
        from docx import Document
        doc = Document(io.BytesIO(content))
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    else:
        raise ValueError(f"Unsupported file format: {file_ext}")

# Serve static files
app.mount("/static", StaticFiles(directory="web/static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 2. Create React Frontend (`web/index.html`)

**New file**: `web/index.html`

Implement modern web interface:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Job Application Agent</title>
    <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://unpkg.com/axios/dist/axios.min.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <div id="root"></div>

    <script type="text/babel">
        const { useState, useEffect, useRef } = React;

        // Main App Component
        function App() {
            const [activeTab, setActiveTab] = useState('analyze');
            const [analysisResults, setAnalysisResults] = useState(null);
            const [applications, setApplications] = useState([]);
            const [analytics, setAnalytics] = useState(null);
            const [loading, setLoading] = useState(false);
            const [error, setError] = useState(null);

            // Load data on component mount
            useEffect(() => {
                loadApplications();
                loadAnalytics();
            }, []);

            const loadApplications = async () => {
                try {
                    const response = await axios.get('/api/applications');
                    setApplications(response.data.applications);
                } catch (err) {
                    console.error('Failed to load applications:', err);
                }
            };

            const loadAnalytics = async () => {
                try {
                    const response = await axios.get('/api/analytics');
                    setAnalytics(response.data);
                } catch (err) {
                    console.error('Failed to load analytics:', err);
                }
            };

            return (
                <div className="min-h-screen bg-gray-50">
                    {/* Header */}
                    <header className="bg-white shadow-sm border-b">
                        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                            <div className="flex justify-between items-center py-4">
                                <div className="flex items-center">
                                    <i className="fas fa-briefcase text-blue-600 text-2xl mr-3"></i>
                                    <h1 className="text-2xl font-bold text-gray-900">Job Application Agent</h1>
                                </div>
                                <div className="flex space-x-4">
                                    <button
                                        onClick={() => setActiveTab('analyze')}
                                        className={`px-4 py-2 rounded-md font-medium ${
                                            activeTab === 'analyze' 
                                                ? 'bg-blue-600 text-white' 
                                                : 'text-gray-600 hover:text-gray-900'
                                        }`}
                                    >
                                        <i className="fas fa-search mr-2"></i>Analyze
                                    </button>
                                    <button
                                        onClick={() => setActiveTab('applications')}
                                        className={`px-4 py-2 rounded-md font-medium ${
                                            activeTab === 'applications' 
                                                ? 'bg-blue-600 text-white' 
                                                : 'text-gray-600 hover:text-gray-900'
                                        }`}
                                    >
                                        <i className="fas fa-list mr-2"></i>Applications
                                    </button>
                                    <button
                                        onClick={() => setActiveTab('analytics')}
                                        className={`px-4 py-2 rounded-md font-medium ${
                                            activeTab === 'analytics' 
                                                ? 'bg-blue-600 text-white' 
                                                : 'text-gray-600 hover:text-gray-900'
                                        }`}
                                    >
                                        <i className="fas fa-chart-bar mr-2"></i>Analytics
                                    </button>
                                </div>
                            </div>
                        </div>
                    </header>

                    {/* Main Content */}
                    <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                        {activeTab === 'analyze' && (
                            <AnalysisTab 
                                onAnalysisComplete={(results) => {
                                    setAnalysisResults(results);
                                    loadApplications();
                                }}
                                loading={loading}
                                setLoading={setLoading}
                                error={error}
                                setError={setError}
                            />
                        )}
                        
                        {activeTab === 'applications' && (
                            <ApplicationsTab 
                                applications={applications}
                                onUpdate={() => loadApplications()}
                            />
                        )}
                        
                        {activeTab === 'analytics' && (
                            <AnalyticsTab analytics={analytics} />
                        )}
                    </main>
                </div>
            );
        }

        // Analysis Tab Component
        function AnalysisTab({ onAnalysisComplete, loading, setLoading, error, setError }) {
            const [jobDescription, setJobDescription] = useState('');
            const [resumeText, setResumeText] = useState('');
            const [trackApplication, setTrackApplication] = useState(true);
            const fileInputRef = useRef(null);

            const handleFileUpload = async (event) => {
                const files = event.target.files;
                if (files.length !== 2) {
                    setError('Please select exactly 2 files: job description and resume');
                    return;
                }

                setLoading(true);
                setError(null);

                try {
                    const formData = new FormData();
                    formData.append('job_file', files[0]);
                    formData.append('resume_file', files[1]);
                    formData.append('track_application', trackApplication);

                    const response = await axios.post('/api/analyze-file', formData, {
                        headers: { 'Content-Type': 'multipart/form-data' }
                    });

                    if (response.data.status === 'success') {
                        onAnalysisComplete(response.data.results);
                    } else {
                        setError(response.data.error);
                    }
                } catch (err) {
                    setError(err.response?.data?.detail || 'Analysis failed');
                } finally {
                    setLoading(false);
                }
            };

            const handleTextAnalysis = async () => {
                if (!jobDescription.trim() || !resumeText.trim()) {
                    setError('Please provide both job description and resume text');
                    return;
                }

                setLoading(true);
                setError(null);

                try {
                    const response = await axios.post('/api/analyze', {
                        job_description: jobDescription,
                        resume_text: resumeText,
                        track_application: trackApplication
                    });

                    if (response.data.status === 'success') {
                        onAnalysisComplete(response.data.results);
                    } else {
                        setError(response.data.error);
                    }
                } catch (err) {
                    setError(err.response?.data?.detail || 'Analysis failed');
                } finally {
                    setLoading(false);
                }
            };

            return (
                <div className="space-y-6">
                    <div className="bg-white rounded-lg shadow p-6">
                        <h2 className="text-xl font-semibold mb-4">Job Application Analysis</h2>
                        
                        {/* File Upload Option */}
                        <div className="mb-6">
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Upload Files
                            </label>
                            <input
                                ref={fileInputRef}
                                type="file"
                                multiple
                                accept=".pdf,.doc,.docx,.txt"
                                onChange={handleFileUpload}
                                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                            />
                            <p className="text-xs text-gray-500 mt-1">
                                Select job description and resume files (PDF, DOC, DOCX, TXT)
                            </p>
                        </div>

                        {/* Text Input Option */}
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Job Description
                                </label>
                                <textarea
                                    value={jobDescription}
                                    onChange={(e) => setJobDescription(e.target.value)}
                                    rows={6}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    placeholder="Paste the job description here..."
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Resume Text
                                </label>
                                <textarea
                                    value={resumeText}
                                    onChange={(e) => setResumeText(e.target.value)}
                                    rows={8}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    placeholder="Paste your resume text here..."
                                />
                            </div>

                            <div className="flex items-center">
                                <input
                                    type="checkbox"
                                    id="trackApplication"
                                    checked={trackApplication}
                                    onChange={(e) => setTrackApplication(e.target.checked)}
                                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                                />
                                <label htmlFor="trackApplication" className="ml-2 block text-sm text-gray-700">
                                    Track this application in database
                                </label>
                            </div>

                            <button
                                onClick={handleTextAnalysis}
                                disabled={loading}
                                className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {loading ? (
                                    <>
                                        <i className="fas fa-spinner fa-spin mr-2"></i>
                                        Analyzing...
                                    </>
                                ) : (
                                    <>
                                        <i className="fas fa-search mr-2"></i>
                                        Analyze Application
                                    </>
                                )}
                            </button>
                        </div>

                        {error && (
                            <div className="mt-4 bg-red-50 border border-red-200 rounded-md p-4">
                                <div className="flex">
                                    <i className="fas fa-exclamation-circle text-red-400 mr-2"></i>
                                    <p className="text-red-800">{error}</p>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            );
        }

        // Applications Tab Component
        function ApplicationsTab({ applications, onUpdate }) {
            const [editingApp, setEditingApp] = useState(null);
            const [statusUpdate, setStatusUpdate] = useState('');

            const updateApplicationStatus = async (appId, status, notes = '') => {
                try {
                    await axios.put(`/api/applications/${appId}`, {
                        status: status,
                        notes: notes
                    });
                    onUpdate();
                    setEditingApp(null);
                } catch (err) {
                    console.error('Failed to update application:', err);
                }
            };

            return (
                <div className="space-y-6">
                    <div className="bg-white rounded-lg shadow">
                        <div className="px-6 py-4 border-b border-gray-200">
                            <h2 className="text-xl font-semibold">Application History</h2>
                        </div>
                        
                        <div className="overflow-x-auto">
                            <table className="min-w-full divide-y divide-gray-200">
                                <thead className="bg-gray-50">
                                    <tr>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Company
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Position
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Applied Date
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Status
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Score
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Actions
                                        </th>
                                    </tr>
                                </thead>
                                <tbody className="bg-white divide-y divide-gray-200">
                                    {applications.map((app) => (
                                        <tr key={app.id}>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                                {app.company}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                {app.job_title}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                {new Date(app.applied_date).toLocaleDateString()}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                                                    app.status === 'Applied' ? 'bg-blue-100 text-blue-800' :
                                                    app.status === 'Interview' ? 'bg-yellow-100 text-yellow-800' :
                                                    app.status === 'Offer' ? 'bg-green-100 text-green-800' :
                                                    app.status === 'Rejected' ? 'bg-red-100 text-red-800' :
                                                    'bg-gray-100 text-gray-800'
                                                }`}>
                                                    {app.status}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                {app.fit_score ? `${app.fit_score}/10` : 'N/A'}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                                <button
                                                    onClick={() => setEditingApp(app)}
                                                    className="text-blue-600 hover:text-blue-900"
                                                >
                                                    Update Status
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    {/* Status Update Modal */}
                    {editingApp && (
                        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
                            <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
                                <div className="mt-3">
                                    <h3 className="text-lg font-medium text-gray-900 mb-4">
                                        Update Application Status
                                    </h3>
                                    <div className="space-y-4">
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                                Status
                                            </label>
                                            <select
                                                value={statusUpdate}
                                                onChange={(e) => setStatusUpdate(e.target.value)}
                                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                            >
                                                <option value="">Select Status</option>
                                                <option value="Applied">Applied</option>
                                                <option value="Interview">Interview</option>
                                                <option value="Offer">Offer</option>
                                                <option value="Accepted">Accepted</option>
                                                <option value="Rejected">Rejected</option>
                                            </select>
                                        </div>
                                        <div className="flex justify-end space-x-3">
                                            <button
                                                onClick={() => setEditingApp(null)}
                                                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
                                            >
                                                Cancel
                                            </button>
                                            <button
                                                onClick={() => updateApplicationStatus(editingApp.id, statusUpdate)}
                                                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
                                            >
                                                Update
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            );
        }

        // Analytics Tab Component
        function AnalyticsTab({ analytics }) {
            if (!analytics) {
                return (
                    <div className="bg-white rounded-lg shadow p-6">
                        <p className="text-gray-500">Loading analytics...</p>
                    </div>
                );
            }

            return (
                <div className="space-y-6">
                    {/* Overview Stats */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                        <div className="bg-white rounded-lg shadow p-6">
                            <div className="flex items-center">
                                <div className="flex-shrink-0">
                                    <i className="fas fa-file-alt text-blue-600 text-2xl"></i>
                                </div>
                                <div className="ml-4">
                                    <p className="text-sm font-medium text-gray-500">Total Applications</p>
                                    <p className="text-2xl font-semibold text-gray-900">
                                        {analytics.overview?.total_applications || 0}
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white rounded-lg shadow p-6">
                            <div className="flex items-center">
                                <div className="flex-shrink-0">
                                    <i className="fas fa-percentage text-green-600 text-2xl"></i>
                                </div>
                                <div className="ml-4">
                                    <p className="text-sm font-medium text-gray-500">Success Rate</p>
                                    <p className="text-2xl font-semibold text-gray-900">
                                        {analytics.overview?.success_rate || 0}%
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white rounded-lg shadow p-6">
                            <div className="flex items-center">
                                <div className="flex-shrink-0">
                                    <i className="fas fa-clock text-yellow-600 text-2xl"></i>
                                </div>
                                <div className="ml-4">
                                    <p className="text-sm font-medium text-gray-500">Avg Response Time</p>
                                    <p className="text-2xl font-semibold text-gray-900">
                                        {analytics.overview?.average_response_days || 0} days
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white rounded-lg shadow p-6">
                            <div className="flex items-center">
                                <div className="flex-shrink-0">
                                    <i className="fas fa-industry text-purple-600 text-2xl"></i>
                                </div>
                                <div className="ml-4">
                                    <p className="text-sm font-medium text-gray-500">Industries</p>
                                    <p className="text-2xl font-semibold text-gray-900">
                                        {Object.keys(analytics.overview?.industry_breakdown || {}).length}
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Status Breakdown */}
                    <div className="bg-white rounded-lg shadow p-6">
                        <h3 className="text-lg font-medium text-gray-900 mb-4">Status Breakdown</h3>
                        <div className="space-y-2">
                            {Object.entries(analytics.overview?.status_breakdown || {}).map(([status, count]) => (
                                <div key={status} className="flex justify-between items-center">
                                    <span className="text-sm text-gray-600">{status}</span>
                                    <span className="text-sm font-medium text-gray-900">{count}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Recommendations */}
                    {analytics.recommendations && analytics.recommendations.length > 0 && (
                        <div className="bg-white rounded-lg shadow p-6">
                            <h3 className="text-lg font-medium text-gray-900 mb-4">Recommendations</h3>
                            <ul className="space-y-2">
                                {analytics.recommendations.map((rec, index) => (
                                    <li key={index} className="flex items-start">
                                        <i className="fas fa-lightbulb text-yellow-500 mr-2 mt-1"></i>
                                        <span className="text-sm text-gray-700">{rec}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
            );
        }

        // Render the app
        ReactDOM.render(<App />, document.getElementById('root'));
    </script>
</body>
</html>
```

### 3. Add Web Server Commands (`main.py`)

**Modify existing**: `main.py`

Add web server command:

```python
# Add new argument
parser.add_argument(
    "--web-server",
    action="store_true",
    help="Start web server interface"
)

parser.add_argument(
    "--port",
    type=int,
    default=8000,
    help="Port for web server (default: 8000)"
)

parser.add_argument(
    "--host",
    default="0.0.0.0",
    help="Host for web server (default: 0.0.0.0)"
)

# Add command handler
if args.web_server:
    import uvicorn
    from src.web_api import app
    
    console.print(f"[green]Starting web server on http://{args.host}:{args.port}[/green]")
    console.print("[blue]Press Ctrl+C to stop the server[/blue]")
    
    uvicorn.run(app, host=args.host, port=args.port)
    sys.exit(0)
```

### 4. Update Configuration (`config.py`)

**Modify existing**: `config.py`

Add web interface configuration:

```python
# Web interface settings
WEB_SERVER_ENABLED = os.getenv("WEB_SERVER_ENABLED", "true").lower() == "true"
WEB_HOST = os.getenv("WEB_HOST", "0.0.0.0")
WEB_PORT = int(os.getenv("WEB_PORT", "8000"))
WEB_CORS_ORIGINS = os.getenv("WEB_CORS_ORIGINS", "http://localhost:3000,http://localhost:8080").split(",")

# File upload settings
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
ALLOWED_FILE_TYPES = os.getenv("ALLOWED_FILE_TYPES", ".pdf,.doc,.docx,.txt").split(",")
```

### 5. Update Dependencies (`pyproject.toml`)

**Modify existing**: `pyproject.toml`

Add to dependencies:
```toml
"fastapi>=0.100.0",  # Web framework
"uvicorn>=0.20.0",  # ASGI server
"python-multipart>=0.0.6",  # File upload support
"PyPDF2>=3.0.0",  # PDF parsing
"python-docx>=1.1.0",  # Word document parsing
```

### 6. Create Web Directory Structure

**Create directories**:
```
web/
├── index.html
├── static/
│   ├── css/
│   ├── js/
│   └── images/
└── templates/
```

### 7. Update Documentation (`README.md`)

**Modify existing**: `README.md`

Add new sections:

**Web Interface** (new major section):
- Explain web interface features
- Document `--web-server` command
- Show screenshots and usage examples
- Explain file upload capabilities
- Document real-time features

**API Documentation** (new section):
- List all API endpoints
- Show request/response examples
- Document WebSocket usage
- Explain authentication (if added)

**Environment Variables** (update existing):
```
WEB_SERVER_ENABLED=true
WEB_HOST=0.0.0.0
WEB_PORT=8000
WEB_CORS_ORIGINS=http://localhost:3000,http://localhost:8080
MAX_FILE_SIZE=10485760
ALLOWED_FILE_TYPES=.pdf,.doc,.docx,.txt
```

## Testing Strategy

1. Test web server startup and shutdown
2. Test file upload functionality with different formats
3. Test text-based analysis through web interface
4. Test WebSocket real-time updates
5. Test application tracking through web interface
6. Test analytics dashboard functionality
7. Test responsive design on different screen sizes
8. Test error handling and user feedback

## Integration Points

**With Phase 1 (Structured Output)**:
- Uses structured data models for API responses
- Leverages improved parsing reliability

**With Phase 2 (Application Tracking)**:
- Integrates with database for application management
- Provides web interface for analytics

**With Phase 3 (ATS Optimization)**:
- Exposes ATS analysis through web API
- Provides real-time ATS checking

**With Phase 4 (LangChain)**:
- Uses LangChain for enhanced analysis
- Implements streaming responses

## Security Considerations

- Validate all file uploads
- Sanitize user inputs
- Implement rate limiting
- Secure WebSocket connections
- Validate file types and sizes
- Implement CORS properly

## Performance Considerations

- Use async operations for I/O
- Implement file upload progress
- Cache static assets
- Optimize database queries
- Implement connection pooling
- Use CDN for static files

## Files to Create/Modify

**New Files**:
- `src/web_api.py` (FastAPI web server)
- `web/index.html` (React frontend)
- `web/static/` (Static assets directory)

**Modified Files**:
- `main.py` (Add web server command)
- `config.py` (Add web configuration)
- `pyproject.toml` (Add web dependencies)
- `README.md` (Add web documentation)

## Success Criteria

- Web interface loads and functions correctly
- File upload works for all supported formats
- Real-time updates work via WebSocket
- Application tracking works through web interface
- Analytics dashboard displays correctly
- Responsive design works on mobile and desktop
- Performance is acceptable (< 2s for most operations)
- Error handling provides clear user feedback

## Future Enhancements

- User authentication and multi-user support
- Advanced file processing (OCR, image analysis)
- Real-time collaboration features
- Mobile app development
- Advanced analytics and reporting
- Integration with job boards
- Automated follow-up reminders

## To-dos

- [ ] Create src/web_api.py with FastAPI web server and all endpoints
- [ ] Create web/index.html with React frontend and all components
- [ ] Add web server CLI commands to main.py
- [ ] Add web interface configuration to config.py
- [ ] Add FastAPI, uvicorn, and file processing dependencies to pyproject.toml
- [ ] Create web directory structure and static assets
- [ ] Update README.md with web interface documentation
- [ ] Test web interface functionality and performance
