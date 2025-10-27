"""
Pydantic models for career analytics and insights.
"""

from enum import Enum
from typing import List, Dict, Optional, Any, Union
from datetime import datetime, date
from pydantic import BaseModel, Field, field_validator


class CareerStage(str, Enum):
    """Career development stages."""
    ENTRY_LEVEL = "entry_level"
    MID_LEVEL = "mid_level"
    SENIOR_LEVEL = "senior_level"
    LEADERSHIP = "leadership"
    EXECUTIVE = "executive"


class SkillCategory(str, Enum):
    """Skill categories for analysis."""
    TECHNICAL = "technical"
    SOFT_SKILLS = "soft_skills"
    LEADERSHIP = "leadership"
    DOMAIN_KNOWLEDGE = "domain_knowledge"
    TOOLS_TECHNOLOGIES = "tools_technologies"


class Industry(str, Enum):
    """Industry classifications."""
    TECHNOLOGY = "technology"
    FINANCE = "finance"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    MANUFACTURING = "manufacturing"
    RETAIL = "retail"
    CONSULTING = "consulting"
    GOVERNMENT = "government"
    NON_PROFIT = "non_profit"
    OTHER = "other"


class TrendDirection(str, Enum):
    """Trend direction indicators."""
    RISING = "rising"
    STABLE = "stable"
    DECLINING = "declining"
    EMERGING = "emerging"


