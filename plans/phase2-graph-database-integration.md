# Phase 2: Graph Database Knowledge Store & Application Tracking

## Overview

Implement Neo4j graph database to store job applications, companies, skills, and their relationships. Enable intelligent pattern recognition, career path analysis, and application tracking with analytics and reporting.

## Prerequisites

- Phase 1 (Encryption) completed
- Neo4j installed and running (see NEO4J_SETUP.md)
- neo4j Python driver installed

## Implementation Steps

### 1. Create Knowledge Graph Module (`src/knowledge_graph.py`)

**New file**: `src/knowledge_graph.py`

Implement `Neo4jKnowledgeGraph` class with:

**Core functionality**:
- Connection management to Neo4j
- Constraint setup for unique node IDs
- CRUD operations for nodes (Person, Application, Company, Job, Skill, Industry, Resume)
- Relationship creation between nodes
- Query methods for complex graph traversals

**Key methods**:
```python
class Neo4jKnowledgeGraph:
    def __init__(self, uri: str, user: str, password: str)
    def _setup_constraints(self)  # Create unique constraints
    def close(self)  # Close driver connection
    
    # Node creation
    def create_application_node(self, application_data: dict) -> str
    def create_company_node(self, company_data: dict) -> str
    def create_skill_node(self, skill: str, category: str) -> str
    def create_job_node(self, job_data: dict) -> str
    def create_person_node(self, person_data: dict) -> str
    
    # Relationship creation
    def create_relationship(self, from_label: str, to_label: str, 
                          from_id: str, to_id: str, rel_type: str, 
                          properties: dict = None)
    
    # Query methods
    def find_similar_companies(self, person_id: str) -> list
    def identify_skill_gaps(self, person_id: str, target_job: str) -> list
    def find_career_paths(self, current_role: str) -> list
    def get_application_history(self, person_id: str) -> list
```

**Node types to support**:
- Person (user profile)
- Application (job applications)
- Company (employers)
- Job (job postings)
- Skill (technical/soft skills)
- Industry (industry sectors)
- Resume (resume versions)

**Relationship types**:
- APPLIED_TO (Person -> Application)
- AT_COMPANY (Application -> Company)
- REQUIRES_SKILL (Job -> Skill)
- HAS_SKILL (Person -> Skill)
- SIMILAR_TO (Company -> Company, Job -> Job)
- IN_INDUSTRY (Company -> Industry)
- USED_RESUME (Application -> Resume)

### 2. Create Entity Extraction Module (`src/entity_extractor.py`)

**New file**: `src/entity_extractor.py`

Extract entities from job descriptions and resumes to populate the graph:

```python
class EntityExtractor:
    def __init__(self, llm_provider):
        self.llm = llm_provider
    
    def extract_from_job_description(self, job_desc: str) -> dict:
        # Extract: company, job title, skills, industry, seniority, location
        # Returns: {
        #   'company': str,
        #   'job_title': str,
        #   'skills': List[str],
        #   'industry': str,
        #   'seniority': str,
        #   'location': str,
        #   'salary_range': str
        # }
    
    def extract_from_resume(self, resume: str) -> dict:
        # Extract: name, email, skills, experience
        # Returns: {
        #   'name': str,
        #   'email': str,
        #   'skills': List[str],
        #   'years_experience': int
        # }
    
    def categorize_skills(self, skills: List[str]) -> dict:
        # Categorize skills as Technical, Soft, Domain-specific
        # Returns: {'Technical': [...], 'Soft': [...], 'Domain': [...]}
```

**Integration with LLM**:
- Use existing `llm_provider` to extract structured data
- Create prompts for entity extraction
- Parse LLM responses into structured format

### 3. Create Graph Analytics Module (`src/graph_analytics.py`)

**New file**: `src/graph_analytics.py`

Implement analytics and insights using graph queries:

```python
class GraphAnalytics:
    def __init__(self, knowledge_graph: Neo4jKnowledgeGraph):
        self.kg = knowledge_graph
    
    def get_application_stats(self, person_id: str) -> dict:
        # Total applications, by status, by industry
        # Returns: {
        #   'total': int,
        #   'by_status': {'Applied': int, 'Interview': int, ...},
        #   'by_industry': {'Tech': int, 'Finance': int, ...},
        #   'success_rate': float
        # }
    
    def find_skill_recommendations(self, person_id: str) -> List[dict]:
        # Suggest skills to develop based on target jobs
        # Returns: [{'skill': str, 'importance': int, 'jobs_requiring': int}]
    
    def analyze_company_patterns(self, person_id: str) -> dict:
        # Which companies respond, average response time
        # Returns: {
        #   'responsive_companies': List[str],
        #   'avg_response_days': float,
        #   'best_industries': List[str]
        # }
    
    def get_career_progression_paths(self, current_role: str) -> List[dict]:
        # Suggest next career steps based on skill overlap
        # Returns: [{'next_role': str, 'skill_overlap': int, 'skills_needed': List[str]}]
    
    def generate_insights_report(self, person_id: str) -> str:
        # Generate comprehensive insights report
```

