# Phase 3: Resume Optimization & Smart Tailoring

## Overview

Implement intelligent resume optimization system that analyzes job descriptions, identifies keyword gaps, provides ATS optimization, and generates tailored resume versions for specific job applications.

## Prerequisites

- Phase 1 (Encryption) completed
- Phase 2 (Graph Database) completed
- LLM provider configured and working

## Implementation Steps

### 1. Create Resume Optimizer Module (`src/resume_optimizer.py`)

**New file**: `src/resume_optimizer.py`

Implement `ResumeOptimizer` class with comprehensive analysis capabilities:

**Core functionality**:
- Extract keywords from job descriptions
- Analyze resume keyword density
- Identify missing keywords and skills
- Generate improvement suggestions
- Score ATS compatibility
- Suggest resume length optimizations

**Key methods**:
```python
class ResumeOptimizer:
    def __init__(self, llm_provider):
        self.llm = llm_provider
    
    def extract_keywords(self, job_description: str) -> dict:
        # Extract keywords with importance scores
        # Returns: {
        #   'required_skills': List[str],
        #   'preferred_skills': List[str],
        #   'keywords': List[str],
        #   'action_verbs': List[str],
        #   'technologies': List[str]
        # }
    
    def analyze_resume_keywords(self, resume: str, job_desc: str) -> dict:
        # Analyze keyword coverage
        # Returns: {
        #   'keyword_match_score': float,  # 0-100
        #   'missing_keywords': List[str],
        #   'present_keywords': List[str],
        #   'keyword_density': dict
        # }
    
    def check_ats_compatibility(self, resume: str) -> dict:
        # Check ATS-friendly formatting
        # Returns: {
        #   'ats_score': float,  # 0-100
        #   'issues': List[str],
        #   'recommendations': List[str]
        # }
    
    def suggest_improvements(self, job_desc: str, resume: str) -> dict:
        # Generate specific improvement suggestions
        # Returns: {
        #   'keyword_suggestions': List[str],
        #   'section_improvements': dict,
        #   'formatting_fixes': List[str],
        #   'content_enhancements': List[str]
        # }
    
    def calculate_resume_score(self, resume: str, job_desc: str) -> dict:
        # Overall resume optimization score
        # Returns: {
        #   'overall_score': float,
        #   'keyword_score': float,
        #   'ats_score': float,
        #   'length_score': float,
        #   'format_score': float
        # }
```

### 2. Create Smart Tailoring Module (`src/resume_tailor.py`)

**New file**: `src/resume_tailor.py`

Implement automated resume tailoring:

```python
class ResumeTailor:
    def __init__(self, llm_provider):
        self.llm = llm_provider
    
    def tailor_resume(self, resume: str, job_desc: str, style: str = 'moderate') -> str:
        # Generate tailored resume version
        # style: 'conservative', 'moderate', 'aggressive'
        # Returns: tailored resume text
    
    def insert_keywords(self, resume: str, keywords: List[str], context: str) -> str:
        # Intelligently insert missing keywords
        # Returns: updated resume with keywords
    
    def rewrite_bullet_points(self, bullet_points: List[str], job_desc: str) -> List[str]:
        # Optimize bullet points for specific job
        # Returns: rewritten bullet points
    
    def reorder_sections(self, resume: str, job_desc: str) -> str:
        # Prioritize most relevant sections
        # Returns: reordered resume
    
    def optimize_length(self, resume: str, target_pages: int = 1) -> str:
        # Optimize resume to target length
        # Returns: optimized resume
    
    def generate_summary(self, resume: str, job_desc: str) -> str:
        # Generate job-specific professional summary
        # Returns: tailored summary paragraph
```

### 3. Create ATS Analyzer Module (`src/ats_analyzer.py`)

**New file**: `src/ats_analyzer.py`

Implement ATS compatibility checking:

