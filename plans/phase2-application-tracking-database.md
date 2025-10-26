# Application Tracking Database (SQLite)

## Overview

Implement local SQLite database for application tracking, analytics, and insights. This provides a foundation for tracking job applications, analyzing success patterns, and generating career insights without requiring external database setup.

## Prerequisites

- Structured output parsing implemented
- SQLite3 (included with Python)
- Existing analysis workflow functional

## Implementation Steps

### 1. Create Database Schema (`src/database_schema.py`)

**New file**: `src/database_schema.py`

Define SQLite database schema:

```python
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
from typing import Optional

Base = declarative_base()

class Person(Base):
    """User profile information"""
    __tablename__ = 'persons'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    applications = relationship("Application", back_populates="person")
    skills = relationship("PersonSkill", back_populates="person")

class Company(Base):
    """Company information"""
    __tablename__ = 'companies'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    industry = Column(String(100))
    size = Column(String(50))  # startup, small, medium, large, enterprise
    location = Column(String(255))
    website = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    applications = relationship("Application", back_populates="company")
    jobs = relationship("Job", back_populates="company")

class Job(Base):
    """Job posting information"""
    __tablename__ = 'jobs'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    requirements = Column(Text)  # JSON string of requirements
    seniority_level = Column(String(50))  # entry, mid, senior, executive
    department = Column(String(100))
    salary_range = Column(String(100))
    location = Column(String(255))
    remote_option = Column(Boolean, default=False)
    company_id = Column(Integer, ForeignKey('companies.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="jobs")
    applications = relationship("Application", back_populates="job")
    job_skills = relationship("JobSkill", back_populates="job")

class Application(Base):
    """Job application tracking"""
    __tablename__ = 'applications'
    
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('persons.id'), nullable=False)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=True)
    
    # Application details
    applied_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default='Applied')  # Applied, Interview, Rejected, Offer, Accepted
    fit_score = Column(Float)  # 1-10 rating from analysis
    resume_version = Column(String(100))  # Resume version used
    cover_letter_path = Column(String(500))  # Path to cover letter file
    
    # Tracking fields
    response_date = Column(DateTime)
    interview_date = Column(DateTime)
    rejection_reason = Column(Text)
    notes = Column(Text)
    
    # Analysis results (JSON)
    assessment_data = Column(Text)  # JSON of assessment results
    optimization_data = Column(Text)  # JSON of optimization results
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    person = relationship("Person", back_populates="applications")
    company = relationship("Company", back_populates="applications")
    job = relationship("Job", back_populates="applications")

class Skill(Base):
    """Skills database"""
    __tablename__ = 'skills'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    category = Column(String(50))  # Technical, Soft, Domain-specific
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class PersonSkill(Base):
    """Person-Skill relationship with proficiency"""
    __tablename__ = 'person_skills'
    
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('persons.id'), nullable=False)
    skill_id = Column(Integer, ForeignKey('skills.id'), nullable=False)
    proficiency_level = Column(String(20))  # Beginner, Intermediate, Advanced, Expert
    years_experience = Column(Float)
    last_used = Column(DateTime)
    
    # Relationships
    person = relationship("Person", back_populates="skills")
    skill = relationship("Skill")

class JobSkill(Base):
    """Job-Skill relationship with importance"""
    __tablename__ = 'job_skills'
    
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False)
    skill_id = Column(Integer, ForeignKey('skills.id'), nullable=False)
    importance_level = Column(Integer)  # 1-5 scale
    is_required = Column(Boolean, default=True)
    
    # Relationships
    job = relationship("Job", back_populates="job_skills")
    skill = relationship("Skill")

class ResumeVersion(Base):
    """Resume version tracking"""
    __tablename__ = 'resume_versions'
    
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('persons.id'), nullable=False)
    version_name = Column(String(100), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_hash = Column(String(64))  # SHA-256 hash
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    person = relationship("Person")
```

### 2. Create Database Manager (`src/database_manager.py`)

**New file**: `src/database_manager.py`

Implement database operations:

