# Configuration Guide

Complete configuration guide for the Job Application Agent.

## Environment Setup

Create a `.env` file in the project root:

```bash
cp .env.example .env
# Edit .env with your API keys
```

## Basic Configuration

### API Keys

```bash
# For Claude (recommended)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# For Ollama (local models)
OLLAMA_BASE_URL=http://localhost:11434
```

## Error Handling Configuration

Optional settings for error handling and retry logic:

```bash
MAX_LLM_RETRIES=3              # Maximum retry attempts
LLM_RETRY_DELAY=1.0            # Initial delay between retries (seconds)
LLM_BACKOFF_FACTOR=2.0         # Exponential backoff multiplier
LLM_MAX_DELAY=60.0             # Maximum delay between retries (seconds)
ENABLE_RETRY_LOGIC=true        # Enable/disable retry logic
```

## Structured Parsing Configuration

Optional settings for structured output parsing:

```bash
STRUCTURED_PARSING_ENABLED=true # Enable structured parsing
FALLBACK_TO_REGEX=true         # Enable regex fallback
RESPONSE_VALIDATION_ENABLED=true # Enable response validation
```

## Cache Encryption Configuration

### Basic Settings

```bash
# Enable/disable encryption
CACHE_ENCRYPTION_ENABLED=true

# Choose authentication method
CACHE_AUTH_METHOD=password  # or keyfile, yubikey

# Set cache expiry (days)
CACHE_EXPIRY_DAYS=90
```

### Encryption Methods

**Password-based (default)**
- Simple password protection
- No additional setup required

**Keyfile**
- Use a secure key file for encryption
- Generate a keyfile and specify its path

**YubiKey (optional)**
- Hardware key authentication with PIN
- Requires `yubikey-manager` package

```bash
# YubiKey settings
CACHE_AUTH_METHOD=yubikey
YUBIKEY_SERIAL=12345678
YUBIKEY_PIN=your_pin
```

Install YubiKey support:
```bash
uv add yubikey-manager
```

## Security Features

The application includes comprehensive data encryption for GDPR compliance:

- **AES-256-GCM encryption** for all cached data
- **Secure file deletion** with multiple overwrite passes
- **Hardware key support** for enhanced security
- **Automatic cleanup** of expired data (configurable, default: 90 days)
- **Export functionality** for data portability

## Configuration Best Practices

1. **API Keys**: Never commit your `.env` file to version control
2. **Encryption**: Enable encryption for sensitive data
3. **Cache Expiry**: Set appropriate expiry times based on your data retention needs
4. **YubiKey**: Use hardware keys for enhanced security in production environments

## Multi-Agent Settings

Enable and configure the multi-agent workflow via environment variables:

```bash
# Core switches
MULTI_AGENT_ENABLED=true
AGENT_PARALLEL_EXECUTION=false
QUALITY_REVIEW_ENABLED=true

# Optional advisory agents
ENABLE_CAREER_ADVISOR=false
ENABLE_LEARNING_PLAN=false

# Orchestrator behavior
AGENT_MAX_RETRIES=2
AGENT_BACKOFF_FACTOR=2.0
```

Notes:
- You can also enable per-run via CLI flags (`--multi-agent`, `--enable-career-advisor`, `--enable-learning-plan`).
- Parallel execution can be enabled later; defaults to sequential for predictability.

