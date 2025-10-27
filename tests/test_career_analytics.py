"""
Tests for career analytics and insights features.
"""

import pytest
from datetime import datetime, date
from unittest.mock import Mock, patch
import tempfile
import os

from src.career_analytics_models import (
    CareerStage, SkillCategory, Industry, TrendDirection,
    SkillTrend, IndustryInsight, CareerMilestone, CareerProgression,
    PersonalizedRecommendation, CareerAnalytics, SalaryBenchmark,
    CompetitiveAnalysis, AnalyticsDashboard
)
from src.career_progression_tracker import CareerProgressionTracker
from src.industry_trend_analyzer import IndustryTrendAnalyzer
from src.personalized_recommendation_engine import PersonalizedRecommendationEngine
from src.analytics_dashboard import AnalyticsDashboard as AnalyticsDashboardClass


class TestCareerAnalyticsModels:
    """Test career analytics Pydantic models."""
    
    def test_skill_trend_creation(self):
        """Test creating skill trend."""
        trend = SkillTrend(
            skill_name="Python",
            category=SkillCategory.TECHNICAL,
            trend_direction=TrendDirection.RISING,
            demand_score=0.9,
            growth_rate=15.2,
            market_saturation=0.3,
            salary_impact=0.8
        )
        
        assert trend.skill_name == "Python"
        assert trend.category == SkillCategory.TECHNICAL
        assert trend.trend_direction == TrendDirection.RISING
        assert trend.demand_score == 0.9
    
    def test_industry_insight_creation(self):
        """Test creating industry insight."""
        insight = IndustryInsight(
            industry=Industry.TECHNOLOGY,
            growth_rate=8.5,
            average_salary_range={
                'entry': 65000,
                'mid': 95000,
                'senior': 140000
            },
            top_skills=['Python', 'JavaScript', 'Cloud Computing'],
            job_market_trends=['AI adoption', 'Remote work'],
            future_outlook='Strong growth expected'
        )
        
        assert insight.industry == Industry.TECHNOLOGY
        assert insight.growth_rate == 8.5
        assert len(insight.top_skills) == 3
    
    def test_career_milestone_creation(self):
        """Test creating career milestone."""
        milestone = CareerMilestone(
            milestone_type="skill_development",
            title="Technical Expertise",
            description="Develop advanced technical skills",
            status="in_progress",
            impact_score=0.8
        )
        
        assert milestone.milestone_type == "skill_development"
        assert milestone.title == "Technical Expertise"
        assert milestone.impact_score == 0.8
    
    def test_career_progression_creation(self):
        """Test creating career progression."""
        progression = CareerProgression(
            current_stage=CareerStage.MID_LEVEL,
            next_stage=CareerStage.SENIOR_LEVEL,
            progression_score=0.7,
            time_to_next_stage=18,
            skill_gaps=['Leadership', 'Architecture'],
            recommended_actions=['Take leadership training', 'Lead projects'],
            milestones=[]
        )
        
        assert progression.current_stage == CareerStage.MID_LEVEL
        assert progression.next_stage == CareerStage.SENIOR_LEVEL
        assert progression.progression_score == 0.7
        assert len(progression.skill_gaps) == 2
    
    def test_personalized_recommendation_creation(self):
        """Test creating personalized recommendation."""
        recommendation = PersonalizedRecommendation(
            recommendation_type="skill_development",
            priority="high",
            title="Learn Python",
            description="Develop Python skills for career growth",
            expected_impact="High salary increase potential",
            time_investment="3-6 months",
            difficulty_level="Medium",
            resources=["Online courses", "Projects"],
            success_metrics=["Complete certification", "Build project"]
        )
        
        assert recommendation.recommendation_type == "skill_development"
        assert recommendation.priority == "high"
        assert recommendation.title == "Learn Python"
        assert len(recommendation.resources) == 2
    
    def test_career_analytics_creation(self):
        """Test creating career analytics."""
        progression = CareerProgression(
            current_stage=CareerStage.MID_LEVEL,
            next_stage=CareerStage.SENIOR_LEVEL,
            progression_score=0.7,
            time_to_next_stage=18,
            skill_gaps=['Leadership'],
            recommended_actions=['Take training'],
            milestones=[]
        )
        
        analytics = CareerAnalytics(
            user_id="test_user",
            career_progression=progression,
            skill_trends=[],
            industry_insights=[],
            personalized_recommendations=[],
            career_score=75.0,
            market_position="Strong Competitor",
            competitive_advantages=["Strong technical skills"],
            areas_for_improvement=["Leadership skills"]
        )
        
        assert analytics.user_id == "test_user"
        assert analytics.career_score == 75.0
        assert analytics.market_position == "Strong Competitor"


