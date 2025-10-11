# Job Application Agent

An AI-powered agent that analyzes job postings against resumes to assess suitability and provide comprehensive recommendations for job applications.

## Features

- **Smart Analysis**: Rates job suitability on a 1-10 scale with detailed breakdown
- **Multiple Input Formats**: Supports job descriptions from URLs or files, resumes in text, Markdown, or Word formats
- **AI-Powered**: Uses Claude or Ollama for intelligent analysis
- **Comprehensive Output**: Generates resume improvements, cover letters, interview questions, and action plans
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

# Save results to file
python main.py --job job.txt --resume resume.docx --output results.json

# JSON output format
python main.py --job job.txt --resume resume.docx --format json
```

### Command Line Options

- `--job, -j`: Job description file path or URL (required)
- `--resume, -r`: Resume file path (required)
- `--provider, -p`: LLM provider (claude/ollama, auto-detect if not specified)
- `--output, -o`: Output file path (optional)
- `--format, -f`: Output format (console/json, default: console)
- `--verbose, -v`: Enable verbose output

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

### Save results to file
```bash
python main.py --job job_description.txt --resume resume.md --output analysis_results.json
```

### Use specific LLM provider
```bash
python main.py --job job.txt --resume resume.docx --provider ollama
```

## Requirements

- Python 3.13+
- Anthropic API key (for Claude) or Ollama (for local models)

## License

MIT License