### 4. Update Analyzer to Populate Graph (`src/analyzer.py`)

**Modify existing**: `src/analyzer.py`

Integration points in `JobApplicationAnalyzer`:

**After analysis completion** (around line 150+):
```python
def analyze(self, job_description: str, resume: str) -> dict:
    # ... existing analysis code ...
    
    # NEW: Populate knowledge graph
    if Config.GRAPH_DB_ENABLED:
        self._populate_knowledge_graph(job_description, resume, results)
    
    return results

def _populate_knowledge_graph(self, job_desc: str, resume: str, results: dict):
    """Extract entities and populate Neo4j graph"""
    from src.entity_extractor import EntityExtractor
    from src.knowledge_graph import Neo4jKnowledgeGraph
    
    # Extract entities
    extractor = EntityExtractor(self.llm)
    job_entities = extractor.extract_from_job_description(job_desc)
    resume_entities = extractor.extract_from_resume(resume)
    
    # Connect to graph
    kg = Neo4jKnowledgeGraph(
        uri=Config.NEO4J_URI,
        user=Config.NEO4J_USER,
        password=Config.NEO4J_PASSWORD
    )
    
    # Create nodes
    person_id = kg.create_person_node(resume_entities)
    company_id = kg.create_company_node(job_entities)
    app_id = kg.create_application_node({
        'job_title': job_entities['job_title'],
        'company': job_entities['company'],
        'applied_date': datetime.now(),
        'status': 'Applied',
        'fit_score': results.get('overall_score', 0)
    })
    
    # Create relationships
    kg.create_relationship('Person', 'Application', person_id, app_id, 'APPLIED_TO')
    kg.create_relationship('Application', 'Company', app_id, company_id, 'AT_COMPANY')
    
    # Add skills
    for skill in job_entities['skills']:
        skill_id = kg.create_skill_node(skill, 'Technical')
        kg.create_relationship('Job', 'Skill', job_entities['job_id'], skill_id, 'REQUIRES_SKILL')
    
    kg.close()
```

### 5. Add Application Tracking Commands (`main.py`)

**Modify existing**: `main.py`

Add new CLI commands for tracking:

```python
parser.add_argument(
    "--track-application",
    action="store_true",
    help="Save this analysis to application tracking database"
)

parser.add_argument(
    "--list-applications",
    action="store_true",
    help="List all tracked applications"
)

parser.add_argument(
    "--update-status",
    nargs=2,
    metavar=("APP_ID", "STATUS"),
    help="Update application status (Applied, Interview, Rejected, Offer, Accepted)"
)

parser.add_argument(
    "--application-stats",
    action="store_true",
    help="Show application statistics and insights"
)

parser.add_argument(
    "--career-insights",
    action="store_true",
    help="Get career path recommendations based on your applications"
)
```

**Command handlers**:
```python
# Handle tracking commands
if args.list_applications:
    from src.graph_analytics import GraphAnalytics
    from src.knowledge_graph import Neo4jKnowledgeGraph
    
    kg = Neo4jKnowledgeGraph(Config.NEO4J_URI, Config.NEO4J_USER, Config.NEO4J_PASSWORD)
    analytics = GraphAnalytics(kg)
    apps = analytics.get_application_history('default_user')
    # Display applications in table format
    kg.close()
    return 0

if args.update_status:
    app_id, status = args.update_status
    # Update application status in graph
    return 0

if args.application_stats:
    # Show comprehensive statistics
    return 0

if args.career_insights:
    # Show career path recommendations
    return 0
```

### 6. Update Configuration (`config.py`)

**Modify existing**: `config.py`

Add Neo4j configuration:

```python
# Neo4j Graph Database settings
GRAPH_DB_ENABLED = os.getenv("GRAPH_DB_ENABLED", "false").lower() == "true"
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

# User profile (for graph queries)
USER_ID = os.getenv("USER_ID", "default_user")
USER_NAME = os.getenv("USER_NAME", "")
USER_EMAIL = os.getenv("USER_EMAIL", "")
```

### 7. Create Application Dashboard Module (`src/dashboard.py`)