```python
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import json
import os
from pathlib import Path

from .database_schema import Base, Person, Company, Job, Application, Skill, PersonSkill, JobSkill, ResumeVersion
from config import Config

class DatabaseManager:
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(Config.DATA_DIR, "applications.db")
        
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    def close(self):
        """Close database connection"""
        self.engine.dispose()
    
    # Person operations
    def create_or_get_person(self, name: str, email: str) -> Person:
        """Create or get existing person"""
        with self.get_session() as session:
            person = session.query(Person).filter(Person.email == email).first()
            if not person:
                person = Person(name=name, email=email)
                session.add(person)
                session.commit()
                session.refresh(person)
            return person
    
    # Company operations
    def create_or_get_company(self, name: str, industry: str = None, 
                             size: str = None, location: str = None) -> Company:
        """Create or get existing company"""
        with self.get_session() as session:
            company = session.query(Company).filter(Company.name == name).first()
            if not company:
                company = Company(
                    name=name,
                    industry=industry,
                    size=size,
                    location=location
                )
                session.add(company)
                session.commit()
                session.refresh(company)
            return company
    
    # Job operations
    def create_job(self, title: str, description: str, company_id: int,
                   requirements: List[str] = None, seniority_level: str = None,
                   salary_range: str = None, location: str = None) -> Job:
        """Create new job posting"""
        with self.get_session() as session:
            job = Job(
                title=title,
                description=description,
                company_id=company_id,
                requirements=json.dumps(requirements) if requirements else None,
                seniority_level=seniority_level,
                salary_range=salary_range,
                location=location
            )
            session.add(job)
            session.commit()
            session.refresh(job)
            return job
    
    # Application operations
    def create_application(self, person_id: int, company_id: int, job_id: int = None,
                           fit_score: float = None, resume_version: str = None,
                           assessment_data: Dict = None, optimization_data: Dict = None) -> Application:
        """Create new application record"""
        with self.get_session() as session:
            application = Application(
                person_id=person_id,
                company_id=company_id,
                job_id=job_id,
                fit_score=fit_score,
                resume_version=resume_version,
                assessment_data=json.dumps(assessment_data) if assessment_data else None,
                optimization_data=json.dumps(optimization_data) if optimization_data else None
            )
            session.add(application)
            session.commit()
            session.refresh(application)
            return application
    
    def update_application_status(self, app_id: int, status: str, 
                                 response_date: datetime = None, 
                                 interview_date: datetime = None,
                                 notes: str = None):
        """Update application status"""
        with self.get_session() as session:
            application = session.query(Application).filter(Application.id == app_id).first()
            if application:
                application.status = status
                application.updated_at = datetime.utcnow()
                if response_date:
                    application.response_date = response_date
                if interview_date:
                    application.interview_date = interview_date
                if notes:
                    application.notes = notes
                session.commit()
    
    def get_applications_by_person(self, person_id: int) -> List[Application]:
        """Get all applications for a person"""
        with self.get_session() as session:
            return session.query(Application).filter(Application.person_id == person_id).all()
    
    def get_applications_by_status(self, person_id: int, status: str) -> List[Application]:
        """Get applications by status"""
        with self.get_session() as session:
            return session.query(Application).filter(
                Application.person_id == person_id,
                Application.status == status
            ).all()
    
    # Analytics operations
    def get_application_stats(self, person_id: int) -> Dict[str, Any]:
        """Get comprehensive application statistics"""
        with self.get_session() as session:
            total_apps = session.query(Application).filter(Application.person_id == person_id).count()
            
            # Status breakdown
            status_counts = session.query(
                Application.status,
                func.count(Application.id)
            ).filter(Application.person_id == person_id).group_by(Application.status).all()
            
            # Industry breakdown
            industry_counts = session.query(
                Company.industry,
                func.count(Application.id)
            ).join(Application).filter(Application.person_id == person_id).group_by(Company.industry).all()
            
            # Success rate
            successful_apps = session.query(Application).filter(
                Application.person_id == person_id,
                Application.status.in_(['Interview', 'Offer', 'Accepted'])
            ).count()
            
            success_rate = (successful_apps / total_apps * 100) if total_apps > 0 else 0
            
            # Average response time
            avg_response_time = session.query(
                func.avg(func.julianday(Application.response_date) - func.julianday(Application.applied_date))
            ).filter(
                Application.person_id == person_id,
                Application.response_date.isnot(None)
            ).scalar()
            
            return {
                'total_applications': total_apps,
                'status_breakdown': dict(status_counts),
                'industry_breakdown': dict(industry_counts),
                'success_rate': round(success_rate, 2),
                'average_response_days': round(avg_response_time, 1) if avg_response_time else None
            }
    
    def get_company_insights(self, person_id: int) -> Dict[str, Any]:
        """Get insights about companies applied to"""
        with self.get_session() as session:
            # Most responsive companies
            responsive_companies = session.query(
                Company.name,
                func.count(Application.id).label('total_apps'),
                func.sum(func.case([(Application.status.in_(['Interview', 'Offer', 'Accepted']), 1)], else_=0)).label('successful_apps')
            ).join(Application).filter(Application.person_id == person_id).group_by(Company.id).all()
            
            # Best performing industries
            industry_performance = session.query(
                Company.industry,
                func.count(Application.id).label('total_apps'),
                func.sum(func.case([(Application.status.in_(['Interview', 'Offer', 'Accepted']), 1)], else_=0)).label('successful_apps')
            ).join(Application).filter(Application.person_id == person_id).group_by(Company.industry).all()
            
            return {
                'responsive_companies': [
                    {
                        'name': comp.name,
                        'total_apps': comp.total_apps,
                        'success_rate': round((comp.successful_apps / comp.total_apps * 100), 2)
                    }
                    for comp in responsive_companies
                ],
                'industry_performance': [
                    {
                        'industry': ind.industry,
                        'total_apps': ind.total_apps,
                        'success_rate': round((ind.successful_apps / ind.total_apps * 100), 2)
                    }
                    for ind in industry_performance
                ]
            }
    
    # Resume version operations
    def save_resume_version(self, person_id: int, version_name: str, 
                           file_path: str, file_hash: str) -> ResumeVersion:
        """Save resume version"""
        with self.get_session() as session:
            # Deactivate other versions
            session.query(ResumeVersion).filter(
                ResumeVersion.person_id == person_id
            ).update({'is_active': False})
            
            # Create new version
            version = ResumeVersion(
                person_id=person_id,
                version_name=version_name,
                file_path=file_path,
                file_hash=file_hash
            )
            session.add(version)
            session.commit()
            session.refresh(version)
            return version
    
    def get_active_resume_version(self, person_id: int) -> Optional[ResumeVersion]:
        """Get active resume version"""
        with self.get_session() as session:
            return session.query(ResumeVersion).filter(
                ResumeVersion.person_id == person_id,
                ResumeVersion.is_active == True
            ).first()
```

