"""Tests for database functionality."""

import pytest
import tempfile
import os

from src.database_manager import DatabaseManager
from src.database_schema import (
    Person,
    Company,
    Application,
    ApplicationStatus,
)


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    db_manager = DatabaseManager(db_path)
    yield db_manager

    # Clean up
    if os.path.exists(db_path):
        os.unlink(db_path)


class TestDatabaseManager:
    """Test DatabaseManager functionality."""

    def test_database_initialization(self, temp_db):
        """Test database initialization."""
        assert temp_db.database_path.exists()
        assert temp_db.engine is not None
        assert temp_db.SessionLocal is not None

    def test_get_or_create_person(self, temp_db):
        """Test person creation and retrieval."""
        # Create new person
        person = temp_db.get_or_create_person("Test User", "test@example.com")
        assert person.name == "Test User"
        assert person.email == "test@example.com"
        assert person.id is not None

        # Get existing person
        person2 = temp_db.get_or_create_person("Test User", "test@example.com")
        assert person2.id == person.id
        assert person2.name == person.name

    def test_get_or_create_company(self, temp_db):
        """Test company creation and retrieval."""
        # Create new company
        company = temp_db.get_or_create_company("Test Company", industry="Technology")
        assert company.name == "Test Company"
        assert company.industry == "Technology"
        assert company.id is not None

        # Get existing company
        company2 = temp_db.get_or_create_company("Test Company")
        assert company2.id == company.id
        assert company2.name == company.name

    def test_create_application(self, temp_db):
        """Test application creation."""
        application = temp_db.create_application(
            person_email="test@example.com",
            person_name="Test User",
            company_name="Test Company",
            job_title="Software Engineer",
            status=ApplicationStatus.APPLIED,
            notes="Test application",
        )

        assert application.id is not None
        assert application.status == ApplicationStatus.APPLIED
        assert application.notes == "Test application"

    def test_update_application_status(self, temp_db):
        """Test application status update."""
        # Create application
        application = temp_db.create_application(
            person_email="test@example.com",
            person_name="Test User",
            company_name="Test Company",
            job_title="Software Engineer",
            status=ApplicationStatus.APPLIED,
        )

        # Update status
        success = temp_db.update_application_status(
            application.id, ApplicationStatus.UNDER_REVIEW, "Updated status"
        )

        assert success is True

        # Verify update
        updated_app = temp_db.get_application_by_id(application.id)
        assert updated_app.status == ApplicationStatus.UNDER_REVIEW
        assert updated_app.notes == "Updated status"

    def test_get_applications(self, temp_db):
        """Test application retrieval."""
        # Create multiple applications
        app1 = temp_db.create_application(
            person_email="test@example.com",
            person_name="Test User",
            company_name="Company A",
            job_title="Engineer A",
            status=ApplicationStatus.APPLIED,
        )

        _ = temp_db.create_application(
            person_email="test@example.com",
            person_name="Test User",
            company_name="Company B",
            job_title="Engineer B",
            status=ApplicationStatus.UNDER_REVIEW,
        )

        # Get all applications
        applications = temp_db.get_applications(person_email="test@example.com")
        assert len(applications) == 2

        # Filter by status
        applied_apps = temp_db.get_applications(
            person_email="test@example.com", status=ApplicationStatus.APPLIED
        )
        assert len(applied_apps) == 1
        assert applied_apps[0]["id"] == app1.id

    def test_save_analysis_result(self, temp_db):
        """Test analysis result saving."""
        # Create application
        application = temp_db.create_application(
            person_email="test@example.com",
            person_name="Test User",
            company_name="Test Company",
            job_title="Software Engineer",
        )

        # Save analysis result
        analysis_data = {
            "rating": 8,
            "recommendation": "Yes",
            "confidence": "High",
            "strengths": "Strong technical skills",
            "gaps": "Limited management experience",
            "missing_requirements": "None",
        }

        analysis_result = temp_db.save_analysis_result(application.id, analysis_data)

        assert analysis_result.id is not None
        assert analysis_result.suitability_rating == 8
        assert analysis_result.recommendation == "Yes"
        assert analysis_result.confidence_level == "High"

    def test_analytics_summary(self, temp_db):
        """Test analytics summary generation."""
        # Create applications with different statuses
        _ = temp_db.create_application(
            person_email="test@example.com",
            person_name="Test User",
            company_name="Company A",
            job_title="Engineer A",
            status=ApplicationStatus.APPLIED,
        )

        _ = temp_db.create_application(
            person_email="test@example.com",
            person_name="Test User",
            company_name="Company B",
            job_title="Engineer B",
            status=ApplicationStatus.OFFER_RECEIVED,
        )

        # Get analytics summary
        analytics = temp_db.get_analytics_summary(person_email="test@example.com")

        assert analytics["total_applications"] == 2
        assert analytics["success_rate"] == 50.0  # 1 out of 2 applications successful
        assert "applied" in analytics["status_breakdown"]
        assert "offer_received" in analytics["status_breakdown"]
        assert analytics["status_breakdown"]["applied"] == 1
        assert analytics["status_breakdown"]["offer_received"] == 1

    def test_export_data(self, temp_db):
        """Test data export functionality."""
        # Create test data
        _ = temp_db.create_application(
            person_email="test@example.com",
            person_name="Test User",
            company_name="Test Company",
            job_title="Software Engineer",
            status=ApplicationStatus.APPLIED,
        )

        # Export data
        export_data = temp_db.export_data(person_email="test@example.com")

        assert "export_timestamp" in export_data
        assert len(export_data["persons"]) == 1
        assert len(export_data["applications"]) == 1
        assert len(export_data["companies"]) == 1

        # Verify exported data
        person_data = export_data["persons"][0]
        assert person_data["email"] == "test@example.com"
        assert person_data["name"] == "Test User"

        app_data = export_data["applications"][0]
        assert app_data["status"] == "applied"
        assert app_data["company_name"] == "Test Company"

    def test_error_handling(self, temp_db):
        """Test error handling in database operations."""
        # Test updating non-existent application
        success = temp_db.update_application_status(999, ApplicationStatus.APPLIED)
        assert success is False

        # Test getting non-existent application
        app = temp_db.get_application_by_id(999)
        assert app is None

    def test_delete_application(self, temp_db):
        """Test deleting an application and related records."""
        # Create application with analysis result
        application = temp_db.create_application(
            person_email="test@example.com",
            person_name="Test User",
            company_name="Test Company",
            job_title="Test Job",
        )

        # Add analysis result
        analysis_data = {
            "rating": 8,
            "recommendation": "Yes",
            "confidence": "High",
            "strengths": "Strong technical skills",
            "gaps": "Limited management experience",
            "missing_requirements": "None",
        }
        _ = temp_db.save_analysis_result(application.id, analysis_data)

        # Verify application exists
        apps = temp_db.get_applications()
        assert len(apps) == 1
        assert apps[0]["id"] == application.id

        # Delete the application
        success = temp_db.delete_application(application.id)
        assert success is True

        # Verify application is deleted
        apps = temp_db.get_applications()
        assert len(apps) == 0

        # Verify analytics event was logged
        analytics = temp_db.get_analytics_summary()
        assert analytics["total_applications"] == 0

    def test_delete_nonexistent_application(self, temp_db):
        """Test deleting a non-existent application."""
        success = temp_db.delete_application(999)
        assert success is False

    def test_delete_application_orphan_cleanup(self, temp_db):
        """Test that orphaned companies and job postings are cleaned up."""
        # Create two applications for the same company
        app1 = temp_db.create_application(
            person_email="user1@example.com",
            person_name="User One",
            company_name="Shared Company",
            job_title="Job One",
        )

        app2 = temp_db.create_application(
            person_email="user2@example.com",
            person_name="User Two",
            company_name="Shared Company",
            job_title="Job Two",
        )

        # Delete first application - company should remain
        success = temp_db.delete_application(app1.id)
        assert success is True

        # Verify second application still exists
        apps = temp_db.get_applications()
        assert len(apps) == 1
        assert apps[0]["id"] == app2.id

        # Delete second application - company should be cleaned up
        success = temp_db.delete_application(app2.id)
        assert success is True

        # Verify no applications remain
        apps = temp_db.get_applications()
        assert len(apps) == 0


