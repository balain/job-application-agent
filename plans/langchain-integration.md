# LangChain & LangGraph Integration Guide

## Overview

This document outlines how to integrate LangChain and LangGraph into existing phases to improve reliability, maintainability, and capabilities of the Job Application Agent.

## Why LangChain/LangGraph?

### **LangChain Benefits**
- **Structured output parsing**: Reliable JSON extraction from LLM responses
- **Prompt management**: Versioned, testable prompt templates
- **Error handling**: Built-in retry logic and fallbacks
- **Caching**: Automatic response caching to reduce API calls
- **Observability**: Built-in tracing and debugging
- **RAG support**: Easy vector store integration

### **LangGraph Benefits**
- **Stateful workflows**: Maintain context across multiple steps
- **Conditional logic**: Dynamic workflow based on results
- **Multi-agent systems**: Coordinate multiple specialized agents
- **Cyclic workflows**: Iterative improvement loops
- **Human-in-the-loop**: Easy integration of user feedback

## Integration by Phase

### **Phase 1: Encryption & Cache Management**

**LangChain Integration**: Minimal (no LLM usage in this phase)

**Enhancement**: Add LangChain caching layer
```python
# src/llm_cache_wrapper.py
from langchain.cache import SQLiteCache
import langchain

# Initialize LangChain cache
langchain.llm_cache = SQLiteCache(
    database_path=str(cache_dir / "llm_cache.db")
)

# This will automatically cache all LLM responses
# Integrates with existing cache encryption
```

**New dependencies**:
```toml
"langchain>=0.1.0",
"langchain-anthropic>=0.1.0",  # For Claude
"langchain-community>=0.0.20",  # For Ollama
```

---

### **Phase 2: Graph Database & Application Tracking**

**LangChain Integration**: Entity extraction with structured outputs

**Create**: `src/langchain_extractors.py`
```python
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List

class JobEntities(BaseModel):
    """Structured job description entities"""
    company: str = Field(description="Company name")
    job_title: str = Field(description="Job title")
    skills: List[str] = Field(description="Required skills")
    industry: str = Field(description="Industry sector")
    seniority: str = Field(description="Seniority level")
    location: str = Field(description="Job location")
    salary_range: str = Field(description="Salary range if mentioned")

class ResumeEntities(BaseModel):
    """Structured resume entities"""
    name: str = Field(description="Candidate name")
    email: str = Field(description="Email address")
    skills: List[str] = Field(description="Skills listed")
    years_experience: int = Field(description="Total years of experience")
    current_role: str = Field(description="Current or most recent role")

class LangChainEntityExtractor:
    def __init__(self, llm):
        self.llm = llm
        self.job_parser = PydanticOutputParser(pydantic_object=JobEntities)
        self.resume_parser = PydanticOutputParser(pydantic_object=ResumeEntities)
    
    def extract_from_job_description(self, job_desc: str) -> JobEntities:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert at extracting structured information from job descriptions."),
            ("user", "{format_instructions}\n\nJob Description:\n{job_desc}")
        ])
        
        chain = prompt | self.llm | self.job_parser
        
        result = chain.invoke({
            "job_desc": job_desc,
            "format_instructions": self.job_parser.get_format_instructions()
        })
        
        return result
    
    def extract_from_resume(self, resume: str) -> ResumeEntities:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert at extracting structured information from resumes."),
            ("user", "{format_instructions}\n\nResume:\n{resume}")
        ])
        
        chain = prompt | self.llm | self.resume_parser
        
        result = chain.invoke({
            "resume": resume,
            "format_instructions": self.resume_parser.get_format_instructions()
        })
        
        return result
```

**RAG Integration**: Store and retrieve similar applications
```python
# src/application_rag.py
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document

class ApplicationRAG:
    def __init__(self, persist_directory: str = "./data/vectorstore"):
        self.embeddings = OpenAIEmbeddings()
        self.vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings
        )
    
    def add_application(self, app_data: dict):
        """Add application to vector store"""
        doc = Document(
            page_content=f"{app_data['job_title']} at {app_data['company']}",
            metadata=app_data
        )
        self.vectorstore.add_documents([doc])
    
    def find_similar_applications(self, query: str, k: int = 5) -> List[dict]:
        """Find similar applications using semantic search"""
        results = self.vectorstore.similarity_search(query, k=k)
        return [doc.metadata for doc in results]
```