```python
class ATSAnalyzer:
    def check_formatting(self, resume_text: str) -> dict:
        # Check for ATS-unfriendly formatting
        # Returns: {
        #   'has_tables': bool,
        #   'has_images': bool,
        #   'has_headers_footers': bool,
        #   'has_columns': bool,
        #   'has_text_boxes': bool,
        #   'issues': List[str]
        # }
    
    def check_file_format(self, file_path: str) -> dict:
        # Check if file format is ATS-friendly
        # Returns: {
        #   'format': str,  # .docx, .pdf, .txt
        #   'is_ats_friendly': bool,
        #   'recommendation': str
        # }
    
    def check_section_headers(self, resume_text: str) -> dict:
        # Check for standard section headers
        # Returns: {
        #   'standard_headers': List[str],
        #   'non_standard_headers': List[str],
        #   'missing_headers': List[str]
        # }
    
    def check_contact_info(self, resume_text: str) -> dict:
        # Verify contact information is parseable
        # Returns: {
        #   'has_email': bool,
        #   'has_phone': bool,
        #   'has_location': bool,
        #   'format_issues': List[str]
        # }
    
    def generate_ats_report(self, resume_text: str, file_path: str) -> dict:
        # Comprehensive ATS compatibility report
        # Returns: {
        #   'overall_score': float,
        #   'formatting_score': float,
        #   'structure_score': float,
        #   'issues': List[dict],
        #   'recommendations': List[str]
        # }
```

### 4. Create Resume Version Manager (`src/resume_versions.py`)

**New file**: `src/resume_versions.py`

Manage multiple resume versions:

```python
class ResumeVersionManager:
    def __init__(self, storage_dir: str = None):
        self.storage_dir = storage_dir or Path.home() / '.job-agent' / 'resumes'
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def save_version(self, resume_text: str, job_title: str, company: str, 
                    metadata: dict = None) -> str:
        # Save tailored resume version
        # Returns: version_id
    
    def list_versions(self) -> List[dict]:
        # List all saved resume versions
        # Returns: [{'version_id': str, 'job_title': str, 'company': str, ...}]
    
    def get_version(self, version_id: str) -> dict:
        # Retrieve specific resume version
        # Returns: {'text': str, 'metadata': dict}
    
    def compare_versions(self, version_id1: str, version_id2: str) -> dict:
        # Compare two resume versions
        # Returns: {
        #   'differences': List[str],
        #   'keyword_changes': dict,
        #   'structure_changes': List[str]
        # }
    
    def delete_version(self, version_id: str) -> bool:
        # Delete a resume version
        # Returns: success status
```

### 5. Update Analyzer with Optimization (`src/analyzer.py`)

**Modify existing**: `src/analyzer.py`

Add resume optimization to analysis workflow:

**Integration point** (after main analysis, around line 150+):
```python
def analyze(self, job_description: str, resume: str) -> dict:
    # ... existing analysis code ...
    
    # NEW: Add resume optimization analysis
    if Config.RESUME_OPTIMIZATION_ENABLED:
        optimization_results = self._analyze_resume_optimization(job_description, resume)
        results['resume_optimization'] = optimization_results
    
    return results

def _analyze_resume_optimization(self, job_desc: str, resume: str) -> dict:
    """Analyze resume optimization opportunities"""
    from src.resume_optimizer import ResumeOptimizer
    from src.ats_analyzer import ATSAnalyzer
    
    optimizer = ResumeOptimizer(self.llm)
    ats_analyzer = ATSAnalyzer()
    
    # Keyword analysis
    keywords = optimizer.extract_keywords(job_desc)
    keyword_analysis = optimizer.analyze_resume_keywords(resume, job_desc)
    
    # ATS compatibility
    ats_report = ats_analyzer.generate_ats_report(resume, "")
    
    # Overall score
    resume_score = optimizer.calculate_resume_score(resume, job_desc)
    
    # Improvement suggestions
    suggestions = optimizer.suggest_improvements(job_desc, resume)
    
    return {
        'keywords': keywords,
        'keyword_analysis': keyword_analysis,
        'ats_report': ats_report,
        'resume_score': resume_score,
        'suggestions': suggestions
    }
```

### 6. Add Optimization Commands (`main.py`)

**Modify existing**: `main.py`

Add new CLI commands for resume optimization:

