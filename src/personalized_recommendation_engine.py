"""
Personalized recommendation engine for career development.
"""

import logging
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime, date, timedelta
import random

from rich.console import Console

from .career_analytics_models import (
    PersonalizedRecommendation, CareerAnalytics, CareerStage, SkillCategory,
    Industry, TrendDirection
)
from .career_progression_tracker import CareerProgressionTracker
from .industry_trend_analyzer import IndustryTrendAnalyzer

logger = logging.getLogger(__name__)
console = Console()


class PersonalizedRecommendationEngine:
    """Generates personalized career recommendations."""
    
    def __init__(self):
        self.logger = logger
        self.progression_tracker = CareerProgressionTracker()
        self.trend_analyzer = IndustryTrendAnalyzer()
        
        # Recommendation templates
        self.recommendation_templates = {
            'skill_development': {
                'high_priority': {
                    'title': "Develop High-Demand Skills",
                    'description': "Focus on {skill_name} to increase marketability and salary potential",
                    'expected_impact': "High salary increase potential",
                    'time_investment': "3-6 months",
                    'difficulty_level': "Medium",
                    'resources': [
                        "Online courses and certifications",
                        "Hands-on projects",
                        "Industry conferences and meetups"
                    ],
                    'success_metrics': [
                        "Complete certification",
                        "Build portfolio project",
                        "Apply skills in current role"
                    ]
                }
            },
            'career_progression': {
                'high_priority': {
                    'title': "Advance to Next Career Stage",
                    'description': "Develop {skill_gap} skills to progress to {next_stage} level",
                    'expected_impact': "Career advancement and increased responsibilities",
                    'time_investment': "6-12 months",
                    'difficulty_level': "High",
                    'resources': [
                        "Leadership training programs",
                        "Mentorship opportunities",
                        "Advanced certifications"
                    ],
                    'success_metrics': [
                        "Take on leadership responsibilities",
                        "Complete advanced training",
                        "Achieve promotion or role change"
                    ]
                }
            },
            'industry_transition': {
                'medium_priority': {
                    'title': "Explore Industry Transition",
                    'description': "Consider transitioning to {industry} for better growth opportunities",
                    'expected_impact': "Access to growing market with higher demand",
                    'time_investment': "12-18 months",
                    'difficulty_level': "High",
                    'resources': [
                        "Industry-specific training",
                        "Networking events",
                        "Side projects in target industry"
                    ],
                    'success_metrics': [
                        "Complete industry-specific training",
                        "Build network in target industry",
                        "Secure interview in target industry"
                    ]
                }
            },
            'salary_optimization': {
                'medium_priority': {
                    'title': "Optimize Salary Potential",
                    'description': "Develop {skill_name} to increase salary by {salary_increase}%",
                    'expected_impact': "Significant salary increase",
                    'time_investment': "6-9 months",
                    'difficulty_level': "Medium",
                    'resources': [
                        "High-value skill certifications",
                        "Salary negotiation training",
                        "Market research and benchmarking"
                    ],
                    'success_metrics': [
                        "Achieve salary increase",
                        "Complete high-value certification",
                        "Improve negotiation skills"
                    ]
                }
            },
            'networking': {
                'low_priority': {
                    'title': "Build Professional Network",
                    'description': "Expand professional network in {industry} industry",
                    'expected_impact': "Better job opportunities and career insights",
                    'time_investment': "Ongoing",
                    'difficulty_level': "Low",
                    'resources': [
                        "LinkedIn networking",
                        "Industry conferences",
                        "Professional associations"
                    ],
                    'success_metrics': [
                        "Connect with 50+ industry professionals",
                        "Attend 3+ industry events",
                        "Join professional association"
                    ]
                }
            },
            'education': {
                'medium_priority': {
                    'title': "Pursue Advanced Education",
                    'description': "Consider {education_type} to enhance career prospects",
                    'expected_impact': "Long-term career advancement",
                    'time_investment': "1-3 years",
                    'difficulty_level': "High",
                    'resources': [
                        "University programs",
                        "Online degree programs",
                        "Professional certifications"
                    ],
                    'success_metrics': [
                        "Complete degree or certification",
                        "Apply new knowledge in role",
                        "Achieve career advancement"
                    ]
                }
            }
        }
    
    def generate_recommendations(self, user_profile: Dict[str, Any]) -> List[PersonalizedRecommendation]:
        """
        Generate personalized career recommendations.
        
        Args:
            user_profile: User profile data
            
        Returns:
            List of personalized recommendations
        """
        console.print("[blue]Generating personalized recommendations...[/blue]")
        
        recommendations = []
        
        # Analyze user's current situation
        career_progression = self.progression_tracker.analyze_career_progression(user_profile)
        skill_trends = self.trend_analyzer.analyze_skill_trends(user_profile.get('skills', []))
        industry_insights = self.trend_analyzer.analyze_industry_trends(user_profile)
        competitive_analysis = self.trend_analyzer.perform_competitive_analysis(user_profile)
        
        # Generate different types of recommendations
        recommendations.extend(self._generate_skill_recommendations(user_profile, skill_trends))
        recommendations.extend(self._generate_progression_recommendations(user_profile, career_progression))
        recommendations.extend(self._generate_industry_recommendations(user_profile, industry_insights))
        recommendations.extend(self._generate_salary_recommendations(user_profile, competitive_analysis))
        recommendations.extend(self._generate_networking_recommendations(user_profile, industry_insights))
        recommendations.extend(self._generate_education_recommendations(user_profile, career_progression))
        
        # Prioritize and limit recommendations
        recommendations = self._prioritize_recommendations(recommendations, user_profile)
        recommendations = recommendations[:8]  # Limit to top 8 recommendations
        
        console.print(f"[green]✓ Generated {len(recommendations)} personalized recommendations[/green]")
        
        return recommendations
    
    def _generate_skill_recommendations(self, user_profile: Dict[str, Any], 
                                      skill_trends: List) -> List[PersonalizedRecommendation]:
        """Generate skill development recommendations."""
        
        recommendations = []
        user_skills = [skill.lower() for skill in user_profile.get('skills', [])]
        
        # Find high-demand skills user doesn't have
        high_demand_skills = [
            'Machine Learning', 'Cloud Computing', 'DevOps', 'Kubernetes',
            'Python', 'JavaScript', 'React', 'AWS', 'Docker', 'Data Analysis'
        ]
        
        for skill in high_demand_skills:
            if not any(skill.lower() in user_skill for user_skill in user_skills):
                # Get skill trend data
                trend_data = self.trend_analyzer._get_skill_trend_data(skill)
                
                if trend_data and trend_data['demand'] > 0.8:
                    recommendation = PersonalizedRecommendation(
                        recommendation_type='skill_development',
                        priority='high' if trend_data['demand'] > 0.9 else 'medium',
                        title=f"Learn {skill}",
                        description=f"Develop {skill} skills to increase marketability and salary potential",
                        expected_impact=f"High salary increase potential ({trend_data['growth']:.1f}% growth)",
                        time_investment="3-6 months",
                        difficulty_level="Medium",
                        resources=[
                            f"{skill} online courses",
                            "Hands-on projects",
                            "Industry certifications"
                        ],
                        success_metrics=[
                            f"Complete {skill} certification",
                            f"Build {skill} portfolio project",
                            f"Apply {skill} in current role"
                        ]
                    )
                    recommendations.append(recommendation)
        
        return recommendations[:2]  # Limit to top 2 skill recommendations
    
    def _generate_progression_recommendations(self, user_profile: Dict[str, Any], 
                                            career_progression) -> List[PersonalizedRecommendation]:
        """Generate career progression recommendations."""
        
        recommendations = []
        
        if career_progression.progression_score < 0.7:
            # User needs to develop skills for next stage
            skill_gaps = career_progression.skill_gaps[:2]  # Top 2 gaps
            
            for skill_gap in skill_gaps:
                recommendation = PersonalizedRecommendation(
                    recommendation_type='career_progression',
                    priority='high',
                    title=f"Develop {skill_gap} Skills",
                    description=f"Focus on {skill_gap} to progress to {career_progression.next_stage.value.replace('_', ' ').title()} level",
                    expected_impact="Career advancement and increased responsibilities",
                    time_investment="6-12 months",
                    difficulty_level="High",
                    resources=[
                        f"{skill_gap} training programs",
                        "Mentorship opportunities",
                        "Advanced certifications"
                    ],
                    success_metrics=[
                        f"Master {skill_gap} skills",
                        "Take on leadership responsibilities",
                        "Achieve promotion or role change"
                    ]
                )
                recommendations.append(recommendation)
        
        return recommendations[:1]  # Limit to 1 progression recommendation
    
    def _generate_industry_recommendations(self, user_profile: Dict[str, Any], 
                                         industry_insights: List) -> List[PersonalizedRecommendation]:
        """Generate industry transition recommendations."""
        
        recommendations = []
        
        # Find high-growth industries user isn't currently in
        current_industry = self.trend_analyzer._identify_primary_industry(user_profile)
        
        for insight in industry_insights:
            if insight.industry != current_industry and insight.growth_rate > 6.0:
                recommendation = PersonalizedRecommendation(
                    recommendation_type='industry_transition',
                    priority='medium',
                    title=f"Explore {insight.industry.value.title()} Industry",
                    description=f"Consider transitioning to {insight.industry.value} for {insight.growth_rate}% growth opportunities",
                    expected_impact="Access to growing market with higher demand",
                    time_investment="12-18 months",
                    difficulty_level="High",
                    resources=[
                        f"{insight.industry.value.title()} industry training",
                        "Industry networking events",
                        f"Side projects in {insight.industry.value}"
                    ],
                    success_metrics=[
                        f"Complete {insight.industry.value} training",
                        f"Build network in {insight.industry.value}",
                        f"Secure interview in {insight.industry.value}"
                    ]
                )
                recommendations.append(recommendation)
        
        return recommendations[:1]  # Limit to 1 industry recommendation
    
    def _generate_salary_recommendations(self, user_profile: Dict[str, Any], 
                                       competitive_analysis) -> List[PersonalizedRecommendation]:
        """Generate salary optimization recommendations."""
        
        recommendations = []
        
        if competitive_analysis.competitive_score < 70:
            # User needs to improve competitive position
            high_value_skills = ['Machine Learning', 'Cloud Computing', 'DevOps', 'Leadership']
            
            for skill in high_value_skills[:2]:  # Top 2 skills
                recommendation = PersonalizedRecommendation(
                    recommendation_type='salary_optimization',
                    priority='medium',
                    title=f"Develop {skill} for Salary Growth",
                    description=f"Master {skill} to increase competitive position and salary potential",
                    expected_impact="Significant salary increase and market positioning",
                    time_investment="6-9 months",
                    difficulty_level="Medium",
                    resources=[
                        f"{skill} certifications",
                        "Salary negotiation training",
                        "Market research and benchmarking"
                    ],
                    success_metrics=[
                        f"Complete {skill} certification",
                        "Achieve salary increase",
                        "Improve competitive score"
                    ]
                )
                recommendations.append(recommendation)
        
        return recommendations[:1]  # Limit to 1 salary recommendation
    
    def _generate_networking_recommendations(self, user_profile: Dict[str, Any], 
                                           industry_insights: List) -> List[PersonalizedRecommendation]:
        """Generate networking recommendations."""
        
        recommendations = []
        
        # Always recommend networking
        primary_industry = self.trend_analyzer._identify_primary_industry(user_profile)
        
        recommendation = PersonalizedRecommendation(
            recommendation_type='networking',
            priority='low',
            title="Build Professional Network",
            description=f"Expand professional network in {primary_industry.value} industry",
            expected_impact="Better job opportunities and career insights",
            time_investment="Ongoing",
            difficulty_level="Low",
            resources=[
                "LinkedIn networking",
                f"{primary_industry.value.title()} industry conferences",
                "Professional associations"
            ],
            success_metrics=[
                "Connect with 50+ industry professionals",
                "Attend 3+ industry events",
                "Join professional association"
            ]
        )
        recommendations.append(recommendation)
        
        return recommendations
    
    def _generate_education_recommendations(self, user_profile: Dict[str, Any], 
                                          career_progression) -> List[PersonalizedRecommendation]:
        """Generate education recommendations."""
        
        recommendations = []
        
        # Check if user needs advanced education for next stage
        if career_progression.next_stage in [CareerStage.LEADERSHIP, CareerStage.EXECUTIVE]:
            resume_content = user_profile.get('resume_content', '').lower()
            
            if 'master' not in resume_content and 'mba' not in resume_content:
                education_type = "MBA" if career_progression.next_stage == CareerStage.EXECUTIVE else "Master's Degree"
                
                recommendation = PersonalizedRecommendation(
                    recommendation_type='education',
                    priority='medium',
                    title=f"Pursue {education_type}",
                    description=f"Consider {education_type} to enhance career prospects for {career_progression.next_stage.value.replace('_', ' ').title()} level",
                    expected_impact="Long-term career advancement and leadership opportunities",
                    time_investment="1-3 years",
                    difficulty_level="High",
                    resources=[
                        f"{education_type} programs",
                        "Online degree programs",
                        "Professional certifications"
                    ],
                    success_metrics=[
                        f"Complete {education_type}",
                        "Apply new knowledge in role",
                        "Achieve career advancement"
                    ]
                )
                recommendations.append(recommendation)
        
        return recommendations
    
    def _prioritize_recommendations(self, recommendations: List[PersonalizedRecommendation], 
                                  user_profile: Dict[str, Any]) -> List[PersonalizedRecommendation]:
        """Prioritize recommendations based on user profile and impact."""
        
        # Priority weights
        priority_weights = {
            'high': 3,
            'medium': 2,
            'low': 1
        }
        
        # Calculate priority scores
        for recommendation in recommendations:
            base_score = priority_weights.get(recommendation.priority, 1)
            
            # Adjust based on user's current situation
            if recommendation.recommendation_type == 'skill_development':
                # Higher priority if user has limited skills
                user_skills = user_profile.get('skills', [])
                if len(user_skills) < 10:
                    base_score += 1
            
            elif recommendation.recommendation_type == 'career_progression':
                # Higher priority if user is stuck in current stage
                experience_years = self.trend_analyzer._extract_experience_years(user_profile)
                if experience_years > 5:
                    base_score += 1
            
            elif recommendation.recommendation_type == 'salary_optimization':
                # Higher priority if user has low competitive score
                competitive_analysis = self.trend_analyzer.perform_competitive_analysis(user_profile)
                if competitive_analysis.competitive_score < 60:
                    base_score += 1
            
            recommendation.priority_score = base_score
        
        # Sort by priority score (descending)
        recommendations.sort(key=lambda x: x.priority_score, reverse=True)
        
        return recommendations
    
    def create_career_analytics(self, user_profile: Dict[str, Any]) -> CareerAnalytics:
        """
        Create comprehensive career analytics for user.
        
        Args:
            user_profile: User profile data
            
        Returns:
            CareerAnalytics with comprehensive analysis
        """
        console.print("[blue]Creating comprehensive career analytics...[/blue]")
        
        # Get user ID
        user_id = user_profile.get('user_id', user_profile.get('email', 'anonymous'))
        
        # Analyze career progression
        career_progression = self.progression_tracker.analyze_career_progression(user_profile)
        
        # Analyze skill trends
        skill_trends = self.trend_analyzer.analyze_skill_trends(user_profile.get('skills', []))
        
        # Analyze industry insights
        industry_insights = self.trend_analyzer.analyze_industry_trends(user_profile)
        
        # Generate personalized recommendations
        personalized_recommendations = self.generate_recommendations(user_profile)
        
        # Calculate overall career score
        career_score = self._calculate_career_score(
            career_progression, skill_trends, industry_insights, user_profile
        )
        
        # Determine market position
        competitive_analysis = self.trend_analyzer.perform_competitive_analysis(user_profile)
        market_position = competitive_analysis.market_position
        
        # Identify competitive advantages
        competitive_advantages = competitive_analysis.strengths
        
        # Identify areas for improvement
        areas_for_improvement = competitive_analysis.weaknesses
        
        console.print(f"[green]✓ Career analytics complete[/green]")
        console.print(f"[blue]Career Score: {career_score:.1f}/100[/blue]")
        console.print(f"[blue]Market Position: {market_position}[/blue]")
        
        return CareerAnalytics(
            user_id=user_id,
            career_progression=career_progression,
            skill_trends=skill_trends,
            industry_insights=industry_insights,
            personalized_recommendations=personalized_recommendations,
            career_score=career_score,
            market_position=market_position,
            competitive_advantages=competitive_advantages,
            areas_for_improvement=areas_for_improvement
        )
    
    def _calculate_career_score(self, career_progression, skill_trends: List, 
                              industry_insights: List, user_profile: Dict[str, Any]) -> float:
        """Calculate overall career score."""
        
        score = 0.0
        
        # Career progression factor (30%)
        progression_score = career_progression.progression_score * 100
        score += progression_score * 0.30
        
        # Skills factor (25%)
        if skill_trends:
            avg_skill_demand = sum(trend.demand_score for trend in skill_trends) / len(skill_trends)
            skills_score = avg_skill_demand * 100
            score += skills_score * 0.25
        else:
            score += 50 * 0.25  # Default score
        
        # Industry factor (20%)
        if industry_insights:
            avg_growth_rate = sum(insight.growth_rate for insight in industry_insights) / len(industry_insights)
            industry_score = min(avg_growth_rate * 10, 100)  # Scale growth rate
            score += industry_score * 0.20
        else:
            score += 50 * 0.20  # Default score
        
        # Experience factor (15%)
        experience_years = self.trend_analyzer._extract_experience_years(user_profile)
        experience_score = min(experience_years * 5, 100)  # 5 points per year, cap at 100
        score += experience_score * 0.15
        
        # Education factor (10%)
        education_score = self.trend_analyzer._calculate_education_competitiveness(user_profile) * 100
        score += education_score * 0.10
        
        return min(score, 100.0)
