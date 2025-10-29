# Architecture & Technical Details

Technical documentation for the Job Application Agent architecture and implementation details.

## Structured Output Parsing

The Job Application Agent features a robust structured output parsing system that ensures reliable data extraction from LLM responses.

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

## Career Analytics

### Career Progression Tracking

- Analyze your current career stage and progression path
- Track skill development over time
- Identify career milestones and achievements

### Industry Trend Analysis

- Track skill demand trends and industry growth patterns
- Analyze market trends for your field
- Identify emerging technologies and skills

### Personalized Recommendations

- Get tailored advice based on your profile and market trends
- Competitive analysis and market positioning
- Salary benchmarking against industry standards
- Skill gap analysis for professional development

### Analytics Dashboard

Provides:
- **Career Score**: Overall career health and progression metrics
- **Skill Trends**: Demand analysis for your technical skills
- **Industry Insights**: Growth patterns and opportunities in your field
- **Recommendations**: Personalized action items for career growth
- **Competitive Position**: Market analysis and differentiation strategies

## Application Tracking Database

### Database Schema

The system tracks:
- **Persons**: User profiles with name and email
- **Companies**: Company information including industry, size, and location
- **Applications**: Job applications with status, dates, and notes
- **Analysis Results**: AI analysis results linked to applications
- **Interviews**: Interview tracking with questions and outcomes
- **Analytics Events**: Usage tracking for insights

### Features

- **Application Management**: Track job applications with company, position, and status information
- **Status Updates**: Update application status throughout the hiring process
- **Analytics Dashboard**: View success rates, application patterns, and insights
- **Data Export**: Export all application data to JSON for external use
- **Multi-User Support**: Separate data for different users based on email addresses

## LangChain Integration

### Components

- **LLM Wrapper**: Seamless integration with existing Claude/Ollama providers
- **Structured Parser**: Pydantic-based output parsing for reliable results
- **Entity Extractor**: Extract structured entities from job descriptions and resumes
- **RAG System**: Vector store for finding similar applications
- **Resume Tailor**: LangGraph workflow for iterative resume optimization
- **Observability**: Metrics tracking and performance monitoring

### Key Features

- **Structured Output Parsing**: Reliable JSON extraction using Pydantic models
- **RAG (Retrieval-Augmented Generation)**: Find similar applications and get insights
- **LangGraph Workflows**: Iterative resume optimization with state management
- **Advanced Caching**: Automatic response caching to reduce API costs
- **Observability**: Built-in metrics tracking and LangSmith integration
- **Entity Extraction**: Structured extraction of job and resume entities

## Cache Architecture

### Encrypted Caching

- **Data Encryption**: AES-256-GCM encryption for all cached data
- **Secure Storage**: Encrypted cache entries with automatic expiration
- **Authentication**: Multiple authentication methods (password, keyfile, YubiKey)
- **Automatic Cleanup**: Expired entries are automatically removed
- **Export Functionality**: Export cached data for backup or portability

### Cache Management

- Cache entries automatically expire after configurable time (default: 90 days)
- Secure file deletion with multiple overwrite passes
- GDPR-compliant data retention policies
- Cross-platform cache directory management

## MCP Server Architecture

The agent can run as a Model Context Protocol (MCP) server, providing tools for AI assistants:

- **Tool Registration**: Registers analysis functions as MCP tools
- **Request Handling**: Processes MCP requests and returns structured responses
- **Error Handling**: Graceful error handling with proper MCP error responses
- **Integration Support**: Compatible with Claude Desktop and other MCP clients

### Available MCP Tools

- `analyze_job_application`: Complete job application analysis
- `get_resume_improvements`: Resume improvement suggestions
- `generate_cover_letter`: Tailored cover letter generation
- `prepare_interview_questions`: Interview preparation
- `get_next_steps`: Action plan for job application