**New file**: `src/dashboard.py`

Create visual dashboard for application tracking:

```python
class ApplicationDashboard:
    def __init__(self, analytics: GraphAnalytics):
        self.analytics = analytics
    
    def generate_text_dashboard(self, person_id: str) -> str:
        # Generate rich text dashboard with statistics
        # Uses rich library for formatted output
    
    def generate_table_view(self, applications: List[dict]) -> str:
        # Generate table of applications
    
    def export_to_csv(self, applications: List[dict], output_path: str):
        # Export applications to CSV
    
    def export_to_json(self, applications: List[dict], output_path: str):
        # Export applications to JSON
```

### 8. Update Documentation

**Modify**: `README.md`

Add new sections:

**Application Tracking** (new major section):
- Explain graph database integration
- Document `--track-application` flag
- Document `--list-applications` command
- Document `--update-status` command
- Document `--application-stats` command
- Document `--career-insights` command

**Graph Database Setup** (new section):
- Link to NEO4J_SETUP.md
- Explain what data is stored in the graph
- Explain relationship types and their meaning
- Show example queries users can run

**Environment Variables** (update existing):
```
GRAPH_DB_ENABLED=true
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j
USER_ID=your_user_id
```

**Update**: `.env.example`

Add Neo4j configuration template.

### 9. Update Dependencies

**Modify**: `pyproject.toml`

Add to dependencies:
```toml
"neo4j>=5.0.0",  # Neo4j graph database driver
"pandas>=2.0.0",  # Data analysis for analytics
```

## Testing Strategy

1. Test Neo4j connection and constraint setup
2. Test node creation for all entity types
3. Test relationship creation
4. Test entity extraction from job descriptions
5. Test entity extraction from resumes
6. Test graph queries (similar companies, skill gaps, career paths)
7. Test application tracking workflow
8. Test analytics and reporting
9. Test dashboard generation
10. Test export functionality

## Integration Points

**With Phase 1 (Encryption)**:
- Graph database credentials stored encrypted
- Application data can be encrypted before storage

**With existing analyzer**:
- Automatic entity extraction after analysis
- Optional graph population (controlled by config)

**With cache system**:
- Cache entity extraction results
- Cache graph query results for performance

## Security Considerations

- Store Neo4j credentials securely (encrypted)
- Validate all inputs before graph queries
- Prevent Cypher injection attacks
- Implement access control for multi-user scenarios
- Encrypt sensitive data in graph nodes
- Regular graph database backups

## Performance Considerations

- Use indexes on frequently queried properties
- Batch node/relationship creation when possible
- Cache common query results
- Limit graph traversal depth
- Use EXPLAIN to optimize Cypher queries

## Files to Create/Modify

**New Files**:
- `src/knowledge_graph.py` (Neo4j integration)
- `src/entity_extractor.py` (Entity extraction from text)
- `src/graph_analytics.py` (Analytics and insights)
- `src/dashboard.py` (Application dashboard)

**Modified Files**:
- `src/analyzer.py` (Add graph population)
- `config.py` (Add Neo4j config)
- `main.py` (Add tracking commands)
- `README.md` (Add tracking documentation)
- `.env.example` (Add Neo4j variables)
- `pyproject.toml` (Add dependencies)

## Success Criteria

- Neo4j successfully stores applications and relationships
- Entity extraction works accurately for jobs and resumes
- Graph queries return relevant insights
- Application tracking commands work correctly
- Analytics provide actionable insights
- Dashboard displays comprehensive statistics
- Career path recommendations are relevant
- Performance is acceptable (< 2s for most queries)
- Documentation is clear and complete

## Future Enhancements (Phase 2.5)

- Company similarity scoring algorithm
- Job recommendation engine
- Skill clustering and categorization
- Network analysis (who works where)
- Time-series analysis (market trends)
- Integration with LinkedIn/job boards
- Collaborative filtering for recommendations

## To-dos

- [ ] Create src/knowledge_graph.py with Neo4jKnowledgeGraph class for node/relationship management
- [ ] Create src/entity_extractor.py to extract entities from job descriptions and resumes
- [ ] Create src/graph_analytics.py for analytics, insights, and pattern recognition
- [ ] Update src/analyzer.py to populate graph after analysis completion
- [ ] Add application tracking CLI commands to main.py (list, update-status, stats, insights)
- [ ] Add Neo4j configuration options to config.py
- [ ] Create src/dashboard.py for application tracking dashboard and export
- [ ] Update README.md with application tracking, graph database, and new commands documentation
- [ ] Add neo4j and pandas dependencies to pyproject.toml