**Update**: `src/entity_extractor.py` to use LangChain
```python
class EntityExtractor:
    def __init__(self, llm_provider):
        # Wrap existing LLM provider with LangChain
        from langchain_anthropic import ChatAnthropic
        from langchain_community.llms import Ollama
        
        if isinstance(llm_provider, ClaudeProvider):
            self.llm = ChatAnthropic(
                model=llm_provider.model,
                api_key=llm_provider.api_key
            )
        else:
            self.llm = Ollama(model=llm_provider.model)
        
        self.extractor = LangChainEntityExtractor(self.llm)
    
    def extract_from_job_description(self, job_desc: str) -> dict:
        entities = self.extractor.extract_from_job_description(job_desc)
        return entities.dict()
```

**New dependencies**:
```toml
"langchain-chroma>=0.1.0",  # Vector store
"chromadb>=0.4.0",  # Vector database
"openai>=1.0.0",  # For embeddings
```

---

### **Phase 3: Resume Optimization**

**LangChain Integration**: Structured optimization with chains

**Create**: `src/langchain_optimizer.py`
```python
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List

class KeywordAnalysis(BaseModel):
    """Structured keyword analysis"""
    required_skills: List[str] = Field(description="Required skills from job description")
    preferred_skills: List[str] = Field(description="Preferred skills")
    missing_keywords: List[str] = Field(description="Keywords missing from resume")
    present_keywords: List[str] = Field(description="Keywords present in resume")
    keyword_match_score: float = Field(description="Keyword match percentage 0-100")

class ResumeImprovements(BaseModel):
    """Structured improvement suggestions"""
    keyword_suggestions: List[str] = Field(description="Keywords to add")
    section_improvements: dict = Field(description="Section-specific improvements")
    formatting_fixes: List[str] = Field(description="Formatting issues to fix")
    content_enhancements: List[str] = Field(description="Content improvements")

class LangChainResumeOptimizer:
    def __init__(self, llm):
        self.llm = llm
        self.keyword_parser = PydanticOutputParser(pydantic_object=KeywordAnalysis)
        self.improvement_parser = PydanticOutputParser(pydantic_object=ResumeImprovements)
    
    def analyze_keywords(self, job_desc: str, resume: str) -> KeywordAnalysis:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert at analyzing keyword matches between job descriptions and resumes."),
            ("user", "{format_instructions}\n\nJob Description:\n{job_desc}\n\nResume:\n{resume}")
        ])
        
        chain = prompt | self.llm | self.keyword_parser
        
        return chain.invoke({
            "job_desc": job_desc,
            "resume": resume,
            "format_instructions": self.keyword_parser.get_format_instructions()
        })
    
    def suggest_improvements(self, job_desc: str, resume: str) -> ResumeImprovements:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert resume consultant. Provide specific, actionable improvements."),
            ("user", "{format_instructions}\n\nJob Description:\n{job_desc}\n\nResume:\n{resume}")
        ])
        
        chain = prompt | self.llm | self.improvement_parser
        
        return chain.invoke({
            "job_desc": job_desc,
            "resume": resume,
            "format_instructions": self.improvement_parser.get_format_instructions()
        })
```

**LangGraph Integration**: Iterative resume optimization

