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
- **Application Tracking**: SQLite database for tracking job applications, status updates, and analytics
- **Analytics Dashboard**: Comprehensive insights into application success rates and patterns
- **Resume Optimization**: ATS compatibility analysis, resume scoring, and improvement recommendations
- **Career Analytics**: Career progression tracking, industry trend analysis, and personalized recommendations
- **LangChain Integration**: Advanced AI workflows with structured outputs, RAG, and iterative optimization

## LangChain Integration

The job application agent includes advanced LangChain integration for enhanced reliability, structured outputs, and intelligent workflows.

### Key LangChain Features

- **Structured Output Parsing**: Reliable JSON extraction using Pydantic models
- **RAG (Retrieval-Augmented Generation)**: Find similar applications and get insights
- **LangGraph Workflows**: Iterative resume optimization with state management
- **Advanced Caching**: Automatic response caching to reduce API costs
- **Observability**: Built-in metrics tracking and LangSmith integration
- **Entity Extraction**: Structured extraction of job and resume entities

### Usage

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

### LangChain Components

- **LLM Wrapper**: Seamless integration with existing Claude/Ollama providers
- **Structured Parser**: Pydantic-based output parsing for reliable results
- **Entity Extractor**: Extract structured entities from job descriptions and resumes
- **RAG System**: Vector store for finding similar applications
- **Resume Tailor**: LangGraph workflow for iterative resume optimization
- **Observability**: Metrics tracking and performance monitoring

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

## Resume Optimization & ATS Analysis

The Job Application Agent now includes comprehensive resume optimization features:

### ATS Compatibility Analysis
- **File Format Support**: PDF, DOCX, DOC, and TXT resume parsing
- **ATS Issue Detection**: Identifies problematic elements (tables, images, headers/footers)
- **Compatibility Scoring**: Rates ATS compatibility from 0-100%
- **Issue Categorization**: Critical, High, Medium, Low severity levels
- **Actionable Fixes**: Specific recommendations for each issue

### Resume Scoring System
- **Comprehensive Scoring**: 6-component scoring system (ATS, Content, Formatting, Keywords, Experience, Skills)
- **Weighted Scoring**: Configurable weights for different components
- **Job-Specific Analysis**: Keyword matching against job descriptions
- **Experience Evaluation**: Years of experience, leadership roles, quantified achievements
- **Skills Assessment**: Technical skills, soft skills, certifications, tools

### Optimization Recommendations
- **Priority Fixes**: Critical issues that must be addressed
- **Content Improvements**: Suggestions for better content structure
- **Formatting Suggestions**: ATS-friendly formatting recommendations
- **Keyword Additions**: Missing keywords from job descriptions
- **Section Recommendations**: Specific feedback for each resume section

### CLI Commands
```bash
# Analyze resume for ATS compatibility
python main.py --analyze-resume resume.pdf

# Analyze with job description for keyword matching
python main.py --analyze-resume resume.pdf --job job.txt

# Calculate comprehensive resume score
python main.py --score-resume resume.pdf --job job.txt

# Save results to file
python main.py --analyze-resume resume.pdf --optimization-output results.json
```

## Career Analytics & Insights

The Job Application Agent includes comprehensive career analytics to help you understand your professional trajectory and make informed career decisions:

### Features

- **Career Progression Tracking**: Analyze your current career stage and progression path
- **Industry Trend Analysis**: Track skill demand trends and industry growth patterns
- **Personalized Recommendations**: Get tailored advice based on your profile and market trends
- **Competitive Analysis**: Understand your market position and competitive advantages
- **Salary Benchmarking**: Compare your compensation against industry standards
- **Skill Gap Analysis**: Identify areas for professional development

### Career Analytics Usage

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

### Analytics Dashboard

The analytics dashboard provides:
- **Career Score**: Overall career health and progression metrics
- **Skill Trends**: Demand analysis for your technical skills
- **Industry Insights**: Growth patterns and opportunities in your field
- **Recommendations**: Personalized action items for career growth
- **Competitive Position**: Market analysis and differentiation strategies

## Application Tracking Database

The Job Application Agent now includes a comprehensive application tracking system using SQLite for local data storage:

### Features

- **Application Management**: Track job applications with company, position, and status information
- **Status Updates**: Update application status throughout the hiring process
- **Analytics Dashboard**: View success rates, application patterns, and insights
- **Data Export**: Export all application data to JSON for external use
- **Multi-User Support**: Separate data for different users based on email addresses

### Database Schema

The system tracks:
- **Persons**: User profiles with name and email
- **Companies**: Company information including industry, size, and location
- **Applications**: Job applications with status, dates, and notes
- **Analysis Results**: AI analysis results linked to applications
- **Interviews**: Interview tracking with questions and outcomes
- **Analytics Events**: Usage tracking for insights

### CLI Commands

```bash
# Track an application during analysis
python main.py --job job.txt --resume resume.docx --track --email "user@example.com" --name "Your Name"

# List all tracked applications
python main.py --list-applications

# Update application status
python main.py --update-status "under_review" --application-id 1

# View analytics dashboard
python main.py --analytics

# Export all data
python main.py --export-data applications.json

# Career Analytics Commands
python main.py --analyze-career-progression --resume resume.pdf
python main.py --analyze-industry-trends --skills "Python,JavaScript,React"
python main.py --generate-recommendations --resume resume.pdf --current-title "Software Developer"
python main.py --create-analytics-dashboard --resume resume.pdf --skills "Python,JavaScript"
python main.py --export-analytics --output analytics.json
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

## Installation

1. Clone the repository:
```bash
git clone https://github.com/balain/job-application-agent.git
cd job-application-agent
```

2. Install dependencies:
```bash
pip install -e .
```

**Key Dependencies:**
- `pydantic>=2.0.0`: Structured data validation and parsing
- `sqlalchemy>=2.0.0`: Database ORM for application tracking
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

### Application Tracking Usage

```bash
# Track an application during analysis
python main.py --job job.txt --resume resume.docx --track --email "user@example.com" --name "Your Name"

# List all tracked applications
python main.py --list-applications

# Update application status
python main.py --update-status "under_review" --application-id 1

# Delete an application and all related records (with confirmation)
python main.py --delete-application 1

# Delete without confirmation prompt (use with caution)
python main.py --delete-application 1 --force-delete

# View analytics dashboard
python main.py --analytics

# Export all application data
python main.py --export-data applications.json
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

**Application Tracking Options:**
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