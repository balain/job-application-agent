# Dependencies

Complete list of dependencies for the Job Application Agent.

## Installation

Install all dependencies:
```bash
pip install -e .
```

## Core Dependencies

### Data Validation & Parsing
- `pydantic>=2.0.0`: Structured data validation and parsing

### Database
- `sqlalchemy>=2.0.0`: Database ORM for application tracking

### AI Integration
- `anthropic>=0.39.0`: Claude API integration

### Web & HTTP
- `requests>=2.32.0`: HTTP requests
- `beautifulsoup4>=4.12.0`: Web scraping

### Document Processing
- `python-docx>=1.1.0`: Word document parsing

### User Interface
- `rich>=13.7.0`: Beautiful CLI output

### Configuration & Environment
- `python-dotenv>=1.0.0`: Environment variable management

### Protocol Support
- `mcp>=1.0.0`: Model Context Protocol

### System Integration
- `platformdirs>=4.0.0`: Cross-platform directory management

### Security
- `cryptography>=41.0.0`: Encryption
- `yubikey-manager>=5.0.0`: YubiKey support (optional)

## Development Dependencies

- `pytest>=7.0.0`: Testing framework
- `pytest-asyncio>=0.21.0`: Async testing support

## Optional Dependencies

- `yubikey-manager>=5.0.0`: Required only for YubiKey hardware key support

Install YubiKey support:
```bash
uv add yubikey-manager
```

## Requirements

- Python 3.13+
- Anthropic API key (for Claude) or Ollama (for local models)