class TestCareerProgressionTracker:
    """Test career progression tracker."""
    
    def test_tracker_initialization(self):
        """Test tracker initialization."""
        tracker = CareerProgressionTracker()
        
        assert tracker.stage_definitions is not None
        assert len(tracker.stage_definitions) == 5
        assert CareerStage.ENTRY_LEVEL in tracker.stage_definitions
    
    def test_determine_career_stage(self):
        """Test career stage determination."""
        tracker = CareerProgressionTracker()
        
        # Test with experience-based determination
        user_profile = {
            'total_experience_years': 3.0,
            'current_title': 'Software Developer'
        }
        
        stage = tracker._determine_career_stage(user_profile)
        assert stage == CareerStage.MID_LEVEL
        
        # Test with title-based determination
        user_profile = {
            'current_title': 'Senior Software Engineer'
        }
        
        stage = tracker._determine_career_stage(user_profile)
        assert stage == CareerStage.SENIOR_LEVEL
    
    def test_extract_experience_years(self):
        """Test experience years extraction."""
        tracker = CareerProgressionTracker()
        
        # Test with explicit field
        user_profile = {'total_experience_years': 5.0}
        years = tracker._extract_experience_years(user_profile)
        assert years == 5.0
        
        # Test with resume content
        user_profile = {
            'resume_content': 'Software Engineer with 3 years of experience'
        }
        years = tracker._extract_experience_years(user_profile)
        assert years == 3.0
    
    def test_parse_experience_from_resume(self):
        """Test parsing experience from resume."""
        tracker = CareerProgressionTracker()
        
        resume_content = """
        John Doe
        Software Engineer
        
        Experience:
        - Company A: Senior Developer (2020-2023)
        - Company B: Developer (2018-2020)
        
        5 years of experience in software development
        """
        
        years = tracker._parse_experience_from_resume(resume_content)
        assert years == 5.0
    
    def test_calculate_progression_score(self):
        """Test progression score calculation."""
        tracker = CareerProgressionTracker()
        
        user_profile = {
            'total_experience_years': 4.0,
            'skills': ['Python', 'JavaScript', 'Leadership'],
            'resume_content': 'Managed team of 5 developers'
        }
        
        score = tracker._calculate_progression_score(
            user_profile, CareerStage.MID_LEVEL, CareerStage.SENIOR_LEVEL
        )
        
        assert 0.0 <= score <= 1.0
    
    def test_identify_skill_gaps(self):
        """Test skill gap identification."""
        tracker = CareerProgressionTracker()
        
        user_profile = {
            'skills': ['Python', 'JavaScript']
        }
        
        gaps = tracker._identify_skill_gaps(
            user_profile, CareerStage.MID_LEVEL, CareerStage.SENIOR_LEVEL
        )
        
        assert isinstance(gaps, list)
        assert len(gaps) <= 5  # Should return top 5 gaps
    
    def test_analyze_career_progression(self):
        """Test complete career progression analysis."""
        tracker = CareerProgressionTracker()
        
        user_profile = {
            'total_experience_years': 3.0,
            'skills': ['Python', 'JavaScript', 'React'],
            'current_title': 'Software Developer',
            'resume_content': 'Software Developer with 3 years experience'
        }
        
        progression = tracker.analyze_career_progression(user_profile)
        
        assert isinstance(progression, CareerProgression)
        assert progression.current_stage is not None
        assert progression.next_stage is not None
        assert 0.0 <= progression.progression_score <= 1.0
        assert progression.time_to_next_stage > 0


