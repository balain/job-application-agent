# Job Application Agent

An AI-powered analysis tool that evaluates job postings against resumes to assess suitability and provide comprehensive recommendations for job applications.

## ⚠️ Important: This is NOT an automated job application tool

This agent **analyzes and provides recommendations**

**What it does NOT do:**
- ❌ Automatically apply to jobs
- ❌ Scrape job listings from websites
- ❌ Submit applications on your behalf
- ❌ Fill out job application forms

**What it DOES do:**
- ✅ Analyzes job fit and provides suitability ratings
- ✅ Generates tailored application materials
- ✅ Prepares you for interviews
- ✅ Helps you decide which jobs to apply for

## How It Works

The Job Application Agent follows a structured workflow to analyze job applications:

![Workflow](app-workflow.png)


### Key Features

- **Smart Analysis**: Rates job suitability on a 1-10 scale with detailed breakdown
- **Structured Output Parsing**: Robust JSON-first parsing with regex fallback for reliable data extraction
- **Error Handling & Retry Logic**: Automatic retry with exponential backoff for LLM API calls
- **Multiple Input Formats**: Supports job descriptions from URLs or files, resumes in text, Markdown, or Word formats
- **AI-Powered**: Uses Claude or Ollama for intelligent analysis
- **Comprehensive Output**: Generates resume improvements, cover letters, interview questions, and action plans
- **Resume Caching**: Automatically caches parsed resume content for faster subsequent analyses
- **MCP Server**: Can run as Model Context Protocol server for AI assistant integration
- **Auto Markdown**: Automatically generates Markdown reports when using JSON output
- **Beautiful CLI**: Rich console output with progress indicators and formatted results

## Structured Output Parsing

The Job Application Agent now features a robust structured output parsing system that ensures reliable data extraction from LLM responses:

### JSON-First Approach
- **Primary Method**: Attempts to parse JSON responses from LLMs
- **Multiple Formats**: Supports markdown code blocks, generic code blocks, and plain JSON objects
- **Validation**: Uses Pydantic models for type-safe data validation

### Regex Fallback
- **Secondary Method**: Falls back to regex parsing when JSON parsing fails
- **Flexible Patterns**: Handles various LLM output formats and structures
- **Content Cleaning**: Automatically removes section headers and formats content

### Error Handling
- **Retry Logic**: Automatic retry with exponential backoff for transient failures
- **Error Categorization**: Intelligent error classification (rate limits, timeouts, authentication, etc.)
- **User-Friendly Messages**: Clear error messages for better user experience
- **Graceful Degradation**: Continues operation even when some components fail

### Configuration Options
```bash
# Environment variables for error handling
MAX_LLM_RETRIES=3              # Maximum retry attempts
LLM_RETRY_DELAY=1.0            # Initial delay between retries (seconds)
LLM_BACKOFF_FACTOR=2.0         # Exponential backoff multiplier
LLM_MAX_DELAY=60.0             # Maximum delay between retries (seconds)
ENABLE_RETRY_LOGIC=true        # Enable/disable retry logic
STRUCTURED_PARSING_ENABLED=true # Enable structured parsing
FALLBACK_TO_REGEX=true         # Enable regex fallback
RESPONSE_VALIDATION_ENABLED=true # Enable response validation
```

### Data Models
All LLM responses are parsed into structured Pydantic models:
- `JobAssessment`: Core assessment with rating, strengths, gaps, recommendation
- `ResumeImprovements`: Structured improvement suggestions
- `CoverLetter`: Cover letter components
- `InterviewQuestions`: Interview Q&A structure
- `NextSteps`: Action plan structure
- `AnalysisResult`: Complete analysis container
- `ErrorInfo`: Structured error information

## Installation

1. Clone the repository:
```bash
git clone https://github.com/username/job-application-agent.git
cd job-application-agent
```

2. Install dependencies:
```bash
pip install -e .
```