**Create**: `src/langgraph_tailor.py`
```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal

class ResumeTailorState(TypedDict):
    """State for resume tailoring workflow"""
    original_resume: str
    job_description: str
    tailored_resume: str
    ats_score: float
    keyword_score: float
    iterations: int
    max_iterations: int
    improvements: List[str]

class LangGraphResumeTailor:
    def __init__(self, llm):
        self.llm = llm
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        workflow = StateGraph(ResumeTailorState)
        
        # Add nodes
        workflow.add_node("analyze", self._analyze_node)
        workflow.add_node("tailor", self._tailor_node)
        workflow.add_node("validate", self._validate_node)
        
        # Set entry point
        workflow.set_entry_point("analyze")
        
        # Add edges
        workflow.add_edge("analyze", "tailor")
        workflow.add_edge("tailor", "validate")
        
        # Conditional edge: continue improving or finish
        workflow.add_conditional_edges(
            "validate",
            self._should_continue,
            {
                "continue": "analyze",
                "finish": END
            }
        )
        
        return workflow.compile()
    
    def _analyze_node(self, state: ResumeTailorState) -> ResumeTailorState:
        """Analyze current resume against job description"""
        # Use LangChain optimizer
        optimizer = LangChainResumeOptimizer(self.llm)
        analysis = optimizer.analyze_keywords(
            state["job_description"],
            state.get("tailored_resume", state["original_resume"])
        )
        
        state["keyword_score"] = analysis.keyword_match_score
        return state
    
    def _tailor_node(self, state: ResumeTailorState) -> ResumeTailorState:
        """Tailor resume based on analysis"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert resume writer. Improve this resume for the job description."),
            ("user", "Job Description:\n{job_desc}\n\nResume:\n{resume}\n\nImprove the resume to better match the job.")
        ])
        
        chain = prompt | self.llm
        
        result = chain.invoke({
            "job_desc": state["job_description"],
            "resume": state.get("tailored_resume", state["original_resume"])
        })
        
        state["tailored_resume"] = result.content
        state["iterations"] = state.get("iterations", 0) + 1
        return state
    
    def _validate_node(self, state: ResumeTailorState) -> ResumeTailorState:
        """Validate tailored resume quality"""
        # Check ATS compatibility
        from src.ats_analyzer import ATSAnalyzer
        ats = ATSAnalyzer()
        report = ats.generate_ats_report(state["tailored_resume"], "")
        
        state["ats_score"] = report["overall_score"]
        return state
    
    def _should_continue(self, state: ResumeTailorState) -> Literal["continue", "finish"]:
        """Decide whether to continue improving or finish"""
        if state["iterations"] >= state.get("max_iterations", 3):
            return "finish"
        
        if state["ats_score"] >= 80 and state["keyword_score"] >= 70:
            return "finish"
        
        return "continue"
    
    def tailor_resume(self, resume: str, job_desc: str, max_iterations: int = 3) -> dict:
        """Run the tailoring workflow"""
        initial_state = {
            "original_resume": resume,
            "job_description": job_desc,
            "tailored_resume": resume,
            "ats_score": 0.0,
            "keyword_score": 0.0,
            "iterations": 0,
            "max_iterations": max_iterations,
            "improvements": []
        }
        
        final_state = self.workflow.invoke(initial_state)
        return final_state
```

**New dependencies**:
```toml
"langgraph>=0.0.20",  # State machine workflows
```

---

### **Phase 4: Industry Analysis**

**LangChain Integration**: Industry classification with structured outputs

**Create**: `src/langchain_industry.py`
```python
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

class IndustryClassification(BaseModel):
    """Structured industry classification"""
    primary_industry: str = Field(description="Primary industry sector")
    sub_industry: str = Field(description="Sub-industry or specialization")
    confidence: float = Field(description="Classification confidence 0-1")
    role_type: str = Field(description="Role category: technical, management, sales, etc.")
    seniority_level: str = Field(description="Seniority: entry, mid, senior, executive")

class LangChainIndustryAnalyzer:
    def __init__(self, llm):
        self.llm = llm
        self.parser = PydanticOutputParser(pydantic_object=IndustryClassification)
    
    def classify_job(self, job_desc: str) -> IndustryClassification:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert at classifying jobs by industry, role type, and seniority."),
            ("user", "{format_instructions}\n\nJob Description:\n{job_desc}")
        ])
        
        chain = prompt | self.llm | self.parser
        
        return chain.invoke({
            "job_desc": job_desc,
            "format_instructions": self.parser.get_format_instructions()
        })
```

**RAG Integration**: Industry benchmarks retrieval
```python
# src/industry_rag.py
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA

class IndustryBenchmarkRAG:
    def __init__(self, llm, persist_directory: str = "./data/industry_vectorstore"):
        self.llm = llm
        self.embeddings = OpenAIEmbeddings()
        self.vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings
        )
        
        # Load industry benchmark documents
        self._load_benchmarks()
    
    def _load_benchmarks(self):
        """Load industry benchmark data into vector store"""
        from pathlib import Path
        import json
        
        industry_dir = Path("data/industries")
        for industry_file in industry_dir.glob("*.json"):
            with open(industry_file) as f:
                data = json.load(f)
                doc = Document(
                    page_content=json.dumps(data),
                    metadata={"industry": data["name"]}
                )
                self.vectorstore.add_documents([doc])
    
    def query_benchmarks(self, query: str) -> str:
        """Query industry benchmarks using RAG"""
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=self.vectorstore.as_retriever(),
            return_source_documents=True
        )
        
        result = qa_chain({"query": query})
        return result["result"]
```

