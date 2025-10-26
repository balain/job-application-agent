"""Database schema for application tracking."""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Float,
    Boolean,
    ForeignKey,
    Enum,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum

Base = declarative_base()


class ApplicationStatus(PyEnum):
    """Application status enumeration."""

    DRAFT = "draft"
    APPLIED = "applied"
    UNDER_REVIEW = "under_review"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEW_COMPLETED = "interview_completed"
    OFFER_RECEIVED = "offer_received"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    ACCEPTED = "accepted"


class Person(Base):
    """User profile information."""

    __tablename__ = "persons"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    applications = relationship("Application", back_populates="person")
    skills = relationship("PersonSkill", back_populates="person")


class Company(Base):
    """Company information."""

    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    industry = Column(String(100))
    size = Column(String(50))  # e.g., "1-10", "11-50", "51-200", "201-1000", "1000+"
    website = Column(String(255))
    location = Column(String(255))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    applications = relationship("Application", back_populates="company")
    job_postings = relationship("JobPosting", back_populates="company")


class JobPosting(Base):
    """Job posting information."""

    __tablename__ = "job_postings"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    requirements = Column(Text)
    salary_min = Column(Float)
    salary_max = Column(Float)
    salary_currency = Column(String(3), default="USD")
    location = Column(String(255))
    remote_allowed = Column(Boolean, default=False)
    employment_type = Column(String(50))  # e.g., "full-time", "part-time", "contract"
    experience_level = Column(String(50))  # e.g., "entry", "mid", "senior"
    url = Column(String(500))
    posted_date = Column(DateTime)
    application_deadline = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign keys
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)

    # Relationships
    company = relationship("Company", back_populates="job_postings")
    applications = relationship("Application", back_populates="job_posting")


class Application(Base):
    """Job application tracking."""

    __tablename__ = "applications"

    id = Column(Integer, primary_key=True)
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.DRAFT)
    applied_date = Column(DateTime)
    notes = Column(Text)
    cover_letter = Column(Text)
    resume_version = Column(String(100))
    expected_salary = Column(Float)
    actual_salary = Column(Float)
    salary_currency = Column(String(3), default="USD")
    response_date = Column(DateTime)
    rejection_reason = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign keys
    person_id = Column(Integer, ForeignKey("persons.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    job_posting_id = Column(Integer, ForeignKey("job_postings.id"), nullable=True)

    # Relationships
    person = relationship("Person", back_populates="applications")
    company = relationship("Company", back_populates="applications")
    job_posting = relationship("JobPosting", back_populates="applications")
    interviews = relationship("Interview", back_populates="application")
    analysis_results = relationship("AnalysisResult", back_populates="application")


class Interview(Base):
    """Interview tracking."""

    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True)
    interview_type = Column(
        String(50)
    )  # e.g., "phone", "video", "in-person", "technical"
    scheduled_date = Column(DateTime)
    duration_minutes = Column(Integer)
    interviewer_name = Column(String(255))
    interviewer_title = Column(String(255))
    interviewer_email = Column(String(255))
    notes = Column(Text)
    questions_asked = Column(Text)
    questions_answered = Column(Text)
    feedback_received = Column(Text)
    outcome = Column(String(50))  # e.g., "passed", "failed", "pending"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign keys
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)

    # Relationships
    application = relationship("Application", back_populates="interviews")


class AnalysisResult(Base):
    """Analysis results from job application agent."""

    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True)
    suitability_rating = Column(Integer)  # 1-10 scale
    recommendation = Column(String(20))  # "Yes", "No", "Unknown"
    confidence_level = Column(String(20))  # "High", "Medium", "Low"
    strengths_analysis = Column(Text)
    gaps_analysis = Column(Text)
    missing_requirements = Column(Text)
    resume_improvements = Column(Text)
    cover_letter_suggestions = Column(Text)
    interview_preparation = Column(Text)
    next_steps = Column(Text)
    analysis_timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign keys
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)

    # Relationships
    application = relationship("Application", back_populates="analysis_results")


class Skill(Base):
    """Skills catalog."""

    __tablename__ = "skills"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    category = Column(String(50))  # e.g., "technical", "soft", "language"
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    person_skills = relationship("PersonSkill", back_populates="skill")


class PersonSkill(Base):
    """Person-skill relationship with proficiency levels."""

    __tablename__ = "person_skills"

    id = Column(Integer, primary_key=True)
    proficiency_level = Column(
        String(20)
    )  # e.g., "beginner", "intermediate", "advanced", "expert"
    years_experience = Column(Float)
    last_used = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign keys
    person_id = Column(Integer, ForeignKey("persons.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)

    # Relationships
    person = relationship("Person", back_populates="skills")
    skill = relationship("Skill", back_populates="person_skills")


class AnalyticsEvent(Base):
    """Analytics events for tracking usage patterns."""

    __tablename__ = "analytics_events"

    id = Column(Integer, primary_key=True)
    event_type = Column(
        String(50), nullable=False
    )  # e.g., "analysis", "application_created", "status_updated"
    event_data = Column(Text)  # JSON string with event details
    user_agent = Column(String(255))
    ip_address = Column(String(45))
    session_id = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Foreign keys (optional)
    person_id = Column(Integer, ForeignKey("persons.id"), nullable=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=True)

    # Relationships
    person = relationship("Person")
    application = relationship("Application")