### 3. Create Application Tracker (`src/application_tracker.py`)

**New file**: `src/application_tracker.py`

Implement application tracking integration:

```python
from typing import Dict, Any, Optional, List
from datetime import datetime
import hashlib
from pathlib import Path

from .database_manager import DatabaseManager
from .models import JobAssessment, ResumeImprovements
from config import Config

class ApplicationTracker:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def track_application(self, job_description: str, resume_text: str, 
                         analysis_results: Dict[str, Any], 
                         person_name: str, person_email: str) -> int:
        """Track a new application"""
        
        # Extract entities from job description
        entities = self._extract_job_entities(job_description)
        
        # Create or get person
        person = self.db.create_or_get_person(person_name, person_email)
        
        # Create or get company
        company = self.db.create_or_get_company(
            name=entities.get('company', 'Unknown'),
            industry=entities.get('industry'),
            location=entities.get('location')
        )
        
        # Create job posting
        job = self.db.create_job(
            title=entities.get('job_title', 'Unknown'),
            description=job_description,
            company_id=company.id,
            seniority_level=entities.get('seniority'),
            salary_range=entities.get('salary_range'),
            location=entities.get('location')
        )
        
        # Create application record
        assessment = analysis_results.get('assessment')
        materials = analysis_results.get('materials')
        
        application = self.db.create_application(
            person_id=person.id,
            company_id=company.id,
            job_id=job.id,
            fit_score=assessment.rating if assessment else None,
            resume_version=self._get_resume_version_hash(resume_text),
            assessment_data=self._serialize_assessment(assessment),
            optimization_data=self._serialize_materials(materials)
        )
        
        return application.id
    
    def update_application_status(self, app_id: int, status: str, 
                                 notes: str = None, interview_date: datetime = None):
        """Update application status"""
        response_date = datetime.utcnow() if status in ['Interview', 'Rejected', 'Offer'] else None
        self.db.update_application_status(app_id, status, response_date, interview_date, notes)
    
    def get_application_history(self, person_email: str) -> List[Dict[str, Any]]:
        """Get application history for person"""
        person = self.db.get_person_by_email(person_email)
        if not person:
            return []
        
        applications = self.db.get_applications_by_person(person.id)
        
        return [
            {
                'id': app.id,
                'company': app.company.name,
                'job_title': app.job.title if app.job else 'Unknown',
                'applied_date': app.applied_date,
                'status': app.status,
                'fit_score': app.fit_score,
                'response_date': app.response_date,
                'interview_date': app.interview_date,
                'notes': app.notes
            }
            for app in applications
        ]
    
    def get_analytics_dashboard(self, person_email: str) -> Dict[str, Any]:
        """Get comprehensive analytics dashboard"""
        person = self.db.get_person_by_email(person_email)
        if not person:
            return {}
        
        stats = self.db.get_application_stats(person.id)
        insights = self.db.get_company_insights(person.id)
        
        return {
            'overview': stats,
            'company_insights': insights,
            'recommendations': self._generate_recommendations(stats, insights)
        }
    
    def _extract_job_entities(self, job_description: str) -> Dict[str, str]:
        """Extract entities from job description using simple patterns"""
        import re
        
        entities = {}
        
        # Extract company name (usually in first few lines)
        company_match = re.search(r'(?:at|@|Company:?)\s+([A-Z][a-zA-Z\s&]+)', job_description[:500])
        if company_match:
            entities['company'] = company_match.group(1).strip()
        
        # Extract job title (usually in first line)
        title_match = re.search(r'^([A-Z][a-zA-Z\s]+(?:Engineer|Manager|Developer|Analyst|Specialist))', job_description)
        if title_match:
            entities['job_title'] = title_match.group(1).strip()
        
        # Extract location
        location_match = re.search(r'(?:Location:?|Based in|Remote|Hybrid)\s+([A-Z][a-zA-Z\s,]+)', job_description)
        if location_match:
            entities['location'] = location_match.group(1).strip()
        
        # Extract salary range
        salary_match = re.search(r'\$[\d,]+(?:k|K)?(?:\s*-\s*\$?[\d,]+(?:k|K)?)?', job_description)
        if salary_match:
            entities['salary_range'] = salary_match.group(0)
        
        return entities
    
    def _get_resume_version_hash(self, resume_text: str) -> str:
        """Generate hash for resume version"""
        return hashlib.sha256(resume_text.encode()).hexdigest()[:16]
    
    def _serialize_assessment(self, assessment) -> Dict[str, Any]:
        """Serialize assessment data for storage"""
        if not assessment:
            return {}
        
        return {
            'rating': assessment.rating,
            'strengths': assessment.strengths,
            'gaps': assessment.gaps,
            'missing_requirements': assessment.missing_requirements,
            'recommendation': assessment.recommendation,
            'confidence': assessment.confidence
        }
    
    def _serialize_materials(self, materials) -> Dict[str, Any]:
        """Serialize materials data for storage"""
        if not materials:
            return {}
        
        return {
            'resume_improvements': materials.resume_improvements,
            'cover_letter': materials.cover_letter,
            'questions_for_employer': materials.questions_for_employer,
            'anticipated_questions': materials.anticipated_questions,
            'suggested_answers': materials.suggested_answers,
            'next_steps': materials.next_steps
        }
    
    def _generate_recommendations(self, stats: Dict, insights: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if stats['success_rate'] < 20:
            recommendations.append("Consider improving resume keywords and tailoring for each application")
        
        if stats['average_response_days'] and stats['average_response_days'] > 14:
            recommendations.append("Follow up on applications after 1-2 weeks")
        
        if insights['industry_performance']:
            best_industry = max(insights['industry_performance'], key=lambda x: x['success_rate'])
            recommendations.append(f"Focus on {best_industry['industry']} industry - highest success rate")
        
        return recommendations
```