class TestIndustryTrendAnalyzer:
    """Test industry trend analyzer."""
    
    def test_analyzer_initialization(self):
        """Test analyzer initialization."""
        analyzer = IndustryTrendAnalyzer()
        
        assert analyzer.industry_data is not None
        assert len(analyzer.industry_data) >= 5
        assert Industry.TECHNOLOGY in analyzer.industry_data
    
    def test_identify_relevant_industries(self):
        """Test relevant industry identification."""
        analyzer = IndustryTrendAnalyzer()
        
        user_profile = {
            'resume_content': 'Software Developer with Python and JavaScript experience',
            'current_title': 'Software Engineer'
        }
        
        industries = analyzer._identify_relevant_industries(user_profile)
        
        assert isinstance(industries, list)
        assert len(industries) <= 3
        assert Industry.TECHNOLOGY in industries
    
    def test_get_skill_trend_data(self):
        """Test skill trend data retrieval."""
        analyzer = IndustryTrendAnalyzer()
        
        # Test exact match
        trend_data = analyzer._get_skill_trend_data('Python')
        assert trend_data is not None
        assert 'demand' in trend_data
        assert 'growth' in trend_data
        
        # Test unknown skill
        trend_data = analyzer._get_skill_trend_data('UnknownSkill')
        assert trend_data is not None  # Should return default data
    
    def test_categorize_skill(self):
        """Test skill categorization."""
        analyzer = IndustryTrendAnalyzer()
        
        assert analyzer._categorize_skill('Python') == SkillCategory.TECHNICAL
        assert analyzer._categorize_skill('Communication') == SkillCategory.SOFT_SKILLS
        assert analyzer._categorize_skill('Leadership') == SkillCategory.LEADERSHIP
        assert analyzer._categorize_skill('AWS') == SkillCategory.TOOLS_TECHNOLOGIES
    
    def test_determine_trend_direction(self):
        """Test trend direction determination."""
        analyzer = IndustryTrendAnalyzer()
        
        # Rising trend
        trend_data = {'growth': 20.0, 'demand': 0.9}
        direction = analyzer._determine_trend_direction(trend_data)
        assert direction == TrendDirection.RISING
        
        # Declining trend
        trend_data = {'growth': 3.0, 'demand': 0.5}
        direction = analyzer._determine_trend_direction(trend_data)
        assert direction == TrendDirection.DECLINING
    
    def test_analyze_skill_trends(self):
        """Test skill trends analysis."""
        analyzer = IndustryTrendAnalyzer()
        
        user_skills = ['Python', 'JavaScript', 'Machine Learning']
        
        trends = analyzer.analyze_skill_trends(user_skills)
        
        assert isinstance(trends, list)
        assert len(trends) <= len(user_skills)
        
        for trend in trends:
            assert isinstance(trend, SkillTrend)
            assert trend.skill_name in user_skills
    
    def test_analyze_industry_trends(self):
        """Test industry trends analysis."""
        analyzer = IndustryTrendAnalyzer()
        
        user_profile = {
            'resume_content': 'Software Developer with Python experience',
            'current_title': 'Software Engineer'
        }
        
        insights = analyzer.analyze_industry_trends(user_profile)
        
        assert isinstance(insights, list)
        assert len(insights) <= 3
        
        for insight in insights:
            assert isinstance(insight, IndustryInsight)
            assert insight.industry in Industry
    
    def test_create_salary_benchmark(self):
        """Test salary benchmark creation."""
        analyzer = IndustryTrendAnalyzer()
        
        user_profile = {
            'current_title': 'Software Developer',
            'resume_content': 'Software Developer with 3 years experience',
            'location': 'United States'
        }
        
        benchmark = analyzer.create_salary_benchmark(user_profile)
        
        assert isinstance(benchmark, SalaryBenchmark)
        assert benchmark.position_title == 'Software Developer'
        assert benchmark.location == 'United States'
        assert 'min' in benchmark.salary_range
        assert 'max' in benchmark.salary_range
        assert 'median' in benchmark.salary_range
    
    def test_perform_competitive_analysis(self):
        """Test competitive analysis."""
        analyzer = IndustryTrendAnalyzer()
        
        user_profile = {
            'resume_content': 'Software Developer with Python and JavaScript experience',
            'skills': ['Python', 'JavaScript', 'React'],
            'current_title': 'Software Developer'
        }
        
        analysis = analyzer.perform_competitive_analysis(user_profile)
        
        assert isinstance(analysis, CompetitiveAnalysis)
        assert 0.0 <= analysis.competitive_score <= 100.0
        assert analysis.market_position is not None
        assert isinstance(analysis.strengths, list)
        assert isinstance(analysis.weaknesses, list)
        assert isinstance(analysis.opportunities, list)
        assert isinstance(analysis.threats, list)