class SkillTrend(BaseModel):
    """Skill trend analysis."""
    
    skill_name: str = Field(description="Name of the skill")
    category: SkillCategory = Field(description="Skill category")
    trend_direction: TrendDirection = Field(description="Current trend direction")
    demand_score: float = Field(description="Demand score (0.0-1.0)")
    growth_rate: float = Field(description="Growth rate percentage")
    market_saturation: float = Field(description="Market saturation (0.0-1.0)")
    salary_impact: float = Field(description="Salary impact score (0.0-1.0)")
    
    @field_validator('demand_score', 'market_saturation', 'salary_impact')
    @classmethod
    def validate_scores(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError('Score must be between 0.0 and 1.0')
        return v
    
    model_config = {"validate_assignment": True}


class IndustryInsight(BaseModel):
    """Industry-specific insights."""
    
    industry: Industry = Field(description="Industry classification")
    growth_rate: float = Field(description="Industry growth rate")
    average_salary_range: Dict[str, float] = Field(description="Salary range by level")
    top_skills: List[str] = Field(description="Most in-demand skills")
    job_market_trends: List[str] = Field(description="Current market trends")
    future_outlook: str = Field(description="Future industry outlook")
    
    model_config = {"validate_assignment": True}


class CareerMilestone(BaseModel):
    """Career milestone tracking."""
    
    milestone_type: str = Field(description="Type of milestone")
    title: str = Field(description="Milestone title")
    description: str = Field(description="Milestone description")
    achieved_date: Optional[date] = Field(default=None, description="Date achieved")
    target_date: Optional[date] = Field(default=None, description="Target date")
    status: str = Field(description="Milestone status")
    impact_score: float = Field(description="Career impact score (0.0-1.0)")
    
    @field_validator('impact_score')
    @classmethod
    def validate_impact_score(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError('Impact score must be between 0.0 and 1.0')
        return v
    
    model_config = {"validate_assignment": True}


class CareerProgression(BaseModel):
    """Career progression analysis."""
    
    current_stage: CareerStage = Field(description="Current career stage")
    next_stage: CareerStage = Field(description="Next target stage")
    progression_score: float = Field(description="Progression readiness score (0.0-1.0)")
    time_to_next_stage: int = Field(description="Estimated months to next stage")
    skill_gaps: List[str] = Field(description="Skills needed for progression")
    recommended_actions: List[str] = Field(description="Recommended actions")
    milestones: List[CareerMilestone] = Field(description="Career milestones")
    
    @field_validator('progression_score')
    @classmethod
    def validate_progression_score(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError('Progression score must be between 0.0 and 1.0')
        return v
    
    model_config = {"validate_assignment": True}


class PersonalizedRecommendation(BaseModel):
    """Personalized career recommendation."""
    
    recommendation_type: str = Field(description="Type of recommendation")
    priority: str = Field(description="Priority level")
    title: str = Field(description="Recommendation title")
    description: str = Field(description="Detailed description")
    expected_impact: str = Field(description="Expected career impact")
    time_investment: str = Field(description="Required time investment")
    difficulty_level: str = Field(description="Difficulty level")
    resources: List[str] = Field(description="Recommended resources")
    success_metrics: List[str] = Field(description="Success metrics")
    priority_score: Optional[float] = Field(default=None, description="Calculated priority score")
    
    model_config = {"validate_assignment": True}


class CareerAnalytics(BaseModel):
    """Comprehensive career analytics."""
    
    user_id: str = Field(description="User identifier")
    analysis_date: datetime = Field(default_factory=datetime.now, description="Analysis date")
    career_progression: CareerProgression = Field(description="Career progression analysis")
    skill_trends: List[SkillTrend] = Field(description="Skill trend analysis")
    industry_insights: List[IndustryInsight] = Field(description="Industry insights")
    personalized_recommendations: List[PersonalizedRecommendation] = Field(description="Personalized recommendations")
    career_score: float = Field(description="Overall career score (0-100)")
    market_position: str = Field(description="Current market position")
    competitive_advantages: List[str] = Field(description="Competitive advantages")
    areas_for_improvement: List[str] = Field(description="Areas needing improvement")
    
    @field_validator('career_score')
    @classmethod
    def validate_career_score(cls, v: float) -> float:
        if not 0.0 <= v <= 100.0:
            raise ValueError('Career score must be between 0.0 and 100.0')
        return v
    
    model_config = {"validate_assignment": True}


class SalaryBenchmark(BaseModel):
    """Salary benchmarking data."""
    
    position_title: str = Field(description="Job title")
    industry: Industry = Field(description="Industry")
    experience_level: str = Field(description="Experience level")
    location: str = Field(description="Geographic location")
    salary_range: Dict[str, float] = Field(description="Salary range (min, max, median)")
    percentile_data: Dict[str, float] = Field(description="Percentile breakdown")
    market_trends: List[str] = Field(description="Market trends affecting salary")
    
    model_config = {"validate_assignment": True}


class CompetitiveAnalysis(BaseModel):
    """Competitive positioning analysis."""
    
    user_profile: Dict[str, Any] = Field(description="User profile data")
    market_position: str = Field(description="Current market position")
    competitive_score: float = Field(description="Competitive score (0-100)")
    strengths: List[str] = Field(description="Competitive strengths")
    weaknesses: List[str] = Field(description="Competitive weaknesses")
    opportunities: List[str] = Field(description="Market opportunities")
    threats: List[str] = Field(description="Market threats")
    differentiation_strategy: List[str] = Field(description="Differentiation strategies")
    
    @field_validator('competitive_score')
    @classmethod
    def validate_competitive_score(cls, v: float) -> float:
        if not 0.0 <= v <= 100.0:
            raise ValueError('Competitive score must be between 0.0 and 100.0')
        return v
    
    model_config = {"validate_assignment": True}


class AnalyticsDashboard(BaseModel):
    """Analytics dashboard data."""
    
    user_id: str = Field(description="User identifier")
    dashboard_date: datetime = Field(default_factory=datetime.now, description="Dashboard date")
    career_analytics: CareerAnalytics = Field(description="Career analytics")
    salary_benchmarks: List[SalaryBenchmark] = Field(description="Salary benchmarks")
    competitive_analysis: CompetitiveAnalysis = Field(description="Competitive analysis")
    key_metrics: Dict[str, float] = Field(description="Key performance metrics")
    trends_summary: List[str] = Field(description="Trends summary")
    action_items: List[str] = Field(description="Priority action items")
    
    model_config = {"validate_assignment": True}