### 4. Update Analyzer Integration (`src/analyzer.py`)

**Modify existing**: `src/analyzer.py`

Add application tracking to analysis workflow:

```python
# Add to analyze_application method after results are generated
def analyze_application(self, job_description: str, resume: str) -> Dict[str, Any]:
    """Perform comprehensive analysis with optional tracking"""
    console.print("[bold blue]Starting job application analysis...[/bold blue]")
    
    # ... existing analysis code ...
    
    # NEW: Track application if enabled
    if Config.APPLICATION_TRACKING_ENABLED:
        try:
            from .application_tracker import ApplicationTracker
            from .database_manager import DatabaseManager
            
            db_manager = DatabaseManager()
            tracker = ApplicationTracker(db_manager)
            
            app_id = tracker.track_application(
                job_description=job_description,
                resume_text=resume,
                analysis_results=results,
                person_name=Config.USER_NAME or "User",
                person_email=Config.USER_EMAIL or "user@example.com"
            )
            
            console.print(f"[green]Application tracked with ID: {app_id}[/green]")
            results['application_id'] = app_id
            
        except Exception as e:
            console.print(f"[yellow]Warning: Could not track application: {e}[/yellow]")
    
    return results
```

### 5. Add Tracking Commands (`main.py`)

**Modify existing**: `main.py`