class TestPersonalizedRecommendationEngine:
    """Test personalized recommendation engine."""
    
    def test_engine_initialization(self):
        """Test engine initialization."""
        engine = PersonalizedRecommendationEngine()
        
        assert engine.progression_tracker is not None
        assert engine.trend_analyzer is not None
        assert engine.recommendation_templates is not None
    
    def test_generate_skill_recommendations(self):
        """Test skill recommendation generation."""
        engine = PersonalizedRecommendationEngine()
        
        user_profile = {
            'skills': ['Python', 'JavaScript']
        }
        
        skill_trends = [
            SkillTrend(
                skill_name="Python",
                category=SkillCategory.TECHNICAL,
                trend_direction=TrendDirection.RISING,
                demand_score=0.9,
                growth_rate=15.0,
                market_saturation=0.3,
                salary_impact=0.8
            )
        ]
        
        recommendations = engine._generate_skill_recommendations(user_profile, skill_trends)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) <= 2  # Should return top 2
    
    def test_generate_progression_recommendations(self):
        """Test progression recommendation generation."""
        engine = PersonalizedRecommendationEngine()
        
        user_profile = {
            'skills': ['Python', 'JavaScript']
        }
        
        progression = CareerProgression(
            current_stage=CareerStage.MID_LEVEL,
            next_stage=CareerStage.SENIOR_LEVEL,
            progression_score=0.5,
            time_to_next_stage=24,
            skill_gaps=['Leadership', 'Architecture'],
            recommended_actions=['Take leadership training'],
            milestones=[]
        )
        
        recommendations = engine._generate_progression_recommendations(user_profile, progression)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) <= 1  # Should return 1 progression recommendation
    
    def test_generate_recommendations(self):
        """Test complete recommendation generation."""
        engine = PersonalizedRecommendationEngine()
        
        user_profile = {
            'user_id': 'test_user',
            'skills': ['Python', 'JavaScript'],
            'resume_content': 'Software Developer with 3 years experience',
            'current_title': 'Software Developer'
        }
        
        recommendations = engine.generate_recommendations(user_profile)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) <= 8  # Should return top 8
        
        for rec in recommendations:
            assert isinstance(rec, PersonalizedRecommendation)
            assert rec.priority in ['high', 'medium', 'low']
    
    def test_create_career_analytics(self):
        """Test career analytics creation."""
        engine = PersonalizedRecommendationEngine()
        
        user_profile = {
            'user_id': 'test_user',
            'skills': ['Python', 'JavaScript', 'React'],
            'resume_content': 'Software Developer with 3 years experience',
            'current_title': 'Software Developer'
        }
        
        analytics = engine.create_career_analytics(user_profile)
        
        assert isinstance(analytics, CareerAnalytics)
        assert analytics.user_id == 'test_user'
        assert 0.0 <= analytics.career_score <= 100.0
        assert analytics.market_position is not None
        assert isinstance(analytics.personalized_recommendations, list)
        assert isinstance(analytics.skill_trends, list)
        assert isinstance(analytics.industry_insights, list)


