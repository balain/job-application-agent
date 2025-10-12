# Job Application Agent

An AI-powered agent that analyzes job postings against resumes to assess suitability and provide comprehensive recommendations for job applications.

## Features

- **Smart Analysis**: Rates job suitability on a 1-10 scale with detailed breakdown
- **Multiple Input Formats**: Supports job descriptions from URLs or files, resumes in text, Markdown, or Word formats
- **AI-Powered**: Uses Claude or Ollama for intelligent analysis
- **Comprehensive Output**: Generates resume improvements, cover letters, interview questions, and action plans
- **Resume Caching**: Automatically caches parsed resume content in system cache directory for faster subsequent analyses
- **MCP Server**: Can run as Model Context Protocol server for AI assistant integration
- **Auto Markdown**: Automatically generates Markdown reports when using JSON output
- **Beautiful CLI**: Rich console output with progress indicators and formatted results

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd job-application-agent
```

2. Install dependencies:
```bash
pip install -e .
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

## Configuration

Create a `.env` file with your API keys:

```bash
# For Claude (recommended)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# For Ollama (local models)
OLLAMA_BASE_URL=http://localhost:11434
```

## Usage

### Basic Usage

```bash
python main.py --job "https://example.com/job-posting" --resume resume.docx
```

### Advanced Usage

```bash
# Specify LLM provider
python main.py --job job.txt --resume resume.md --provider claude

# Save results to JSON file (displays console output AND saves JSON)
python main.py --job job.txt --resume resume.docx --output results.json

# Plain text output (default)
python main.py --job job.txt --resume resume.docx

# JSON console output (automatically creates Markdown report)
python main.py --job job.txt --resume resume.docx --format json
```

### Command Line Options

- `--job, -j`: Job description file path or URL (required)
- `--resume, -r`: Resume file path (required)
- `--provider, -p`: LLM provider (claude/ollama, auto-detect if not specified)
- `--output, -o`: Output file path (optional). Saves JSON to file while also displaying console output
- `--format, -f`: Output format for console display (text/json, default: text)
- `--verbose, -v`: Enable verbose output
- `--clear-cache`: Clear resume cache and exit
- `--cache-stats`: Show cache statistics and exit
- `--mcp-server`: Run as MCP server for AI assistant integration

## Supported Formats

### Job Descriptions
- **URLs**: Automatically scrapes job posting content
- **Files**: Text (.txt) or Markdown (.md) files

### Resumes
- **Word Documents**: .docx files
- **Text Files**: .txt, .md, .markdown files

## Output

The agent provides:

1. **Suitability Rating**: 1-10 scale with recommendation
2. **Detailed Analysis**: Strengths, gaps, and missing requirements
3. **Application Materials** (if recommended):
   - Resume improvement suggestions
   - Tailored cover letter
   - Interview questions to ask
   - Anticipated interview questions with answers
   - Next steps action plan

## Examples

### Analyze a job from URL
```bash
python main.py --job "https://company.com/careers/software-engineer" --resume my_resume.docx
```

### Save results to file (dual output)
```bash
# Displays rich console output AND saves JSON to file
python main.py --job job_description.txt --resume resume.md --output analysis_results.json
```

### Use specific LLM provider
```bash
python main.py --job job.txt --resume resume.docx --provider ollama
```

### Cache management
```bash
# Show cache statistics (including cache directory location)
python main.py --cache-stats

# Clear resume cache
python main.py --clear-cache
```

**Cache Location**: The resume cache is stored in your system's default cache directory:
- **macOS**: `~/Library/Caches/job-application-agent/job-application-agent/`
- **Linux**: `~/.cache/job-application-agent/job-application-agent/`
- **Windows**: `%LOCALAPPDATA%\job-application-agent\job-application-agent\`

### MCP Server Mode
```bash
# Run as MCP server for AI assistant integration
python main.py --mcp-server
```

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

## Automatic Markdown Generation

When using JSON output format, the agent automatically creates a human-readable Markdown report:

### With File Output
```bash
# Creates both results.json AND results.md
python main.py --job job.txt --resume resume.docx --output results.json
```

### With JSON Console Output
```bash
# Creates job_analysis_YYYYMMDD_HHMMSS.md automatically
python main.py --job job.txt --resume resume.docx --format json
```

### Markdown Report Features
- **Structured sections**: Assessment summary, detailed analysis, application materials
- **Professional formatting**: Headers, bullet points, and clear organization
- **Timestamp**: Shows when the analysis was generated
- **Complete content**: All analysis results in readable format
- **Easy sharing**: Perfect for emailing or including in applications

## Requirements

- Python 3.13+
- Anthropic API key (for Claude) or Ollama (for local models)

## License

MIT License