```python
parser.add_argument(
    "--optimize-resume",
    action="store_true",
    help="Show resume optimization suggestions"
)

parser.add_argument(
    "--tailor-resume",
    metavar="OUTPUT",
    help="Generate tailored resume version and save to OUTPUT file"
)

parser.add_argument(
    "--check-ats",
    action="store_true",
    help="Check resume ATS compatibility"
)

parser.add_argument(
    "--list-resume-versions",
    action="store_true",
    help="List all saved resume versions"
)

parser.add_argument(
    "--tailoring-style",
    choices=["conservative", "moderate", "aggressive"],
    default="moderate",
    help="Resume tailoring aggressiveness"
)
```

**Command handlers**:
```python
# Handle optimization commands
if args.optimize_resume:
    from src.resume_optimizer import ResumeOptimizer
    optimizer = ResumeOptimizer(llm)
    suggestions = optimizer.suggest_improvements(job_description, resume)
    # Display optimization suggestions
    return 0

if args.tailor_resume:
    from src.resume_tailor import ResumeTailor
    from src.resume_versions import ResumeVersionManager
    
    tailor = ResumeTailor(llm)
    version_mgr = ResumeVersionManager()
    
    # Generate tailored resume
    tailored = tailor.tailor_resume(resume, job_description, args.tailoring_style)
    
    # Save version
    version_id = version_mgr.save_version(
        tailored, 
        job_title="Extracted from job desc",
        company="Extracted from job desc"
    )
    
    # Write to output file
    with open(args.tailor_resume, 'w') as f:
        f.write(tailored)
    
    console.print(f"[green]Tailored resume saved to: {args.tailor_resume}[/green]")
    console.print(f"[blue]Version ID: {version_id}[/blue]")
    return 0

if args.check_ats:
    from src.ats_analyzer import ATSAnalyzer
    ats = ATSAnalyzer()
    report = ats.generate_ats_report(resume, args.resume)
    # Display ATS report
    return 0

if args.list_resume_versions:
    from src.resume_versions import ResumeVersionManager
    version_mgr = ResumeVersionManager()
    versions = version_mgr.list_versions()
    # Display versions in table format
    return 0
```

### 7. Update Configuration (`config.py`)

**Modify existing**: `config.py`

Add resume optimization configuration:

```python
# Resume Optimization settings
RESUME_OPTIMIZATION_ENABLED = os.getenv("RESUME_OPTIMIZATION_ENABLED", "true").lower() == "true"
DEFAULT_TAILORING_STYLE = os.getenv("DEFAULT_TAILORING_STYLE", "moderate")
RESUME_STORAGE_DIR = os.getenv("RESUME_STORAGE_DIR", "")
ATS_STRICT_MODE = os.getenv("ATS_STRICT_MODE", "false").lower() == "true"

# Optimization thresholds
KEYWORD_MATCH_THRESHOLD = float(os.getenv("KEYWORD_MATCH_THRESHOLD", "70.0"))
ATS_SCORE_THRESHOLD = float(os.getenv("ATS_SCORE_THRESHOLD", "80.0"))
```

### 8. Create Optimization Output Formatter (`src/optimization_formatter.py`)

**New file**: `src/optimization_formatter.py`

Format optimization results for display:

```python
class OptimizationFormatter:
    def format_keyword_analysis(self, analysis: dict) -> str:
        # Format keyword analysis for console output
        # Uses rich library for formatted display
    
    def format_ats_report(self, report: dict) -> str:
        # Format ATS report with color coding
    
    def format_suggestions(self, suggestions: dict) -> str:
        # Format improvement suggestions
    
    def format_resume_score(self, score: dict) -> str:
        # Format resume score with progress bars
    
    def generate_optimization_report(self, optimization_data: dict, output_path: str):
        # Generate comprehensive optimization report as markdown
```

### 9. Update Documentation

**Modify**: `README.md`

Add new sections:

**Resume Optimization** (new major section):
- Explain keyword analysis and matching
- Document `--optimize-resume` command
- Document `--tailor-resume` command
- Document `--check-ats` command
- Document `--list-resume-versions` command
- Explain tailoring styles (conservative, moderate, aggressive)