---

### **Phase 5: Interview Preparation**

**LangChain Integration**: Memory for interview conversations

**Create**: `src/langchain_interview.py`
```python
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts import ChatPromptTemplate

class LangChainInterviewPractice:
    def __init__(self, llm):
        self.llm = llm
        self.memory = ConversationBufferMemory()
        self.chain = self._build_chain()
    
    def _build_chain(self) -> ConversationChain:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an experienced interviewer conducting a practice interview.
            Ask relevant questions, provide constructive feedback, and maintain a professional tone.
            Remember the context of previous answers when asking follow-up questions."""),
            ("user", "{input}")
        ])
        
        return ConversationChain(
            llm=self.llm,
            memory=self.memory,
            prompt=prompt
        )
    
    def ask_question(self, user_input: str = None) -> str:
        """Ask a question or respond to user's answer"""
        if user_input:
            response = self.chain.run(user_input)
        else:
            response = self.chain.run("Start the interview with a question.")
        
        return response
    
    def get_conversation_history(self) -> List[dict]:
        """Get full conversation history"""
        return self.memory.chat_memory.messages
```

**LangGraph Integration**: Multi-stage interview workflow

**Create**: `src/langgraph_interview.py`
```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, List

class InterviewState(TypedDict):
    """State for interview workflow"""
    job_description: str
    stage: str  # behavioral, technical, company
    questions_asked: List[dict]
    answers: List[dict]
    current_question: str
    feedback: List[str]
    overall_score: float

class LangGraphMockInterview:
    def __init__(self, llm):
        self.llm = llm
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        workflow = StateGraph(InterviewState)
        
        # Add nodes for each interview stage
        workflow.add_node("behavioral", self._behavioral_stage)
        workflow.add_node("technical", self._technical_stage)
        workflow.add_node("company", self._company_stage)
        workflow.add_node("evaluate", self._evaluate_stage)
        
        # Set entry point
        workflow.set_entry_point("behavioral")
        
        # Add edges
        workflow.add_edge("behavioral", "technical")
        workflow.add_edge("technical", "company")
        workflow.add_edge("company", "evaluate")
        workflow.add_edge("evaluate", END)
        
        return workflow.compile()
    
    def _behavioral_stage(self, state: InterviewState) -> InterviewState:
        """Conduct behavioral interview questions"""
        # Generate and ask behavioral questions
        state["stage"] = "behavioral"
        # ... implementation
        return state
    
    def _technical_stage(self, state: InterviewState) -> InterviewState:
        """Conduct technical interview questions"""
        state["stage"] = "technical"
        # ... implementation
        return state
    
    def _company_stage(self, state: InterviewState) -> InterviewState:
        """Ask company-specific questions"""
        state["stage"] = "company"
        # ... implementation
        return state
    
    def _evaluate_stage(self, state: InterviewState) -> InterviewState:
        """Evaluate overall interview performance"""
        # Provide comprehensive feedback
        state["stage"] = "complete"
        # ... implementation
        return state
```

---

### **Phase 6: Web Interface**

**LangChain Integration**: Streaming responses for real-time updates

**Create**: `src/langchain_streaming.py`
```python
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.callbacks.base import BaseCallbackHandler
from typing import Any

class WebSocketCallbackHandler(BaseCallbackHandler):
    """Custom callback for streaming to WebSocket"""
    
    def __init__(self, websocket_manager, session_id: str):
        self.websocket_manager = websocket_manager
        self.session_id = session_id
    
    async def on_llm_start(self, serialized: dict, prompts: List[str], **kwargs: Any):
        """Called when LLM starts"""
        await self.websocket_manager.send_update(
            self.session_id,
            {"type": "llm_start", "status": "Analyzing..."}
        )
    
    async def on_llm_new_token(self, token: str, **kwargs: Any):
        """Called when LLM generates a new token"""
        await self.websocket_manager.send_update(
            self.session_id,
            {"type": "token", "token": token}
        )
    
    async def on_llm_end(self, response, **kwargs: Any):
        """Called when LLM finishes"""
        await self.websocket_manager.send_update(
            self.session_id,
            {"type": "llm_end", "status": "Analysis complete"}
        )

# Usage in web_api.py
async def analyze_with_streaming(session_id: str, job_file, resume_file):
    callback = WebSocketCallbackHandler(websocket_manager, session_id)
    
    # Create chain with streaming
    chain = prompt | llm
    
    result = await chain.ainvoke(
        {"job_desc": job_desc, "resume": resume},
        config={"callbacks": [callback]}
    )
```

