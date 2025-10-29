# Usage Guide

Complete guide to using the Job Application Agent command-line interface.

## Quick Start

```bash
python main.py --job "https://example.com/job-posting" --resume resume.docx
```

## Basic Commands

### Job Analysis

```bash
# Analyze a job from URL
python main.py --job "https://company.com/careers/software-engineer" --resume my_resume.docx

# Analyze from file
python main.py --job job.txt --resume resume.md

# Specify LLM provider
python main.py --job job.txt --resume resume.md --provider claude

# Use local Ollama
python main.py --job job.txt --resume resume.docx --provider ollama
```

### Output Options

```bash
# Plain text output (default)
python main.py --job job.txt --resume resume.docx

# JSON console output (automatically creates Markdown report)
python main.py --job job.txt --resume resume.docx --format json

# Save results to JSON file (displays console output AND saves JSON)
python main.py --job job.txt --resume resume.docx --output results.json

# Creates both results.json AND results.md
python main.py --job job.txt --resume resume.docx --output results.json
```

## Application Tracking

### Track Applications

```bash
# Track an application during analysis
python main.py --job job.txt --resume resume.docx --track --email "user@example.com" --name "Your Name"

# List all tracked applications
python main.py --list-applications

# Update application status
python main.py --update-status "under_review" --application-id 1

# Delete an application (with confirmation)
python main.py --delete-application 1

# Delete without confirmation prompt (use with caution)
python main.py --delete-application 1 --force-delete

# View analytics dashboard
python main.py --analytics

# Export all application data
python main.py --export-data applications.json
```

### Application Statuses

- `draft`: Application being prepared
- `applied`: Application submitted
- `under_review`: Application under review
- `interview_scheduled`: Interview scheduled
- `interview_completed`: Interview completed
- `offer_received`: Job offer received
- `rejected`: Application rejected
- `withdrawn`: Application withdrawn
- `accepted`: Job offer accepted

## Resume Optimization

```bash
# Analyze resume for ATS compatibility
python main.py --analyze-resume resume.pdf

# Analyze with job description for keyword matching
python main.py --analyze-resume resume.pdf --job job.txt

# Calculate comprehensive resume score
python main.py --score-resume resume.pdf --job job.txt

# Save optimization results to file
python main.py --analyze-resume resume.pdf --optimization-output results.json
```

## Career Analytics

```bash
# Analyze career progression
python main.py --analyze-career-progression --resume resume.pdf

# Get industry trend insights
python main.py --analyze-industry-trends --skills "Python,JavaScript,React"

# Generate personalized recommendations
python main.py --generate-recommendations --resume resume.pdf --current-title "Software Developer"

# Create comprehensive analytics dashboard
python main.py --create-analytics-dashboard --resume resume.pdf --skills "Python,JavaScript"

# Export analytics data
python main.py --export-analytics --output analytics.json
```

## LangChain Integration

```bash
# Basic LangChain analysis
python main.py --job job.txt --resume resume.pdf --langchain

# With RAG for similar application insights
python main.py --job job.txt --resume resume.pdf --langchain --enable-rag

# With iterative resume tailoring
python main.py --job job.txt --resume resume.pdf --langchain --enable-tailoring

# View LangChain metrics
python main.py --langchain-metrics

# Export metrics to file
python main.py --export-metrics metrics.json
```

## Cache Management

```bash
# Show cache statistics (including cache directory location)
python main.py --cache-stats

# Clear resume cache
python main.py --clear-cache

# Export cached data to JSON file
python main.py --export-cache cache_backup.json
```