**ATS Compatibility** (new section):
- Explain what ATS systems look for
- List common ATS pitfalls
- Provide ATS-friendly formatting guidelines
- Explain ATS scoring system

**Resume Versioning** (new section):
- Explain why multiple versions are useful
- Document version management commands
- Show how to compare versions

**Environment Variables** (update existing):
```
RESUME_OPTIMIZATION_ENABLED=true
DEFAULT_TAILORING_STYLE=moderate
RESUME_STORAGE_DIR=/path/to/resumes
ATS_STRICT_MODE=false
KEYWORD_MATCH_THRESHOLD=70.0
ATS_SCORE_THRESHOLD=80.0
```

**Update**: `.env.example`

Add resume optimization configuration template.

### 10. Update Dependencies

**Modify**: `pyproject.toml`

Add to dependencies (if needed):
```toml
"python-docx>=1.1.0",  # Already included - for Word document handling
"pypdf>=3.0.0",  # PDF parsing for ATS analysis
```

## Testing Strategy

1. Test keyword extraction from various job descriptions
2. Test keyword matching with different resume formats
3. Test ATS compatibility checking with known good/bad resumes
4. Test resume tailoring with different styles
5. Test version management (save, list, retrieve, delete)
6. Test integration with main analysis workflow
7. Test output formatting for all optimization results
8. Test with real job descriptions and resumes

## Integration Points

**With Phase 1 (Encryption)**:
- Encrypted storage of resume versions
- Secure handling of personal information

**With Phase 2 (Graph Database)**:
- Store resume versions in graph
- Track which resume version was used for each application
- Analyze which resume styles perform better

**With existing analyzer**:
- Seamless integration with current analysis workflow
- Optional optimization (controlled by config)

## Security Considerations

- Encrypt stored resume versions
- Sanitize personal information in examples
- Secure file handling for resume uploads
- Validate all file inputs
- Prevent path traversal attacks in version storage

## Performance Considerations

- Cache keyword extraction results
- Batch process multiple resumes
- Optimize LLM calls for tailoring
- Limit resume version storage size
- Implement cleanup of old versions

## Files to Create/Modify

**New Files**:
- `src/resume_optimizer.py` (Keyword analysis and scoring)
- `src/resume_tailor.py` (Smart tailoring)
- `src/ats_analyzer.py` (ATS compatibility checking)
- `src/resume_versions.py` (Version management)
- `src/optimization_formatter.py` (Output formatting)

**Modified Files**:
- `src/analyzer.py` (Add optimization analysis)
- `config.py` (Add optimization config)
- `main.py` (Add optimization commands)
- `README.md` (Add optimization documentation)
- `.env.example` (Add optimization variables)
- `pyproject.toml` (Add dependencies if needed)

## Success Criteria

- Keyword extraction accuracy > 90%
- ATS compatibility detection works for common issues
- Tailored resumes maintain original meaning while improving keyword match
- Resume versions are properly stored and retrievable
- Optimization suggestions are actionable and specific
- ATS score correlates with actual ATS performance
- Performance is acceptable (< 5s for full optimization)
- Documentation is clear with examples

## Future Enhancements (Phase 3.5)

- A/B testing of different resume versions
- Machine learning for keyword importance prediction
- Integration with LinkedIn profile optimization
- Resume template library
- Visual resume builder
- Multi-language support
- Industry-specific optimization rules
- Automated follow-up on resume performance

## To-dos

- [ ] Create src/resume_optimizer.py with keyword analysis and scoring
- [ ] Create src/resume_tailor.py for intelligent resume tailoring
- [ ] Create src/ats_analyzer.py for ATS compatibility checking
- [ ] Create src/resume_versions.py for version management
- [ ] Create src/optimization_formatter.py for output formatting
- [ ] Update src/analyzer.py to include optimization analysis
- [ ] Add optimization configuration options to config.py
- [ ] Add optimization CLI commands to main.py (optimize, tailor, check-ats, list-versions)
- [ ] Update README.md with resume optimization, ATS, and versioning documentation
- [ ] Add pypdf dependency to pyproject.toml if needed
- [ ] Create .env.example entries for optimization settings
