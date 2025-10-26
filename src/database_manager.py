"""Database manager for application tracking."""

import json
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from contextlib import contextmanager

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from .database_schema import (
    Base,
    Person,
    Company,
    JobPosting,
    Application,
    Interview,
    AnalysisResult,
    AnalyticsEvent,
    ApplicationStatus,
)

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database operations for application tracking."""

    def __init__(self, database_path: Optional[str] = None):
        """
        Initialize database manager.

        Args:
            database_path: Path to SQLite database file. If None, uses default location.
        """
        if database_path is None:
            # Use default location in user data directory
            from platformdirs import user_data_dir

            data_dir = Path(user_data_dir("job-application-agent"))
            data_dir.mkdir(parents=True, exist_ok=True)
            database_path = data_dir / "applications.db"

        self.database_path = Path(database_path)
        self.engine = create_engine(f"sqlite:///{self.database_path}")
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

        # Create tables if they don't exist
        Base.metadata.create_all(bind=self.engine)

    @contextmanager
    def get_session(self):
        """Get database session with automatic cleanup."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_or_create_person(self, name: str, email: str) -> Person:
        """Get existing person or create new one."""
        with self.get_session() as session:
            person = session.query(Person).filter(Person.email == email).first()
            if not person:
                person = Person(name=name, email=email)
                session.add(person)
                session.flush()  # Get the ID
            # Detach the object from session so it can be used outside
            session.expunge(person)
            return person

    def get_or_create_company(self, name: str, **kwargs) -> Company:
        """Get existing company or create new one."""
        with self.get_session() as session:
            company = session.query(Company).filter(Company.name == name).first()
            if not company:
                company = Company(name=name, **kwargs)
                session.add(company)
                session.flush()  # Get the ID
            # Detach the object from session so it can be used outside
            session.expunge(company)
            return company

    def create_application(
        self,
        person_email: str,
        company_name: str,
        job_title: str,
        status: ApplicationStatus = ApplicationStatus.DRAFT,
        **kwargs,
    ) -> Application:
        """Create a new job application."""
        with self.get_session() as session:
            # Get or create person and company
            person = session.query(Person).filter(Person.email == person_email).first()
            if not person:
                person = Person(
                    name=kwargs.get("person_name", "Unknown"), email=person_email
                )
                session.add(person)
                session.flush()

            company = (
                session.query(Company).filter(Company.name == company_name).first()
            )
            if not company:
                company = Company(name=company_name, **kwargs.get("company_data", {}))
                session.add(company)
                session.flush()

            # Create application
            application = Application(
                person_id=person.id,
                company_id=company.id,
                status=status,
                **{
                    k: v
                    for k, v in kwargs.items()
                    if k not in ["person_name", "company_data"]
                },
            )

            session.add(application)
            session.flush()  # Get the ID

            # Log analytics event
            self._log_analytics_event(
                session=session,
                event_type="application_created",
                person_id=person.id,
                application_id=application.id,
                event_data={
                    "company": company_name,
                    "job_title": job_title,
                    "status": status.value,
                },
            )

            # Detach the object from session so it can be used outside
            session.expunge(application)
            return application

    def update_application_status(
        self,
        application_id: int,
        status: ApplicationStatus,
        notes: Optional[str] = None,
    ) -> bool:
        """Update application status."""
        with self.get_session() as session:
            application = (
                session.query(Application)
                .filter(Application.id == application_id)
                .first()
            )
            if not application:
                return False

            old_status = application.status
            application.status = status
            application.updated_at = datetime.now(timezone.utc)

            if notes:
                application.notes = notes

            # Log analytics event
            self._log_analytics_event(
                session=session,
                event_type="status_updated",
                person_id=application.person_id,
                application_id=application.id,
                event_data={"old_status": old_status.value, "new_status": status.value},
            )

            return True

    def delete_application(self, application_id: int) -> bool:
        """
        Delete an application and all related records.

        Args:
            application_id: ID of the application to delete

        Returns:
            bool: True if deletion was successful, False if application not found
        """
        with self.get_session() as session:
            try:
                # Get the application with all related data
                application = (
                    session.query(Application)
                    .filter(Application.id == application_id)
                    .first()
                )

                if not application:
                    return False

                # Store IDs for analytics logging
                person_id = application.person_id
                company_id = application.company_id
                job_posting_id = application.job_posting_id

                # Log analytics event before deletion
                self._log_analytics_event(
                    session=session,
                    event_type="application_deleted",
                    person_id=person_id,
                    application_id=application_id,
                    event_data={
                        "company_name": application.company.name
                        if application.company
                        else "Unknown",
                        "job_title": application.job_posting.title
                        if application.job_posting
                        else "N/A",
                        "status": application.status.value,
                    },
                )

                # Delete related analysis results
                session.query(AnalysisResult).filter(
                    AnalysisResult.application_id == application_id
                ).delete()

                # Delete related interviews
                session.query(Interview).filter(
                    Interview.application_id == application_id
                ).delete()

                # Delete the application itself
                session.delete(application)

                # Check if we should clean up orphaned records
                # Only delete company if no other applications reference it
                if company_id:
                    remaining_apps = (
                        session.query(Application)
                        .filter(Application.company_id == company_id)
                        .count()
                    )
                    if remaining_apps == 0:
                        company = (
                            session.query(Company)
                            .filter(Company.id == company_id)
                            .first()
                        )
                        if company:
                            session.delete(company)

                # Only delete job posting if no other applications reference it
                if job_posting_id:
                    remaining_apps = (
                        session.query(Application)
                        .filter(Application.job_posting_id == job_posting_id)
                        .count()
                    )
                    if remaining_apps == 0:
                        job_posting = (
                            session.query(JobPosting)
                            .filter(JobPosting.id == job_posting_id)
                            .first()
                        )
                        if job_posting:
                            session.delete(job_posting)

                # Note: We don't delete the Person record as they might have other applications

                return True

            except SQLAlchemyError as e:
                logger.error(f"Error deleting application {application_id}: {e}")
                return False

    def get_applications(
        self,
        person_email: Optional[str] = None,
        status: Optional[ApplicationStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Application]:
        """Get applications with optional filtering."""
        with self.get_session() as session:
            query = session.query(Application)

            if person_email:
                query = query.join(Person).filter(Person.email == person_email)

            if status:
                query = query.filter(Application.status == status)

            applications = (
                query.order_by(desc(Application.created_at))
                .offset(offset)
                .limit(limit)
                .all()
            )

            # Convert to dictionaries to avoid session issues
            result = []
            for app in applications:
                app_dict = {
                    "id": app.id,
                    "status": app.status,
                    "applied_date": app.applied_date,
                    "notes": app.notes,
                    "company_name": app.company.name if app.company else "Unknown",
                    "job_title": app.job_posting.title if app.job_posting else "N/A",
                }
                result.append(app_dict)

            return result

    def get_application_by_id(self, application_id: int) -> Optional[Application]:
        """Get application by ID."""
        with self.get_session() as session:
            application = (
                session.query(Application)
                .filter(Application.id == application_id)
                .first()
            )
            if application:
                session.expunge(application)
            return application

    def save_analysis_result(
        self, application_id: int, analysis_data: Dict[str, Any]
    ) -> AnalysisResult:
        """Save analysis result to database."""
        with self.get_session() as session:
            analysis_result = AnalysisResult(
                application_id=application_id,
                suitability_rating=analysis_data.get("rating"),
                recommendation=analysis_data.get("recommendation"),
                confidence_level=analysis_data.get("confidence"),
                strengths_analysis=analysis_data.get("strengths"),
                gaps_analysis=analysis_data.get("gaps"),
                missing_requirements=analysis_data.get("missing_requirements"),
                resume_improvements=json.dumps(analysis_data.get("resume_improvements"))
                if analysis_data.get("resume_improvements")
                else None,
                cover_letter_suggestions=json.dumps(analysis_data.get("cover_letter"))
                if analysis_data.get("cover_letter")
                else None,
                interview_preparation=json.dumps(
                    analysis_data.get("interview_questions")
                )
                if analysis_data.get("interview_questions")
                else None,
                next_steps=json.dumps(analysis_data.get("next_steps"))
                if analysis_data.get("next_steps")
                else None,
                analysis_timestamp=datetime.now(timezone.utc),
            )

            session.add(analysis_result)
            session.flush()  # Get the ID

            # Log analytics event
            self._log_analytics_event(
                session=session,
                event_type="analysis_completed",
                application_id=application_id,
                event_data={
                    "rating": analysis_data.get("rating"),
                    "recommendation": analysis_data.get("recommendation"),
                },
            )

            # Detach the object from session so it can be used outside
            session.expunge(analysis_result)
            return analysis_result

    def get_analytics_summary(
        self, person_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get analytics summary for applications."""
        with self.get_session() as session:
            query = session.query(Application)

            if person_email:
                query = query.join(Person).filter(Person.email == person_email)

            total_applications = query.count()

            # Status breakdown
            status_counts = {}
            for status in ApplicationStatus:
                count = query.filter(Application.status == status).count()
                if count > 0:
                    status_counts[status.value] = count

            # Success rate (offers received + accepted)
            success_count = query.filter(
                Application.status.in_(
                    [
                        ApplicationStatus.OFFER_RECEIVED,
                        ApplicationStatus.ACCEPTED,
                    ]
                )
            ).count()

            success_rate = (
                (success_count / total_applications * 100)
                if total_applications > 0
                else 0
            )

            # Recent activity (last 30 days)
            from datetime import timedelta

            thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
            recent_applications = query.filter(
                Application.created_at >= thirty_days_ago
            ).count()

            return {
                "total_applications": total_applications,
                "status_breakdown": status_counts,
                "success_rate": round(success_rate, 2),
                "recent_applications": recent_applications,
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }

    def export_data(self, person_email: Optional[str] = None) -> Dict[str, Any]:
        """Export all data for a person or all data."""
        with self.get_session() as session:
            export_data = {
                "export_timestamp": datetime.now(timezone.utc).isoformat(),
                "persons": [],
                "applications": [],
                "companies": [],
                "analysis_results": [],
            }

            # Get persons
            persons_query = session.query(Person)
            if person_email:
                persons_query = persons_query.filter(Person.email == person_email)

            for person in persons_query.all():
                person_data = {
                    "id": person.id,
                    "name": person.name,
                    "email": person.email,
                    "created_at": person.created_at.isoformat(),
                    "updated_at": person.updated_at.isoformat(),
                }
                export_data["persons"].append(person_data)

            # Get applications
            applications_query = session.query(Application)
            if person_email:
                applications_query = applications_query.join(Person).filter(
                    Person.email == person_email
                )

            for app in applications_query.all():
                app_data = {
                    "id": app.id,
                    "status": app.status.value,
                    "applied_date": app.applied_date.isoformat()
                    if app.applied_date
                    else None,
                    "notes": app.notes,
                    "company_name": app.company.name,
                    "job_title": app.job_posting.title if app.job_posting else None,
                    "created_at": app.created_at.isoformat(),
                    "updated_at": app.updated_at.isoformat(),
                }
                export_data["applications"].append(app_data)

            # Get companies
            companies_query = session.query(Company)
            if person_email:
                companies_query = (
                    companies_query.join(Application)
                    .join(Person)
                    .filter(Person.email == person_email)
                )

            for company in companies_query.distinct().all():
                company_data = {
                    "id": company.id,
                    "name": company.name,
                    "industry": company.industry,
                    "size": company.size,
                    "website": company.website,
                    "location": company.location,
                    "created_at": company.created_at.isoformat(),
                }
                export_data["companies"].append(company_data)

            # Get analysis results
            analysis_query = session.query(AnalysisResult)
            if person_email:
                analysis_query = (
                    analysis_query.join(Application)
                    .join(Person)
                    .filter(Person.email == person_email)
                )

            for analysis in analysis_query.all():
                analysis_data = {
                    "id": analysis.id,
                    "application_id": analysis.application_id,
                    "suitability_rating": analysis.suitability_rating,
                    "recommendation": analysis.recommendation,
                    "confidence_level": analysis.confidence_level,
                    "analysis_timestamp": analysis.analysis_timestamp.isoformat(),
                }
                export_data["analysis_results"].append(analysis_data)

            return export_data

    def _log_analytics_event(
        self,
        session: Session,
        event_type: str,
        person_id: Optional[int] = None,
        application_id: Optional[int] = None,
        event_data: Optional[Dict[str, Any]] = None,
    ):
        """Log analytics event."""
        event = AnalyticsEvent(
            event_type=event_type,
            person_id=person_id,
            application_id=application_id,
            event_data=json.dumps(event_data) if event_data else None,
        )
        session.add(event)


# Global database manager instance
db_manager = DatabaseManager()