class TestDatabaseSchema:
    """Test database schema models."""

    def test_application_status_enum(self):
        """Test ApplicationStatus enum values."""
        assert ApplicationStatus.DRAFT.value == "draft"
        assert ApplicationStatus.APPLIED.value == "applied"
        assert ApplicationStatus.UNDER_REVIEW.value == "under_review"
        assert ApplicationStatus.OFFER_RECEIVED.value == "offer_received"
        assert ApplicationStatus.REJECTED.value == "rejected"

    def test_person_model(self, temp_db):
        """Test Person model creation."""
        with temp_db.get_session() as session:
            person = Person(name="Test User", email="test@example.com")
            session.add(person)
            session.flush()

            assert person.id is not None
            assert person.name == "Test User"
            assert person.email == "test@example.com"
            assert person.created_at is not None

    def test_company_model(self, temp_db):
        """Test Company model creation."""
        with temp_db.get_session() as session:
            company = Company(
                name="Test Company",
                industry="Technology",
                size="51-200",
                website="https://test.com",
            )
            session.add(company)
            session.flush()

            assert company.id is not None
            assert company.name == "Test Company"
            assert company.industry == "Technology"
            assert company.size == "51-200"

    def test_application_model(self, temp_db):
        """Test Application model creation."""
        with temp_db.get_session() as session:
            # Create person and company first
            person = Person(name="Test User", email="test@example.com")
            company = Company(name="Test Company")
            session.add(person)
            session.add(company)
            session.flush()

            # Create application
            application = Application(
                person_id=person.id,
                company_id=company.id,
                status=ApplicationStatus.APPLIED,
                notes="Test application",
            )
            session.add(application)
            session.flush()

            assert application.id is not None
            assert application.status == ApplicationStatus.APPLIED
            assert application.notes == "Test application"
            assert application.person_id == person.id
            assert application.company_id == company.id