class TestAnalyticsDashboard:
    """Test analytics dashboard."""
    
    def test_dashboard_initialization(self):
        """Test dashboard initialization."""
        dashboard = AnalyticsDashboardClass()
        
        assert dashboard.recommendation_engine is not None
        assert dashboard.trend_analyzer is not None
        assert dashboard.progression_tracker is not None
    
    def test_create_dashboard(self):
        """Test dashboard creation."""
        dashboard = AnalyticsDashboardClass()
        
        user_profile = {
            'user_id': 'test_user',
            'skills': ['Python', 'JavaScript'],
            'resume_content': 'Software Developer with 3 years experience',
            'current_title': 'Software Developer'
        }
        
        dashboard_data = dashboard.create_dashboard(user_profile)
        
        assert isinstance(dashboard_data, AnalyticsDashboard)
        assert dashboard_data.user_id == 'test_user'
        assert isinstance(dashboard_data.career_analytics, CareerAnalytics)
        assert isinstance(dashboard_data.salary_benchmarks, list)
        assert isinstance(dashboard_data.competitive_analysis, CompetitiveAnalysis)
        assert isinstance(dashboard_data.key_metrics, dict)
        assert isinstance(dashboard_data.trends_summary, list)
        assert isinstance(dashboard_data.action_items, list)
    
    def test_calculate_key_metrics(self):
        """Test key metrics calculation."""
        dashboard = AnalyticsDashboardClass()
        
        # Create mock analytics
        progression = CareerProgression(
            current_stage=CareerStage.MID_LEVEL,
            next_stage=CareerStage.SENIOR_LEVEL,
            progression_score=0.7,
            time_to_next_stage=18,
            skill_gaps=['Leadership'],
            recommended_actions=['Take training'],
            milestones=[]
        )
        
        analytics = CareerAnalytics(
            user_id="test_user",
            career_progression=progression,
            skill_trends=[],
            industry_insights=[],
            personalized_recommendations=[],
            career_score=75.0,
            market_position="Strong Competitor",
            competitive_advantages=[],
            areas_for_improvement=[]
        )
        
        competitive_analysis = CompetitiveAnalysis(
            user_profile={},
            market_position="Strong Competitor",
            competitive_score=75.0,
            strengths=[],
            weaknesses=[],
            opportunities=[],
            threats=[],
            differentiation_strategy=[]
        )
        
        metrics = dashboard._calculate_key_metrics(analytics, competitive_analysis)
        
        assert isinstance(metrics, dict)
        assert 'career_score' in metrics
        assert 'progression_score' in metrics
        assert 'competitive_score' in metrics
        assert 'skill_demand_avg' in metrics
        assert 'industry_growth_avg' in metrics
        assert 'time_to_next_stage' in metrics
    
    def test_generate_trends_summary(self):
        """Test trends summary generation."""
        dashboard = AnalyticsDashboardClass()
        
        progression = CareerProgression(
            current_stage=CareerStage.MID_LEVEL,
            next_stage=CareerStage.SENIOR_LEVEL,
            progression_score=0.8,
            time_to_next_stage=12,
            skill_gaps=[],
            recommended_actions=[],
            milestones=[]
        )
        
        skill_trends = [
            SkillTrend(
                skill_name="Python",
                category=SkillCategory.TECHNICAL,
                trend_direction=TrendDirection.RISING,
                demand_score=0.9,
                growth_rate=15.0,
                market_saturation=0.3,
                salary_impact=0.8
            )
        ]
        
        industry_insights = [
            IndustryInsight(
                industry=Industry.TECHNOLOGY,
                growth_rate=8.5,
                average_salary_range={},
                top_skills=[],
                job_market_trends=[],
                future_outlook="Strong growth"
            )
        ]
        
        analytics = CareerAnalytics(
            user_id="test_user",
            career_progression=progression,
            skill_trends=skill_trends,
            industry_insights=industry_insights,
            personalized_recommendations=[],
            career_score=80.0,
            market_position="Top Performer",
            competitive_advantages=[],
            areas_for_improvement=[]
        )
        
        trends = dashboard._generate_trends_summary(analytics)
        
        assert isinstance(trends, list)
        assert len(trends) > 0
        
        for trend in trends:
            assert isinstance(trend, str)
            assert len(trend) > 0
    
    def test_generate_action_items(self):
        """Test action items generation."""
        dashboard = AnalyticsDashboardClass()
        
        progression = CareerProgression(
            current_stage=CareerStage.MID_LEVEL,
            next_stage=CareerStage.SENIOR_LEVEL,
            progression_score=0.5,
            time_to_next_stage=24,
            skill_gaps=['Leadership', 'Architecture'],
            recommended_actions=['Take training'],
            milestones=[]
        )
        
        recommendations = [
            PersonalizedRecommendation(
                recommendation_type="skill_development",
                priority="high",
                title="Learn Leadership",
                description="Develop leadership skills",
                expected_impact="Career advancement",
                time_investment="6 months",
                difficulty_level="Medium",
                resources=[],
                success_metrics=[]
            )
        ]
        
        analytics = CareerAnalytics(
            user_id="test_user",
            career_progression=progression,
            skill_trends=[],
            industry_insights=[],
            personalized_recommendations=recommendations,
            career_score=60.0,
            market_position="Average Competitor",
            competitive_advantages=[],
            areas_for_improvement=[]
        )
        
        action_items = dashboard._generate_action_items(analytics)
        
        assert isinstance(action_items, list)
        assert len(action_items) <= 5  # Should return top 5
        
        for item in action_items:
            assert isinstance(item, str)
            assert len(item) > 0