**Cache Location**: The resume cache is stored in your system's default cache directory:
- **macOS**: `~/Library/Caches/job-application-agent/job-application-agent/`
- **Linux**: `~/.cache/job-application-agent/job-application-agent/`
- **Windows**: `%LOCALAPPDATA%\job-application-agent\job-application-agent\`

## MCP Server Mode

```bash
# Run as MCP server for AI assistant integration
python main.py --mcp-server
```

See [MCP Server Integration](#mcp-server-integration) section for setup details.

## Command Line Options

### Core Options

- `--job, -j`: Job description file path or URL (required)
- `--resume, -r`: Resume file path (required)
- `--provider, -p`: LLM provider (claude/ollama, auto-detect if not specified)
- `--output, -o`: Output file path (optional). Saves JSON to file while also displaying console output
- `--format, -f`: Output format for console display (text/json, default: text)
- `--verbose, -v`: Enable verbose output
- `--clear-cache`: Clear resume cache and exit
- `--cache-stats`: Show cache statistics and exit
- `--mcp-server`: Run as MCP server for AI assistant integration

### Application Tracking Options

- `--track`: Track this application in the database
- `--email`: Email address for application tracking (required with --track)
- `--name`: Your name for application tracking (required with --track)
- `--list-applications`: List all tracked applications
- `--update-status`: Update application status (draft, applied, under_review, etc.)
- `--application-id`: Application ID for status updates
- `--delete-application`: Delete an application and all related records (requires confirmation)
- `--force-delete`: Skip confirmation prompt when deleting applications (use with caution)
- `--analytics`: Show application analytics and insights
- `--export-data`: Export all application data to JSON file

### Resume Optimization Options

- `--analyze-resume`: Analyze resume for ATS compatibility
- `--score-resume`: Calculate comprehensive resume score
- `--optimization-output`: File path for optimization results

### Career Analytics Options

- `--analyze-career-progression`: Analyze career progression
- `--analyze-industry-trends`: Get industry trend insights
- `--generate-recommendations`: Generate personalized recommendations
- `--create-analytics-dashboard`: Create comprehensive analytics dashboard
- `--export-analytics`: Export analytics data

### LangChain Options

- `--langchain`: Enable LangChain analysis
- `--enable-rag`: Enable RAG for similar application insights
- `--enable-tailoring`: Enable iterative resume tailoring
- `--langchain-metrics`: View LangChain metrics
- `--export-metrics`: Export metrics to file

## Supported Formats

### Job Descriptions
- **URLs**: Automatically scrapes job posting content
- **Files**: Text (.txt) or Markdown (.md) files

### Resumes
- **Word Documents**: .docx files
- **PDF**: .pdf files
- **Text Files**: .txt, .md, .markdown files

## Output Format

The agent provides:

1. **Suitability Rating**: 1-10 scale with recommendation
2. **Detailed Analysis**: Strengths, gaps, and missing requirements
3. **Application Materials** (if recommended):
   - Resume improvement suggestions
   - Tailored cover letter
   - Interview questions to ask
   - Anticipated interview questions with answers
   - Next steps action plan

## Automatic Markdown Generation

When using JSON output format, the agent automatically creates a human-readable Markdown report:

- **With File Output**: Creates both `results.json` AND `results.md`
- **With JSON Console Output**: Creates `job_analysis_YYYYMMDD_HHMMSS.md` automatically

The Markdown report includes structured sections, professional formatting, timestamps, and complete analysis results for easy sharing.

## MCP Server Integration

The job application agent can run as an MCP (Model Context Protocol) server, allowing it to be used as a tool within AI assistants like Claude Desktop.

### Setup for Claude Desktop

1. **Install the agent** (if not already done):
```bash
pip install -e .
```

2. **Configure Claude Desktop** by adding to your MCP settings:
```json
{
  "mcpServers": {
    "job-application-agent": {
      "command": "python",
      "args": ["/path/to/job-application-agent/main.py", "--mcp-server"],
      "env": {
        "ANTHROPIC_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

3. **Available MCP Tools**:
   - `analyze_job_application`: Complete job application analysis
   - `get_resume_improvements`: Resume improvement suggestions
   - `generate_cover_letter`: Tailored cover letter generation
   - `prepare_interview_questions`: Interview preparation
   - `get_next_steps`: Action plan for job application

### Usage in AI Assistants

Once configured, you can use natural language commands like:
- "Analyze this job posting against my resume"
- "Generate a cover letter for this position"
- "What improvements should I make to my resume for this job?"
- "Prepare me for the interview for this role"