---

## Migration Strategy

### **Step 1: Add Dependencies (Week 1)**
```toml
# pyproject.toml
dependencies = [
    # ... existing dependencies ...
    "langchain>=0.1.0",
    "langchain-anthropic>=0.1.0",
    "langchain-community>=0.0.20",
    "langgraph>=0.0.20",
    "langchain-chroma>=0.1.0",
    "chromadb>=0.4.0",
]
```

### **Step 2: Create LLM Wrapper (Week 1)**
```python
# src/llm_wrapper.py
from langchain_anthropic import ChatAnthropic
from langchain_community.llms import Ollama

def create_langchain_llm(provider: str, model: str, **kwargs):
    """Create LangChain LLM from provider"""
    if provider == "claude":
        return ChatAnthropic(model=model, **kwargs)
    elif provider == "ollama":
        return Ollama(model=model, **kwargs)
    else:
        raise ValueError(f"Unknown provider: {provider}")
```

### **Step 3: Migrate Existing Code (Weeks 2-3)**
- Replace direct LLM calls with LangChain chains
- Add structured output parsing
- Implement prompt templates
- Add caching and error handling

### **Step 4: Add Advanced Features (Weeks 4-6)**
- Implement RAG for knowledge retrieval
- Add LangGraph workflows for complex processes
- Implement streaming for web interface
- Add observability and monitoring

## Testing Strategy

### **Unit Tests**
```python
# tests/test_langchain_integration.py
from langchain.llms.fake import FakeListLLM

def test_entity_extraction():
    fake_llm = FakeListLLM(responses=[
        '{"company": "Test Corp", "job_title": "Engineer", ...}'
    ])
    
    extractor = LangChainEntityExtractor(fake_llm)
    result = extractor.extract_from_job_description("test job desc")
    
    assert result.company == "Test Corp"
    assert result.job_title == "Engineer"
```

### **Integration Tests**
```python
def test_resume_optimization_workflow():
    # Test full LangGraph workflow
    tailor = LangGraphResumeTailor(llm)
    result = tailor.tailor_resume(resume, job_desc, max_iterations=2)
    
    assert result["ats_score"] > 70
    assert result["iterations"] <= 2
```

## Observability

### **LangSmith Integration**
```python
# config.py
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "true")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY", "")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "job-application-agent")

# Automatic tracing of all LangChain calls
```

### **Custom Callbacks**
```python
# src/langchain_callbacks.py
from langchain.callbacks.base import BaseCallbackHandler

class MetricsCallbackHandler(BaseCallbackHandler):
    """Track LLM usage metrics"""
    
    def __init__(self):
        self.total_tokens = 0
        self.total_cost = 0.0
    
    def on_llm_end(self, response, **kwargs):
        # Track token usage and cost
        self.total_tokens += response.llm_output.get("token_usage", {}).get("total_tokens", 0)
        # Calculate cost based on model
```

## Performance Considerations

### **Caching**
- Enable LangChain SQLite cache for repeated queries
- Cache embeddings for RAG
- Cache structured outputs

### **Batching**
- Batch multiple LLM calls when possible
- Use async operations for parallel processing

### **Cost Optimization**
- Use cheaper models for simple tasks
- Implement token counting and budgets
- Cache aggressively

## Success Criteria

- ✅ All LLM calls use LangChain/LangGraph
- ✅ Structured outputs are reliable (>95% success rate)
- ✅ Caching reduces API calls by >50%
- ✅ Error handling prevents failures
- ✅ Observability provides insights into LLM usage
- ✅ Performance is acceptable (< 5s for most operations)
- ✅ Tests cover all LangChain integrations

## Documentation Updates

Each phase plan should be updated with:
- LangChain/LangGraph code examples
- Migration notes from existing code
- Testing strategies for new components
- Configuration options for LangChain features

## Next Steps

1. Review this integration plan
2. Update individual phase plans with LangChain/LangGraph details
3. Begin migration starting with Phase 2 (entity extraction)
4. Progressively enhance each phase with advanced features
5. Monitor performance and adjust as needed