class TestIntegration:
    """Integration tests for career analytics."""
    
    def test_full_career_analytics_workflow(self):
        """Test complete career analytics workflow."""
        engine = PersonalizedRecommendationEngine()
        
        user_profile = {
            'user_id': 'test_user',
            'email': 'test@example.com',
            'skills': ['Python', 'JavaScript', 'React'],
            'resume_content': '''
            John Doe
            Software Developer
            
            Experience:
            - Company A: Software Developer (2020-2023)
            - Company B: Junior Developer (2018-2020)
            
            Skills: Python, JavaScript, React, SQL, Git
            
            Education: Bachelor's in Computer Science
            ''',
            'current_title': 'Software Developer',
            'location': 'United States'
        }
        
        analytics = engine.create_career_analytics(user_profile)
        
        assert isinstance(analytics, CareerAnalytics)
        assert analytics.user_id == 'test_user'
        assert 0.0 <= analytics.career_score <= 100.0
        assert analytics.career_progression.current_stage is not None
        assert analytics.career_progression.next_stage is not None
        assert len(analytics.personalized_recommendations) > 0
        assert len(analytics.skill_trends) > 0
        assert len(analytics.industry_insights) > 0
    
    def test_dashboard_workflow(self):
        """Test complete dashboard workflow."""
        dashboard = AnalyticsDashboardClass()
        
        user_profile = {
            'user_id': 'test_user',
            'skills': ['Python', 'JavaScript'],
            'resume_content': 'Software Developer with 3 years experience',
            'current_title': 'Software Developer'
        }
        
        dashboard_data = dashboard.create_dashboard(user_profile)
        
        assert isinstance(dashboard_data, AnalyticsDashboard)
        assert dashboard_data.user_id == 'test_user'
        assert isinstance(dashboard_data.career_analytics, CareerAnalytics)
        assert isinstance(dashboard_data.salary_benchmarks, list)
        assert isinstance(dashboard_data.competitive_analysis, CompetitiveAnalysis)
        assert isinstance(dashboard_data.key_metrics, dict)
        assert len(dashboard_data.key_metrics) > 0
        assert isinstance(dashboard_data.trends_summary, list)
        assert isinstance(dashboard_data.action_items, list)
