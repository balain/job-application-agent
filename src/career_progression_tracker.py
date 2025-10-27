"""
Career progression tracking and analysis.
"""

import logging
import re
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime, date, timedelta
from pathlib import Path

from rich.console import Console

from .career_analytics_models import (
    CareerStage, CareerProgression, CareerMilestone, SkillCategory,
    PersonalizedRecommendation, CareerAnalytics
)
from .database_manager import db_manager

logger = logging.getLogger(__name__)
console = Console()


class CareerProgressionTracker:
    """Tracks and analyzes career progression."""
    
    def __init__(self):
        self.logger = logger
        
        # Career stage definitions
        self.stage_definitions = {
            CareerStage.ENTRY_LEVEL: {
                'experience_years': (0, 2),
                'key_skills': ['basic_technical', 'communication', 'learning'],
                'typical_titles': ['junior', 'associate', 'trainee', 'intern'],
                'next_stage': CareerStage.MID_LEVEL
            },
            CareerStage.MID_LEVEL: {
                'experience_years': (2, 5),
                'key_skills': ['technical_expertise', 'project_management', 'mentoring'],
                'typical_titles': ['developer', 'analyst', 'specialist', 'coordinator'],
                'next_stage': CareerStage.SENIOR_LEVEL
            },
            CareerStage.SENIOR_LEVEL: {
                'experience_years': (5, 10),
                'key_skills': ['advanced_technical', 'leadership', 'architecture'],
                'typical_titles': ['senior', 'lead', 'principal', 'architect'],
                'next_stage': CareerStage.LEADERSHIP
            },
            CareerStage.LEADERSHIP: {
                'experience_years': (10, 15),
                'key_skills': ['team_leadership', 'strategy', 'management'],
                'typical_titles': ['manager', 'director', 'head', 'vp'],
                'next_stage': CareerStage.EXECUTIVE
            },
            CareerStage.EXECUTIVE: {
                'experience_years': (15, 999),
                'key_skills': ['executive_leadership', 'strategy', 'vision'],
                'typical_titles': ['vp', 'svp', 'cfo', 'ceo', 'president'],
                'next_stage': None
            }
        }
        
        # Skill progression mapping
        self.skill_progression = {
            SkillCategory.TECHNICAL: {
                'entry': ['programming_basics', 'tools_familiarity'],
                'mid': ['advanced_programming', 'system_design'],
                'senior': ['architecture', 'technical_leadership'],
                'leadership': ['technical_strategy', 'innovation'],
                'executive': ['technology_vision', 'digital_transformation']
            },
            SkillCategory.SOFT_SKILLS: {
                'entry': ['communication', 'teamwork'],
                'mid': ['presentation', 'collaboration'],
                'senior': ['mentoring', 'influence'],
                'leadership': ['team_building', 'conflict_resolution'],
                'executive': ['executive_presence', 'stakeholder_management']
            },
            SkillCategory.LEADERSHIP: {
                'entry': ['self_management'],
                'mid': ['project_leadership'],
                'senior': ['team_leadership'],
                'leadership': ['department_leadership'],
                'executive': ['organizational_leadership']
            }
        }
    
    def analyze_career_progression(self, user_profile: Dict[str, Any]) -> CareerProgression:
        """
        Analyze user's career progression and provide recommendations.
        
        Args:
            user_profile: User profile data including experience, skills, etc.
            
        Returns:
            CareerProgression analysis
        """
        console.print("[blue]Analyzing career progression...[/blue]")
        
        # Determine current career stage
        current_stage = self._determine_career_stage(user_profile)
        
        # Determine next stage
        next_stage = self._get_next_stage(current_stage)
        
        # Calculate progression score
        progression_score = self._calculate_progression_score(user_profile, current_stage, next_stage)
        
        # Estimate time to next stage
        time_to_next = self._estimate_time_to_next_stage(user_profile, current_stage, next_stage)
        
        # Identify skill gaps
        skill_gaps = self._identify_skill_gaps(user_profile, current_stage, next_stage)
        
        # Generate recommendations
        recommendations = self._generate_progression_recommendations(user_profile, current_stage, next_stage)
        
        # Create milestones
        milestones = self._create_career_milestones(user_profile, current_stage, next_stage)
        
        console.print(f"[green]✓ Career progression analysis complete[/green]")
        console.print(f"[blue]Current Stage: {current_stage.value.replace('_', ' ').title()}[/blue]")
        console.print(f"[blue]Next Stage: {next_stage.value.replace('_', ' ').title()}[/blue]")
        console.print(f"[blue]Progression Score: {progression_score:.1%}[/blue]")
        
        return CareerProgression(
            current_stage=current_stage,
            next_stage=next_stage,
            progression_score=progression_score,
            time_to_next_stage=time_to_next,
            skill_gaps=skill_gaps,
            recommended_actions=recommendations,
            milestones=milestones
        )
    
    def _determine_career_stage(self, user_profile: Dict[str, Any]) -> CareerStage:
        """Determine user's current career stage based on profile data."""
        
        # Extract experience information
        experience_years = self._extract_experience_years(user_profile)
        current_title = user_profile.get('current_title', '').lower()
        
        # Check title-based indicators first
        for stage, definition in self.stage_definitions.items():
            for title_keyword in definition['typical_titles']:
                if title_keyword in current_title:
                    return stage
        
        # Fall back to experience-based determination
        for stage, definition in self.stage_definitions.items():
            min_years, max_years = definition['experience_years']
            if min_years <= experience_years <= max_years:
                return stage
        
        # Default to entry level if unclear
        return CareerStage.ENTRY_LEVEL
    
    def _extract_experience_years(self, user_profile: Dict[str, Any]) -> float:
        """Extract total years of experience from user profile."""
        
        # Try to get from explicit field
        if 'total_experience_years' in user_profile:
            return float(user_profile['total_experience_years'])
        
        # Extract from resume content if available
        resume_content = user_profile.get('resume_content', '')
        if resume_content:
            return self._parse_experience_from_resume(resume_content)
        
        # Default to 0 if no experience found
        return 0.0
    
    def _parse_experience_from_resume(self, resume_content: str) -> float:
        """Parse years of experience from resume content."""
        
        # Look for years patterns
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
            return max(years_found)  # Take the highest number found
        
        # Count job entries as rough estimate
        job_patterns = [
            r'\d{4}\s*[-–]\s*\d{4}',  # Date ranges
            r'\d{4}\s*[-–]\s*present',  # Current job
            r'january|february|march|april|may|june|july|august|september|october|november|december'
        ]
        
        job_count = 0
        for pattern in job_patterns:
            matches = re.findall(pattern, resume_content, re.IGNORECASE)
            job_count += len(matches)
        
        # Rough estimate: 2-3 years per job
        return min(job_count * 2.5, 20.0)  # Cap at 20 years
    
    def _get_next_stage(self, current_stage: CareerStage) -> CareerStage:
        """Get the next career stage."""
        definition = self.stage_definitions.get(current_stage, {})
        next_stage = definition.get('next_stage')
        
        if next_stage is None:
            # Already at highest stage
            return current_stage
        
        return next_stage
    
    def _calculate_progression_score(self, user_profile: Dict[str, Any], 
                                   current_stage: CareerStage, 
                                   next_stage: CareerStage) -> float:
        """Calculate readiness score for progression to next stage."""
        
        if current_stage == next_stage:
            return 1.0  # Already at highest stage
        
        score = 0.0
        
        # Experience factor (30%)
        experience_years = self._extract_experience_years(user_profile)
        current_min, current_max = self.stage_definitions[current_stage]['experience_years']
        next_min, next_max = self.stage_definitions[next_stage]['experience_years']
        
        if experience_years >= next_min:
            score += 0.3  # Full points for experience
        elif experience_years >= current_max:
            score += 0.2  # Partial points
        else:
            score += 0.1  # Minimal points
        
        # Skills factor (40%)
        skills_score = self._calculate_skills_readiness(user_profile, next_stage)
        score += skills_score * 0.4
        
        # Leadership factor (20%)
        leadership_score = self._calculate_leadership_readiness(user_profile, next_stage)
        score += leadership_score * 0.2
        
        # Education/Certifications factor (10%)
        education_score = self._calculate_education_readiness(user_profile, next_stage)
        score += education_score * 0.1
        
        return min(score, 1.0)
    
    def _calculate_skills_readiness(self, user_profile: Dict[str, Any], 
                                   target_stage: CareerStage) -> float:
        """Calculate skills readiness for target stage."""
        
        user_skills = user_profile.get('skills', [])
        if not user_skills:
            return 0.0
        
        # Get required skills for target stage
        required_skills = []
        for category, progression in self.skill_progression.items():
            stage_key = target_stage.value.replace('_', '')
            if stage_key in progression:
                required_skills.extend(progression[stage_key])
        
        if not required_skills:
            return 0.5  # Default score if no specific requirements
        
        # Calculate match percentage
        matched_skills = 0
        for skill in required_skills:
            if any(skill.lower() in user_skill.lower() for user_skill in user_skills):
                matched_skills += 1
        
        return matched_skills / len(required_skills)
    
    def _calculate_leadership_readiness(self, user_profile: Dict[str, Any], 
                                      target_stage: CareerStage) -> float:
        """Calculate leadership readiness for target stage."""
        
        # Leadership requirements increase with stage
        leadership_requirements = {
            CareerStage.ENTRY_LEVEL: 0.1,
            CareerStage.MID_LEVEL: 0.3,
            CareerStage.SENIOR_LEVEL: 0.6,
            CareerStage.LEADERSHIP: 0.8,
            CareerStage.EXECUTIVE: 1.0
        }
        
        required_level = leadership_requirements.get(target_stage, 0.5)
        
        # Check for leadership indicators
        leadership_indicators = [
            'lead', 'manage', 'direct', 'supervise', 'mentor', 'team',
            'project manager', 'team lead', 'supervisor', 'manager'
        ]
        
        resume_content = user_profile.get('resume_content', '').lower()
        current_title = user_profile.get('current_title', '').lower()
        
        leadership_count = 0
        for indicator in leadership_indicators:
            if indicator in resume_content or indicator in current_title:
                leadership_count += 1
        
        # Calculate current leadership level
        current_level = min(leadership_count / len(leadership_indicators), 1.0)
        
        # Return readiness score
        if current_level >= required_level:
            return 1.0
        else:
            return current_level / required_level
    
    def _calculate_education_readiness(self, user_profile: Dict[str, Any], 
                                     target_stage: CareerStage) -> float:
        """Calculate education readiness for target stage."""
        
        # Education requirements by stage
        education_requirements = {
            CareerStage.ENTRY_LEVEL: 0.3,  # Basic degree helpful
            CareerStage.MID_LEVEL: 0.5,    # Degree or equivalent experience
            CareerStage.SENIOR_LEVEL: 0.7, # Degree + certifications
            CareerStage.LEADERSHIP: 0.8,   # Advanced degree or extensive experience
            CareerStage.EXECUTIVE: 0.9     # Advanced degree preferred
        }
        
        required_level = education_requirements.get(target_stage, 0.5)
        
        # Check for education indicators
        education_indicators = [
            'bachelor', 'master', 'phd', 'mba', 'degree', 'certification',
            'certified', 'diploma', 'university', 'college'
        ]
        
        resume_content = user_profile.get('resume_content', '').lower()
        
        education_count = 0
        for indicator in education_indicators:
            if indicator in resume_content:
                education_count += 1
        
        # Calculate current education level
        current_level = min(education_count / len(education_indicators), 1.0)
        
        # Return readiness score
        if current_level >= required_level:
            return 1.0
        else:
            return current_level / required_level
    
    def _estimate_time_to_next_stage(self, user_profile: Dict[str, Any], 
                                   current_stage: CareerStage, 
                                   next_stage: CareerStage) -> int:
        """Estimate months until ready for next stage."""
        
        if current_stage == next_stage:
            return 0  # Already at highest stage
        
        progression_score = self._calculate_progression_score(user_profile, current_stage, next_stage)
        
        # Base time estimates by stage transition
        base_times = {
            (CareerStage.ENTRY_LEVEL, CareerStage.MID_LEVEL): 24,
            (CareerStage.MID_LEVEL, CareerStage.SENIOR_LEVEL): 36,
            (CareerStage.SENIOR_LEVEL, CareerStage.LEADERSHIP): 48,
            (CareerStage.LEADERSHIP, CareerStage.EXECUTIVE): 60
        }
        
        base_time = base_times.get((current_stage, next_stage), 36)
        
        # Adjust based on progression score
        if progression_score >= 0.8:
            return int(base_time * 0.5)  # Ready soon
        elif progression_score >= 0.6:
            return int(base_time * 0.7)  # On track
        elif progression_score >= 0.4:
            return int(base_time * 1.0)  # Normal timeline
        else:
            return int(base_time * 1.5)  # Needs more work
    
    def _identify_skill_gaps(self, user_profile: Dict[str, Any], 
                           current_stage: CareerStage, 
                           next_stage: CareerStage) -> List[str]:
        """Identify skills needed for next stage."""
        
        if current_stage == next_stage:
            return []  # No gaps if already at highest stage
        
        user_skills = user_profile.get('skills', [])
        skill_gaps = []
        
        # Get required skills for next stage
        required_skills = []
        for category, progression in self.skill_progression.items():
            stage_key = next_stage.value.replace('_', '')
            if stage_key in progression:
                required_skills.extend(progression[stage_key])
        
        # Check for missing skills
        for skill in required_skills:
            if not any(skill.lower() in user_skill.lower() for user_skill in user_skills):
                skill_gaps.append(skill.replace('_', ' ').title())
        
        return skill_gaps[:5]  # Return top 5 gaps
    
    def _generate_progression_recommendations(self, user_profile: Dict[str, Any], 
                                           current_stage: CareerStage, 
                                           next_stage: CareerStage) -> List[str]:
        """Generate actionable recommendations for career progression."""
        
        recommendations = []
        
        if current_stage == next_stage:
            recommendations.append("Continue developing executive leadership skills")
            recommendations.append("Focus on strategic thinking and vision")
            return recommendations
        
        # Stage-specific recommendations
        if next_stage == CareerStage.MID_LEVEL:
            recommendations.extend([
                "Develop deeper technical expertise in your domain",
                "Take on more complex projects and responsibilities",
                "Build strong relationships with colleagues and stakeholders",
                "Consider obtaining relevant certifications"
            ])
        elif next_stage == CareerStage.SENIOR_LEVEL:
            recommendations.extend([
                "Develop technical leadership and mentoring skills",
                "Take ownership of larger projects and initiatives",
                "Build expertise in system design and architecture",
                "Start contributing to technical strategy and planning"
            ])
        elif next_stage == CareerStage.LEADERSHIP:
            recommendations.extend([
                "Develop team leadership and management skills",
                "Learn about business strategy and operations",
                "Build experience in budget and resource management",
                "Develop skills in conflict resolution and team building"
            ])
        elif next_stage == CareerStage.EXECUTIVE:
            recommendations.extend([
                "Develop executive presence and communication skills",
                "Build expertise in organizational strategy and vision",
                "Develop skills in stakeholder management and board relations",
                "Consider pursuing an MBA or executive education program"
            ])
        
        return recommendations[:4]  # Return top 4 recommendations
    
    def _create_career_milestones(self, user_profile: Dict[str, Any], 
                                 current_stage: CareerStage, 
                                 next_stage: CareerStage) -> List[CareerMilestone]:
        """Create career milestones for progression."""
        
        milestones = []
        
        if current_stage == next_stage:
            return milestones
        
        # Create stage-specific milestones
        if next_stage == CareerStage.MID_LEVEL:
            milestones.extend([
                CareerMilestone(
                    milestone_type="skill_development",
                    title="Technical Expertise",
                    description="Develop advanced technical skills in primary domain",
                    status="in_progress",
                    impact_score=0.8
                ),
                CareerMilestone(
                    milestone_type="project_leadership",
                    title="Project Ownership",
                    description="Lead a significant project from start to finish",
                    status="pending",
                    impact_score=0.7
                )
            ])
        elif next_stage == CareerStage.SENIOR_LEVEL:
            milestones.extend([
                CareerMilestone(
                    milestone_type="technical_leadership",
                    title="Technical Leadership",
                    description="Mentor junior team members and lead technical decisions",
                    status="pending",
                    impact_score=0.9
                ),
                CareerMilestone(
                    milestone_type="architecture_expertise",
                    title="System Design",
                    description="Design and implement complex system architectures",
                    status="pending",
                    impact_score=0.8
                )
            ])
        elif next_stage == CareerStage.LEADERSHIP:
            milestones.extend([
                CareerMilestone(
                    milestone_type="team_management",
                    title="Team Leadership",
                    description="Manage a team of 5+ people successfully",
                    status="pending",
                    impact_score=0.9
                ),
                CareerMilestone(
                    milestone_type="business_strategy",
                    title="Strategic Planning",
                    description="Contribute to business strategy and planning",
                    status="pending",
                    impact_score=0.8
                )
            ])
        elif next_stage == CareerStage.EXECUTIVE:
            milestones.extend([
                CareerMilestone(
                    milestone_type="executive_leadership",
                    title="Executive Presence",
                    description="Develop executive communication and leadership skills",
                    status="pending",
                    impact_score=1.0
                ),
                CareerMilestone(
                    milestone_type="organizational_vision",
                    title="Strategic Vision",
                    description="Develop and communicate organizational vision",
                    status="pending",
                    impact_score=0.9
                )
            ])
        
        return milestones