Add new CLI commands for application tracking:

```python
# Add new arguments
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
    "--export-applications",
    metavar="OUTPUT",
    help="Export applications to CSV file"
)

# Add command handlers
if args.list_applications:
    from src.application_tracker import ApplicationTracker
    from src.database_manager import DatabaseManager
    
    db_manager = DatabaseManager()
    tracker = ApplicationTracker(db_manager)
    
    applications = tracker.get_application_history(Config.USER_EMAIL or "user@example.com")
    
    if applications:
        # Display applications in table format
        from rich.table import Table
        table = Table(title="Application History")
        table.add_column("ID", style="cyan")
        table.add_column("Company", style="green")
        table.add_column("Position", style="blue")
        table.add_column("Applied", style="yellow")
        table.add_column("Status", style="magenta")
        table.add_column("Score", style="red")
        
        for app in applications:
            table.add_row(
                str(app['id']),
                app['company'],
                app['job_title'],
                app['applied_date'].strftime('%Y-%m-%d'),
                app['status'],
                str(app['fit_score']) if app['fit_score'] else 'N/A'
            )
        
        console.print(table)
    else:
        console.print("[yellow]No applications found[/yellow]")
    
    db_manager.close()
    sys.exit(0)

if args.update_status:
    app_id, status = args.update_status
    from src.application_tracker import ApplicationTracker
    from src.database_manager import DatabaseManager
    
    db_manager = DatabaseManager()
    tracker = ApplicationTracker(db_manager)
    
    tracker.update_application_status(int(app_id), status)
    console.print(f"[green]Updated application {app_id} status to {status}[/green]")
    
    db_manager.close()
    sys.exit(0)

if args.application_stats:
    from src.application_tracker import ApplicationTracker
    from src.database_manager import DatabaseManager
    
    db_manager = DatabaseManager()
    tracker = ApplicationTracker(db_manager)
    
    dashboard = tracker.get_analytics_dashboard(Config.USER_EMAIL or "user@example.com")
    
    if dashboard:
        # Display analytics dashboard
        from rich.panel import Panel
        from rich.table import Table
        
        # Overview stats
        overview = dashboard['overview']
        stats_text = f"""
Total Applications: {overview['total_applications']}
Success Rate: {overview['success_rate']}%
Average Response Time: {overview['average_response_days']} days

Status Breakdown:
{chr(10).join([f"  {status}: {count}" for status, count in overview['status_breakdown'].items()])}

Industry Breakdown:
{chr(10).join([f"  {industry}: {count}" for industry, count in overview['industry_breakdown'].items()])}
        """
        
        console.print(Panel(stats_text, title="Application Statistics", border_style="green"))
        
        # Recommendations
        if dashboard['recommendations']:
            rec_text = "\n".join([f"• {rec}" for rec in dashboard['recommendations']])
            console.print(Panel(rec_text, title="Recommendations", border_style="blue"))
    
    db_manager.close()
    sys.exit(0)

if args.export_applications:
    from src.application_tracker import ApplicationTracker
    from src.database_manager import DatabaseManager
    import csv
    
    db_manager = DatabaseManager()
    tracker = ApplicationTracker(db_manager)
    
    applications = tracker.get_application_history(Config.USER_EMAIL or "user@example.com")
    
    with open(args.export_applications, 'w', newline='') as csvfile:
        fieldnames = ['id', 'company', 'job_title', 'applied_date', 'status', 'fit_score', 'response_date', 'interview_date', 'notes']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for app in applications:
            writer.writerow({
                'id': app['id'],
                'company': app['company'],
                'job_title': app['job_title'],
                'applied_date': app['applied_date'].strftime('%Y-%m-%d'),
                'status': app['status'],
                'fit_score': app['fit_score'],
                'response_date': app['response_date'].strftime('%Y-%m-%d') if app['response_date'] else '',
                'interview_date': app['interview_date'].strftime('%Y-%m-%d') if app['interview_date'] else '',
                'notes': app['notes'] or ''
            })
    
    console.print(f"[green]Applications exported to: {args.export_applications}[/green]")
    db_manager.close()
    sys.exit(0)
```