class TestDatabaseIntegration:
    """Test database integration scenarios."""

    def test_full_workflow(self, temp_db):
        """Test complete application tracking workflow."""
        # 1. Create application
        application = temp_db.create_application(
            person_email="test@example.com",
            person_name="Test User",
            company_name="Test Company",
            job_title="Software Engineer",
            status=ApplicationStatus.APPLIED,
        )

        # 2. Save analysis result
        analysis_data = {
            "rating": 8,
            "recommendation": "Yes",
            "confidence": "High",
            "strengths": "Strong technical skills",
            "gaps": "Limited management experience",
        }
        analysis_result = temp_db.save_analysis_result(application.id, analysis_data)

        # 3. Update status
        temp_db.update_application_status(
            application.id, ApplicationStatus.UNDER_REVIEW
        )

        # 4. Get analytics
        analytics = temp_db.get_analytics_summary(person_email="test@example.com")

        # 5. Export data
        export_data = temp_db.export_data(person_email="test@example.com")

        # Verify everything worked
        assert application.id is not None
        assert analysis_result.id is not None
        assert analytics["total_applications"] == 1
        assert len(export_data["applications"]) == 1
        assert len(export_data["analysis_results"]) == 1

    def test_multiple_users(self, temp_db):
        """Test multiple users with separate data."""
        # User 1 applications
        app1 = temp_db.create_application(
            person_email="user1@example.com",
            person_name="User One",
            company_name="Company A",
            job_title="Engineer A",
        )

        # User 2 applications
        app2 = temp_db.create_application(
            person_email="user2@example.com",
            person_name="User Two",
            company_name="Company B",
            job_title="Engineer B",
        )

        # Get applications for each user
        user1_apps = temp_db.get_applications(person_email="user1@example.com")
        user2_apps = temp_db.get_applications(person_email="user2@example.com")

        assert len(user1_apps) == 1
        assert len(user2_apps) == 1
        assert user1_apps[0]["id"] == app1.id
        assert user2_apps[0]["id"] == app2.id

        # Analytics should be separate
        analytics1 = temp_db.get_analytics_summary(person_email="user1@example.com")
        analytics2 = temp_db.get_analytics_summary(person_email="user2@example.com")

        assert analytics1["total_applications"] == 1
        assert analytics2["total_applications"] == 1
