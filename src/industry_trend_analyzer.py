"""
Industry trend analysis and market insights.
"""

import logging
import re
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime, date
import json

from rich.console import Console

from .career_analytics_models import (
    Industry, IndustryInsight, SkillTrend, TrendDirection, SkillCategory,
    SalaryBenchmark, CompetitiveAnalysis
)

logger = logging.getLogger(__name__)
console = Console()


class IndustryTrendAnalyzer:
    """Analyzes industry trends and market insights."""
    
    def __init__(self):
        self.logger = logger
        
        # Industry-specific data (in a real implementation, this would come from external APIs)
        self.industry_data = {
            Industry.TECHNOLOGY: {
                'growth_rate': 8.5,
                'average_salary_range': {
                    'entry': 65000,
                    'mid': 95000,
                    'senior': 140000,
                    'leadership': 180000,
                    'executive': 250000
                },
                'top_skills': [
                    'Python', 'JavaScript', 'Cloud Computing', 'Machine Learning',
                    'DevOps', 'React', 'Node.js', 'AWS', 'Docker', 'Kubernetes'
                ],
                'trends': [
                    'AI and Machine Learning adoption',
                    'Cloud-first architecture',
                    'Remote work becoming standard',
                    'Cybersecurity focus increasing',
                    'Low-code/no-code platforms growing'
                ],
                'outlook': 'Strong growth expected with continued digital transformation'
            },
            Industry.FINANCE: {
                'growth_rate': 4.2,
                'average_salary_range': {
                    'entry': 55000,
                    'mid': 80000,
                    'senior': 120000,
                    'leadership': 160000,
                    'executive': 220000
                },
                'top_skills': [
                    'Financial Analysis', 'Risk Management', 'Python', 'SQL',
                    'Excel', 'PowerBI', 'Tableau', 'Regulatory Compliance', 'CFA', 'FRM'
                ],
                'trends': [
                    'Fintech disruption',
                    'Regulatory technology (RegTech)',
                    'Sustainable finance focus',
                    'Digital banking transformation',
                    'Cryptocurrency integration'
                ],
                'outlook': 'Moderate growth with focus on digital transformation and compliance'
            },
            Industry.HEALTHCARE: {
                'growth_rate': 6.8,
                'average_salary_range': {
                    'entry': 45000,
                    'mid': 70000,
                    'senior': 100000,
                    'leadership': 130000,
                    'executive': 180000
                },
                'top_skills': [
                    'Healthcare IT', 'Electronic Health Records', 'HIPAA Compliance',
                    'Data Analysis', 'Python', 'SQL', 'Machine Learning', 'Telemedicine'
                ],
                'trends': [
                    'Telemedicine expansion',
                    'AI in diagnostics',
                    'Personalized medicine',
                    'Healthcare data analytics',
                    'Remote patient monitoring'
                ],
                'outlook': 'Strong growth driven by aging population and technology adoption'
            },
            Industry.EDUCATION: {
                'growth_rate': 3.1,
                'average_salary_range': {
                    'entry': 40000,
                    'mid': 55000,
                    'senior': 75000,
                    'leadership': 95000,
                    'executive': 130000
                },
                'top_skills': [
                    'Educational Technology', 'Learning Management Systems',
                    'Data Analysis', 'Curriculum Design', 'Assessment Tools',
                    'Online Learning Platforms', 'Student Information Systems'
                ],
                'trends': [
                    'Online learning acceleration',
                    'Personalized learning platforms',
                    'AI in education',
                    'Virtual and augmented reality',
                    'Competency-based education'
                ],
                'outlook': 'Moderate growth with focus on technology integration and accessibility'
            },
            Industry.MANUFACTURING: {
                'growth_rate': 2.8,
                'average_salary_range': {
                    'entry': 45000,
                    'mid': 65000,
                    'senior': 85000,
                    'leadership': 110000,
                    'executive': 150000
                },
                'top_skills': [
                    'Industrial Automation', 'IoT', 'Robotics', 'Lean Manufacturing',
                    'Six Sigma', 'Supply Chain Management', 'Quality Control',
                    'Manufacturing Execution Systems'
                ],
                'trends': [
                    'Industry 4.0 adoption',
                    'Smart manufacturing',
                    'Sustainable production',
                    'Supply chain resilience',
                    'Automation and robotics'
                ],
                'outlook': 'Steady growth with focus on automation and sustainability'
            }
        }
        
        # Skill trend data
        self.skill_trends = {
            'Python': {'demand': 0.95, 'growth': 15.2, 'saturation': 0.3, 'salary_impact': 0.8},
            'JavaScript': {'demand': 0.92, 'growth': 12.8, 'saturation': 0.4, 'salary_impact': 0.7},
            'Machine Learning': {'demand': 0.88, 'growth': 25.5, 'saturation': 0.2, 'salary_impact': 0.9},
            'Cloud Computing': {'demand': 0.90, 'growth': 18.3, 'saturation': 0.3, 'salary_impact': 0.8},
            'DevOps': {'demand': 0.87, 'growth': 16.7, 'saturation': 0.25, 'salary_impact': 0.85},
            'React': {'demand': 0.85, 'growth': 14.2, 'saturation': 0.35, 'salary_impact': 0.7},
            'AWS': {'demand': 0.88, 'growth': 17.5, 'saturation': 0.3, 'salary_impact': 0.8},
            'Docker': {'demand': 0.82, 'growth': 13.8, 'saturation': 0.4, 'salary_impact': 0.75},
            'Kubernetes': {'demand': 0.80, 'growth': 22.1, 'saturation': 0.2, 'salary_impact': 0.85},
            'SQL': {'demand': 0.90, 'growth': 8.5, 'saturation': 0.5, 'salary_impact': 0.6},
            'Data Analysis': {'demand': 0.85, 'growth': 12.3, 'saturation': 0.4, 'salary_impact': 0.7},
            'Project Management': {'demand': 0.80, 'growth': 6.8, 'saturation': 0.6, 'salary_impact': 0.65},
            'Leadership': {'demand': 0.75, 'growth': 5.2, 'saturation': 0.7, 'salary_impact': 0.8},
            'Communication': {'demand': 0.95, 'growth': 3.5, 'saturation': 0.8, 'salary_impact': 0.5}
        }
    
    def analyze_industry_trends(self, user_profile: Dict[str, Any]) -> List[IndustryInsight]:
        """
        Analyze industry trends relevant to user's profile.
        
        Args:
            user_profile: User profile data
            
        Returns:
            List of industry insights
        """
        console.print("[blue]Analyzing industry trends...[/blue]")
        
        # Determine relevant industries
        relevant_industries = self._identify_relevant_industries(user_profile)
        
        insights = []
        for industry in relevant_industries:
            insight = self._create_industry_insight(industry, user_profile)
            insights.append(insight)
        
        console.print(f"[green]✓ Industry trend analysis complete[/green]")
        console.print(f"[blue]Analyzed {len(insights)} industries[/blue]")
        
        return insights
    
    def analyze_skill_trends(self, user_skills: List[str]) -> List[SkillTrend]:
        """
        Analyze trends for user's skills.
        
        Args:
            user_skills: List of user's skills
            
        Returns:
            List of skill trend analyses
        """
        console.print("[blue]Analyzing skill trends...[/blue]")
        
        skill_trends = []
        for skill in user_skills:
            trend_data = self._get_skill_trend_data(skill)
            if trend_data:
                trend = SkillTrend(
                    skill_name=skill,
                    category=self._categorize_skill(skill),
                    trend_direction=self._determine_trend_direction(trend_data),
                    demand_score=trend_data['demand'],
                    growth_rate=trend_data['growth'],
                    market_saturation=trend_data['saturation'],
                    salary_impact=trend_data['salary_impact']
                )
                skill_trends.append(trend)
        
        console.print(f"[green]✓ Skill trend analysis complete[/green]")
        console.print(f"[blue]Analyzed {len(skill_trends)} skills[/blue]")
        
        return skill_trends
    
    def create_salary_benchmark(self, user_profile: Dict[str, Any]) -> SalaryBenchmark:
        """
        Create salary benchmark for user's profile.
        
        Args:
            user_profile: User profile data
            
        Returns:
            Salary benchmark data
        """
        console.print("[blue]Creating salary benchmark...[/blue]")
        
        # Extract profile information
        position_title = user_profile.get('current_title', 'Software Developer')
        industry = self._identify_primary_industry(user_profile)
        experience_level = self._determine_experience_level(user_profile)
        location = user_profile.get('location', 'United States')
        
        # Get industry-specific salary data
        industry_data = self.industry_data.get(industry, self.industry_data[Industry.TECHNOLOGY])
        salary_range = industry_data['average_salary_range']
        
        # Adjust for experience level
        base_salary = salary_range.get(experience_level, salary_range['mid'])
        
        # Create percentile data
        percentile_data = {
            '25th': base_salary * 0.8,
            '50th': base_salary,
            '75th': base_salary * 1.2,
            '90th': base_salary * 1.4
        }
        
        # Get market trends
        market_trends = industry_data['trends'][:3]  # Top 3 trends
        
        console.print(f"[green]✓ Salary benchmark created[/green]")
        console.print(f"[blue]Position: {position_title}[/blue]")
        console.print(f"[blue]Industry: {industry.value}[/blue]")
        console.print(f"[blue]Median Salary: ${base_salary:,.0f}[/blue]")
        
        return SalaryBenchmark(
            position_title=position_title,
            industry=industry,
            experience_level=experience_level,
            location=location,
            salary_range={
                'min': percentile_data['25th'],
                'max': percentile_data['90th'],
                'median': percentile_data['50th']
            },
            percentile_data=percentile_data,
            market_trends=market_trends
        )
    
    def perform_competitive_analysis(self, user_profile: Dict[str, Any]) -> CompetitiveAnalysis:
        """
        Perform competitive analysis for user's profile.
        
        Args:
            user_profile: User profile data
            
        Returns:
            Competitive analysis results
        """
        console.print("[blue]Performing competitive analysis...[/blue]")
        
        # Analyze competitive position
        competitive_score = self._calculate_competitive_score(user_profile)
        market_position = self._determine_market_position(competitive_score)
        
        # SWOT analysis
        strengths = self._identify_strengths(user_profile)
        weaknesses = self._identify_weaknesses(user_profile)
        opportunities = self._identify_opportunities(user_profile)
        threats = self._identify_threats(user_profile)
        
        # Differentiation strategies
        differentiation_strategies = self._generate_differentiation_strategies(
            user_profile, strengths, weaknesses
        )
        
        console.print(f"[green]✓ Competitive analysis complete[/green]")
        console.print(f"[blue]Competitive Score: {competitive_score:.1f}/100[/blue]")
        console.print(f"[blue]Market Position: {market_position}[/blue]")
        
        return CompetitiveAnalysis(
            user_profile=user_profile,
            market_position=market_position,
            competitive_score=competitive_score,
            strengths=strengths,
            weaknesses=weaknesses,
            opportunities=opportunities,
            threats=threats,
            differentiation_strategy=differentiation_strategies
        )
    
    def _identify_relevant_industries(self, user_profile: Dict[str, Any]) -> List[Industry]:
        """Identify industries relevant to user's profile."""
        
        relevant_industries = []
        resume_content = user_profile.get('resume_content', '').lower()
        current_title = user_profile.get('current_title', '').lower()
        
        # Industry keywords mapping
        industry_keywords = {
            Industry.TECHNOLOGY: ['software', 'developer', 'engineer', 'programming', 'tech', 'it', 'computer'],
            Industry.FINANCE: ['finance', 'banking', 'investment', 'financial', 'analyst', 'trading', 'risk'],
            Industry.HEALTHCARE: ['healthcare', 'medical', 'health', 'hospital', 'clinical', 'pharmaceutical'],
            Industry.EDUCATION: ['education', 'teacher', 'professor', 'academic', 'university', 'school'],
            Industry.MANUFACTURING: ['manufacturing', 'production', 'factory', 'industrial', 'automation'],
            Industry.RETAIL: ['retail', 'sales', 'customer', 'commerce', 'ecommerce', 'marketing'],
            Industry.CONSULTING: ['consulting', 'consultant', 'advisory', 'strategy', 'management'],
            Industry.GOVERNMENT: ['government', 'public', 'federal', 'state', 'municipal', 'policy'],
            Industry.NON_PROFIT: ['nonprofit', 'non-profit', 'charity', 'foundation', 'ngo']
        }
        
        # Check for industry matches
        for industry, keywords in industry_keywords.items():
            for keyword in keywords:
                if keyword in resume_content or keyword in current_title:
                    if industry not in relevant_industries:
                        relevant_industries.append(industry)
                    break
        
        # Default to technology if no specific industry found
        if not relevant_industries:
            relevant_industries = [Industry.TECHNOLOGY]
        
        return relevant_industries[:3]  # Return top 3 relevant industries
    
    def _create_industry_insight(self, industry: Industry, user_profile: Dict[str, Any]) -> IndustryInsight:
        """Create industry insight for specific industry."""
        
        industry_data = self.industry_data.get(industry, self.industry_data[Industry.TECHNOLOGY])
        
        return IndustryInsight(
            industry=industry,
            growth_rate=industry_data['growth_rate'],
            average_salary_range=industry_data['average_salary_range'],
            top_skills=industry_data['top_skills'],
            job_market_trends=industry_data['trends'],
            future_outlook=industry_data['outlook']
        )
    
    def _get_skill_trend_data(self, skill: str) -> Optional[Dict[str, float]]:
        """Get trend data for specific skill."""
        
        # Try exact match first
        skill_lower = skill.lower()
        for trend_skill, data in self.skill_trends.items():
            if trend_skill.lower() == skill_lower:
                return data
        
        # Try partial match
        for trend_skill, data in self.skill_trends.items():
            if trend_skill.lower() in skill_lower or skill_lower in trend_skill.lower():
                return data
        
        # Default trend data for unknown skills
        return {
            'demand': 0.6,
            'growth': 5.0,
            'saturation': 0.5,
            'salary_impact': 0.5
        }
    
    def _categorize_skill(self, skill: str) -> SkillCategory:
        """Categorize skill into skill category."""
        
        skill_lower = skill.lower()
        
        # Technical skills
        technical_keywords = ['python', 'javascript', 'java', 'sql', 'programming', 'coding', 'development']
        if any(keyword in skill_lower for keyword in technical_keywords):
            return SkillCategory.TECHNICAL
        
        # Soft skills
        soft_keywords = ['communication', 'teamwork', 'presentation', 'collaboration']
        if any(keyword in skill_lower for keyword in soft_keywords):
            return SkillCategory.SOFT_SKILLS
        
        # Leadership skills
        leadership_keywords = ['management', 'lead', 'supervise', 'mentor', 'direct', 'leadership']
        if any(keyword in skill_lower for keyword in leadership_keywords):
            return SkillCategory.LEADERSHIP
        
        # Tools and technologies
        tools_keywords = ['aws', 'docker', 'kubernetes', 'git', 'jenkins', 'excel', 'powerbi']
        if any(keyword in skill_lower for keyword in tools_keywords):
            return SkillCategory.TOOLS_TECHNOLOGIES
        
        # Default to technical
        return SkillCategory.TECHNICAL
    
    def _determine_trend_direction(self, trend_data: Dict[str, float]) -> TrendDirection:
        """Determine trend direction based on data."""
        
        growth_rate = trend_data['growth']
        demand_score = trend_data['demand']
        
        if growth_rate > 15 and demand_score > 0.8:
            return TrendDirection.RISING
        elif growth_rate > 20:
            return TrendDirection.EMERGING
        elif growth_rate < 5 or demand_score < 0.6:
            return TrendDirection.DECLINING
        else:
            return TrendDirection.STABLE
    
    def _identify_primary_industry(self, user_profile: Dict[str, Any]) -> Industry:
        """Identify user's primary industry."""
        
        relevant_industries = self._identify_relevant_industries(user_profile)
        return relevant_industries[0] if relevant_industries else Industry.TECHNOLOGY
    
    def _determine_experience_level(self, user_profile: Dict[str, Any]) -> str:
        """Determine user's experience level."""
        
        experience_years = self._extract_experience_years(user_profile)
        
        if experience_years < 2:
            return 'entry'
        elif experience_years < 5:
            return 'mid'
        elif experience_years < 10:
            return 'senior'
        elif experience_years < 15:
            return 'leadership'
        else:
            return 'executive'
    
    def _extract_experience_years(self, user_profile: Dict[str, Any]) -> float:
        """Extract years of experience from user profile."""
        
        if 'total_experience_years' in user_profile:
            return float(user_profile['total_experience_years'])
        
        resume_content = user_profile.get('resume_content', '')
        if resume_content:
            return self._parse_experience_from_resume(resume_content)
        
        return 0.0
    
    def _parse_experience_from_resume(self, resume_content: str) -> float:
        """Parse years of experience from resume content."""
        
        years_patterns = [
            r'(\d+)\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)',
            r'(?:experience|exp)[:\s]*(\d+)\s*(?:years?|yrs?)',
            r'(\d+)\+?\s*(?:years?|yrs?)'
        ]
        
        years_found = []
        for pattern in years_patterns:
            matches = re.findall(pattern, resume_content, re.IGNORECASE)
            years_found.extend([int(match) for match in matches if match.isdigit()])
        
        if years_found:
            return max(years_found)
        
        return 0.0
    
    def _calculate_competitive_score(self, user_profile: Dict[str, Any]) -> float:
        """Calculate competitive score for user."""
        
        score = 0.0
        
        # Experience factor (25%)
        experience_years = self._extract_experience_years(user_profile)
        experience_score = min(experience_years / 10.0, 1.0)  # Cap at 10 years
        score += experience_score * 0.25
        
        # Skills factor (30%)
        user_skills = user_profile.get('skills', [])
        skills_score = self._calculate_skills_competitiveness(user_skills)
        score += skills_score * 0.30
        
        # Education factor (20%)
        education_score = self._calculate_education_competitiveness(user_profile)
        score += education_score * 0.20
        
        # Leadership factor (15%)
        leadership_score = self._calculate_leadership_competitiveness(user_profile)
        score += leadership_score * 0.15
        
        # Industry relevance factor (10%)
        industry_score = self._calculate_industry_relevance(user_profile)
        score += industry_score * 0.10
        
        return min(score * 100, 100.0)
    
    def _calculate_skills_competitiveness(self, user_skills: List[str]) -> float:
        """Calculate skills competitiveness score."""
        
        if not user_skills:
            return 0.0
        
        # Get trend data for user skills
        skill_scores = []
        for skill in user_skills:
            trend_data = self._get_skill_trend_data(skill)
            if trend_data:
                # Weight by demand and growth
                skill_score = (trend_data['demand'] + trend_data['growth'] / 100) / 2
                skill_scores.append(skill_score)
        
        if not skill_scores:
            return 0.5  # Default score
        
        return sum(skill_scores) / len(skill_scores)
    
    def _calculate_education_competitiveness(self, user_profile: Dict[str, Any]) -> float:
        """Calculate education competitiveness score."""
        
        resume_content = user_profile.get('resume_content', '').lower()
        
        education_score = 0.0
        
        # Degree level scoring
        if 'phd' in resume_content or 'doctorate' in resume_content:
            education_score += 0.4
        elif 'master' in resume_content or 'mba' in resume_content:
            education_score += 0.3
        elif 'bachelor' in resume_content or 'degree' in resume_content:
            education_score += 0.2
        
        # Certification scoring
        cert_keywords = ['certified', 'certification', 'certificate', 'license']
        cert_count = sum(1 for keyword in cert_keywords if keyword in resume_content)
        education_score += min(cert_count * 0.1, 0.3)
        
        return min(education_score, 1.0)
    
    def _calculate_leadership_competitiveness(self, user_profile: Dict[str, Any]) -> float:
        """Calculate leadership competitiveness score."""
        
        resume_content = user_profile.get('resume_content', '').lower()
        current_title = user_profile.get('current_title', '').lower()
        
        leadership_score = 0.0
        
        # Title-based scoring
        leadership_titles = ['manager', 'director', 'lead', 'head', 'vp', 'ceo', 'president']
        for title in leadership_titles:
            if title in current_title:
                leadership_score += 0.3
                break
        
        # Experience-based scoring
        leadership_experience = ['managed', 'led', 'directed', 'supervised', 'mentored']
        exp_count = sum(1 for exp in leadership_experience if exp in resume_content)
        leadership_score += min(exp_count * 0.1, 0.4)
        
        return min(leadership_score, 1.0)
    
    def _calculate_industry_relevance(self, user_profile: Dict[str, Any]) -> float:
        """Calculate industry relevance score."""
        
        # This is a simplified calculation
        # In a real implementation, this would be more sophisticated
        return 0.8  # Default high relevance
    
    def _determine_market_position(self, competitive_score: float) -> str:
        """Determine market position based on competitive score."""
        
        if competitive_score >= 85:
            return "Top Performer"
        elif competitive_score >= 70:
            return "Strong Competitor"
        elif competitive_score >= 55:
            return "Average Competitor"
        elif competitive_score >= 40:
            return "Below Average"
        else:
            return "Needs Improvement"
    
    def _identify_strengths(self, user_profile: Dict[str, Any]) -> List[str]:
        """Identify user's competitive strengths."""
        
        strengths = []
        
        # Experience strength
        experience_years = self._extract_experience_years(user_profile)
        if experience_years >= 5:
            strengths.append(f"Strong experience ({experience_years:.1f} years)")
        
        # Skills strength
        user_skills = user_profile.get('skills', [])
        if len(user_skills) >= 10:
            strengths.append(f"Broad skill set ({len(user_skills)} skills)")
        
        # Education strength
        resume_content = user_profile.get('resume_content', '').lower()
        if 'master' in resume_content or 'mba' in resume_content:
            strengths.append("Advanced degree")
        
        # Leadership strength
        if any(word in resume_content for word in ['managed', 'led', 'directed']):
            strengths.append("Leadership experience")
        
        return strengths[:5]  # Return top 5 strengths
    
    def _identify_weaknesses(self, user_profile: Dict[str, Any]) -> List[str]:
        """Identify user's competitive weaknesses."""
        
        weaknesses = []
        
        # Experience weakness
        experience_years = self._extract_experience_years(user_profile)
        if experience_years < 2:
            weaknesses.append("Limited experience")
        
        # Skills weakness
        user_skills = user_profile.get('skills', [])
        if len(user_skills) < 5:
            weaknesses.append("Limited skill diversity")
        
        # Education weakness
        resume_content = user_profile.get('resume_content', '').lower()
        if 'degree' not in resume_content and 'certification' not in resume_content:
            weaknesses.append("No formal education/certification")
        
        return weaknesses[:5]  # Return top 5 weaknesses
    
    def _identify_opportunities(self, user_profile: Dict[str, Any]) -> List[str]:
        """Identify market opportunities for user."""
        
        opportunities = []
        
        # Industry growth opportunities
        industry = self._identify_primary_industry(user_profile)
        industry_data = self.industry_data.get(industry, self.industry_data[Industry.TECHNOLOGY])
        
        if industry_data['growth_rate'] > 5:
            opportunities.append(f"Growing industry ({industry_data['growth_rate']}% growth)")
        
        # Skill opportunities
        user_skills = user_profile.get('skills', [])
        trending_skills = ['Machine Learning', 'Cloud Computing', 'DevOps', 'AI']
        
        for skill in trending_skills:
            if not any(skill.lower() in user_skill.lower() for user_skill in user_skills):
                opportunities.append(f"High-demand skill: {skill}")
        
        return opportunities[:5]  # Return top 5 opportunities
    
    def _identify_threats(self, user_profile: Dict[str, Any]) -> List[str]:
        """Identify market threats for user."""
        
        threats = []
        
        # Automation threats
        resume_content = user_profile.get('resume_content', '').lower()
        if 'manual' in resume_content or 'routine' in resume_content:
            threats.append("Automation risk")
        
        # Skill obsolescence
        user_skills = user_profile.get('skills', [])
        legacy_skills = ['COBOL', 'Fortran', 'VB6', 'Flash']
        
        for skill in legacy_skills:
            if any(skill.lower() in user_skill.lower() for user_skill in user_skills):
                threats.append(f"Legacy skill: {skill}")
        
        # Market saturation
        threats.append("High competition in job market")
        
        return threats[:5]  # Return top 5 threats
    
    def _generate_differentiation_strategies(self, user_profile: Dict[str, Any], 
                                          strengths: List[str], 
                                          weaknesses: List[str]) -> List[str]:
        """Generate differentiation strategies."""
        
        strategies = []
        
        # Leverage strengths
        if "Strong experience" in str(strengths):
            strategies.append("Emphasize depth of experience in applications")
        
        if "Broad skill set" in str(strengths):
            strategies.append("Highlight versatility and adaptability")
        
        # Address weaknesses
        if "Limited experience" in str(weaknesses):
            strategies.append("Focus on projects and achievements over years")
        
        if "Limited skill diversity" in str(weaknesses):
            strategies.append("Develop expertise in emerging technologies")
        
        # General strategies
        strategies.extend([
            "Build personal brand and thought leadership",
            "Develop unique combination of skills",
            "Focus on specific industry vertical"
        ])
        
        return strategies[:5]  # Return top 5 strategies