**Key Dependencies:**
- `pydantic>=2.0.0`: Structured data validation and parsing
- `anthropic>=0.39.0`: Claude API integration
- `requests>=2.32.0`: HTTP requests
- `beautifulsoup4>=4.12.0`: Web scraping
- `python-docx>=1.1.0`: Word document parsing
- `rich>=13.7.0`: Beautiful CLI output
- `python-dotenv>=1.0.0`: Environment variable management
- `mcp>=1.0.0`: Model Context Protocol
- `platformdirs>=4.0.0`: Cross-platform directory management
- `cryptography>=41.0.0`: Encryption
- `yubikey-manager>=5.0.0`: YubiKey support (optional)

**Development Dependencies:**
- `pytest>=7.0.0`: Testing framework
- `pytest-asyncio>=0.21.0`: Async testing support

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

# Error handling and retry settings (optional)
MAX_LLM_RETRIES=3
LLM_RETRY_DELAY=1.0
LLM_BACKOFF_FACTOR=2.0
LLM_MAX_DELAY=60.0
ENABLE_RETRY_LOGIC=true

# Structured parsing settings (optional)
STRUCTURED_PARSING_ENABLED=true
FALLBACK_TO_REGEX=true
RESPONSE_VALIDATION_ENABLED=true
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

## 🔒 **Cache Management & Security**

### **Encrypted Caching**
The application now includes comprehensive data encryption for GDPR compliance:

```bash
# Clear all cached data (with secure deletion)
python main.py --clear-cache

# Export cached data to JSON file
python main.py --export-cache cache_backup.json

# View detailed cache statistics
python main.py --cache-stats
```

### **Encryption Options**
- **Password-based**: Simple password protection (default)
- **Keyfile**: Use a secure key file for encryption
- **YubiKey**: Hardware key authentication with PIN (requires `yubikey-manager` package)

### **Automatic Data Expiry**
- Cache entries automatically expire after 90 days (configurable)
- Expired entries are cleaned up automatically
- GDPR-compliant data retention policies

### **Environment Configuration**
Copy `.env.example` to `.env` and configure:

```bash
# Enable/disable encryption
CACHE_ENCRYPTION_ENABLED=true

# Choose authentication method
CACHE_AUTH_METHOD=password  # or keyfile, yubikey

# Set cache expiry (days)
CACHE_EXPIRY_DAYS=90

# YubiKey settings (if using hardware key)
YUBIKEY_SERIAL=12345678
YUBIKEY_PIN=your_pin
```

### **Security Features**
- **AES-256-GCM encryption** for all cached data
- **Secure file deletion** with multiple overwrite passes
- **Hardware key support** for enhanced security
- **Automatic cleanup** of expired data
- **Export functionality** for data portability

### **YubiKey Hardware Key Support**
For enhanced security, you can use a YubiKey hardware key:

```bash
# Install YubiKey support (optional)
uv add yubikey-manager

# Configure in .env file
CACHE_AUTH_METHOD=yubikey
YUBIKEY_SERIAL=your_yubikey_serial
YUBIKEY_PIN=your_yubikey_pin
```

**Note**: YubiKey support requires the `yubikey-manager` package and a physical YubiKey device.

## 📋 **Documentation**

### **Future Development Plan**
- **[FUTURE.md](FUTURE.md)**: Comprehensive roadmap for enhancing the Job Application Agent
  - **6-phase implementation plan** with detailed technical specifications
  - **Graph database integration** with Neo4j for knowledge storage
  - **Advanced analytics** including application tracking and career insights
  - **Web interface development** for improved user experience
  - **Security enhancements** with data encryption and GDPR compliance
  - **Timeline**: 12-week implementation schedule with clear milestones

### **Graph Database Alternatives**
- **[GRAPH_DB_ALTERNATIVES.md](GRAPH_DB_ALTERNATIVES.md)**: Detailed comparison of graph database options
  - **6 major alternatives** analyzed: Neo4j, ArangoDB, Dgraph, JanusGraph, OrientDB, TinkerPop
  - **Feature comparison table** with ratings and capabilities
  - **Selection criteria** and justification for Neo4j choice
  - **Implementation examples** and code samples for each option
  - **Resource links** for further learning and documentation

## Requirements

- Python 3.13+
- Anthropic API key (for Claude) or Ollama (for local models)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.