### 6. Update Configuration (`config.py`)

**Modify existing**: `config.py`

Add application tracking configuration:

```python
# Application tracking settings
APPLICATION_TRACKING_ENABLED = os.getenv("APPLICATION_TRACKING_ENABLED", "true").lower() == "true"
DATA_DIR = os.getenv("DATA_DIR", os.path.join(os.path.expanduser("~"), ".job-agent", "data"))
DATABASE_PATH = os.getenv("DATABASE_PATH", os.path.join(DATA_DIR, "applications.db"))

# User profile settings
USER_NAME = os.getenv("USER_NAME", "")
USER_EMAIL = os.getenv("USER_EMAIL", "")

# Analytics settings
ANALYTICS_RETENTION_DAYS = int(os.getenv("ANALYTICS_RETENTION_DAYS", "365"))
```

### 7. Update Dependencies (`pyproject.toml`)

**Modify existing**: `pyproject.toml`

Add to dependencies:
```toml
"sqlalchemy>=2.0.0",  # Database ORM
```

### 8. Update Documentation (`README.md`)

**Modify existing**: `README.md`

Add new sections:

**Application Tracking** (new major section):
- Explain SQLite database for local tracking
- Document `--track-application` flag
- Document `--list-applications` command
- Document `--update-status` command
- Document `--application-stats` command
- Document `--export-applications` command

**Database Schema** (new section):
- Explain what data is stored
- Show database structure
- Explain data retention policies

**Environment Variables** (update existing):
```
APPLICATION_TRACKING_ENABLED=true
DATA_DIR=/path/to/data
DATABASE_PATH=/path/to/applications.db
USER_NAME=Your Name
USER_EMAIL=your.email@example.com
ANALYTICS_RETENTION_DAYS=365
```

## Testing Strategy

1. Test database creation and schema setup
2. Test application tracking workflow
3. Test status updates and analytics
4. Test export functionality
5. Test error handling and data validation
6. Test with multiple applications
7. Test database migration and backup

## Integration Points

**With Phase 1 (Structured Output)**:
- Uses structured data models for storage
- Leverages improved parsing reliability

**With existing analyzer**:
- Seamless integration with analysis workflow
- Optional tracking (controlled by config)
- Preserves existing functionality

## Security Considerations

- Local SQLite database (no external dependencies)
- Encrypted storage of sensitive data
- Data retention policies
- Secure file handling for exports

## Performance Considerations

- Efficient database queries with indexes
- Batch operations for multiple applications
- Database connection pooling
- Regular database maintenance

## Files to Create/Modify

**New Files**:
- `src/database_schema.py` (SQLAlchemy models)
- `src/database_manager.py` (Database operations)
- `src/application_tracker.py` (Application tracking logic)

**Modified Files**:
- `src/analyzer.py` (Add tracking integration)
- `config.py` (Add tracking configuration)
- `main.py` (Add tracking commands)
- `pyproject.toml` (Add SQLAlchemy dependency)
- `README.md` (Add tracking documentation)

## Success Criteria

- SQLite database successfully stores applications
- Application tracking commands work correctly
- Analytics provide actionable insights
- Export functionality works for CSV
- Performance is acceptable (< 1s for most operations)
- Data integrity maintained
- Clear documentation and examples

## Future Enhancements

- Advanced analytics and reporting
- Integration with job boards
- Automated follow-up reminders
- Resume version comparison
- Skill gap analysis
- Career path recommendations

## To-dos

- [ ] Create src/database_schema.py with SQLAlchemy models for all entities
- [ ] Create src/database_manager.py with database operations and analytics
- [ ] Create src/application_tracker.py for application tracking integration
- [ ] Update src/analyzer.py to integrate with application tracking
- [ ] Add application tracking CLI commands to main.py
- [ ] Add tracking configuration options to config.py
- [ ] Add SQLAlchemy dependency to pyproject.toml
- [ ] Update README.md with application tracking documentation

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
