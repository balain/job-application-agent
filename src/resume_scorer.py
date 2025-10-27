"""
Resume scoring system for comprehensive evaluation.
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, date
import re

from rich.console import Console

from .ats_models import ResumeScore, ATSCompatibilityReport, SectionScore
from .ats_analyzer import ATSAnalyzer

logger = logging.getLogger(__name__)
console = Console()


class ResumeScorer:
    """Comprehensive resume scoring system."""
    
    def __init__(self):
        self.logger = logger
        self.ats_analyzer = ATSAnalyzer()
        
        # Scoring weights for different components
        self.scoring_weights = {
            'ats_compatibility': 0.25,
            'content_quality': 0.20,
            'formatting': 0.15,
            'keyword_optimization': 0.15,
            'experience_relevance': 0.15,
            'skills_match': 0.10
        }
        
        # Experience scoring criteria
        self.experience_criteria = {
            'years_experience': 0.3,
            'leadership_roles': 0.2,
            'quantified_achievements': 0.2,
            'relevant_industries': 0.15,
            'career_progression': 0.15
        }
        
        # Skills scoring criteria
        self.skills_criteria = {
            'technical_skills': 0.4,
            'soft_skills': 0.2,
            'certifications': 0.2,
            'tools_technologies': 0.2
        }
    
    def score_resume(
        self, 
        resume_content: str, 
        job_description: str = "",
        resume_path: str = ""
    ) -> ResumeScore:
        """
        Calculate comprehensive resume score.
        
        Args:
            resume_content: Resume text content
            job_description: Job description for relevance scoring
            resume_path: Path to resume file (for ATS analysis)
            
        Returns:
            ResumeScore with detailed scoring breakdown
        """
        console.print("[blue]Calculating comprehensive resume score...[/blue]")
        
        # ATS Compatibility Score
        ats_score = self._calculate_ats_score(resume_path or resume_content)
        
        # Content Quality Score
        content_score = self._calculate_content_score(resume_content)
        
        # Formatting Score
        formatting_score = self._calculate_formatting_score(resume_content)
        
        # Keyword Optimization Score
        keyword_score = self._calculate_keyword_score(resume_content, job_description)
        
        # Experience Relevance Score
        experience_score = self._calculate_experience_score(resume_content, job_description)
        
        # Skills Match Score
        skills_score = self._calculate_skills_score(resume_content, job_description)
        
        # Calculate total weighted score
        total_score = (
            ats_score * self.scoring_weights['ats_compatibility'] +
            content_score * self.scoring_weights['content_quality'] +
            formatting_score * self.scoring_weights['formatting'] +
            keyword_score * self.scoring_weights['keyword_optimization'] +
            experience_score * self.scoring_weights['experience_relevance'] +
            skills_score * self.scoring_weights['skills_match']
        )
        
        console.print(f"[green]✓ Resume scoring complete - Total Score: {total_score:.1f}/100[/green]")
        
        return ResumeScore(
            total_score=total_score,
            ats_score=ats_score,
            content_score=content_score,
            formatting_score=formatting_score,
            keyword_score=keyword_score,
            experience_score=experience_score,
            skills_score=skills_score
        )
    
    def _calculate_ats_score(self, resume_input: str) -> float:
        """Calculate ATS compatibility score."""
        try:
            if resume_input.endswith(('.pdf', '.docx', '.doc', '.txt')):
                # File path provided
                optimization = self.ats_analyzer.analyze_resume(resume_input)
                return optimization.ats_compatibility.overall_score * 100
            else:
                # Content provided - basic ATS analysis
                return self._basic_ats_analysis(resume_input) * 100
        except Exception as e:
            self.logger.error(f"Error calculating ATS score: {e}")
            return 50.0  # Default score on error
    
    def _basic_ats_analysis(self, content: str) -> float:
        """Basic ATS analysis for text content."""
        score = 1.0
        
        # Check for problematic elements
        problematic_patterns = [
            r'<table>', r'<img>', r'<div>', r'<span>',
            r'header\s*:', r'footer\s*:', r'page\s*number'
        ]
        
        for pattern in problematic_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                score -= 0.2
        
        # Check for proper formatting
        lines = content.split('\n')
        if len(lines) < 10:
            score -= 0.3  # Too short
        
        # Check for section headers
        section_headers = sum(1 for line in lines if re.match(r'^[A-Z][A-Z\s]+:$', line.strip()))
        if section_headers < 3:
            score -= 0.2
        
        return max(0.0, score)
    
    def _calculate_content_score(self, content: str) -> float:
        """Calculate content quality score."""
        score = 0.0
        
        # Length check
        word_count = len(content.split())
        if word_count >= 300:
            score += 20
        elif word_count >= 200:
            score += 15
        elif word_count >= 100:
            score += 10
        
        # Essential sections check
        essential_sections = ['experience', 'education', 'skills']
        found_sections = 0
        
        for section in essential_sections:
            if re.search(section, content, re.IGNORECASE):
                found_sections += 1
        
        score += (found_sections / len(essential_sections)) * 30
        
        # Contact information check
        contact_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # Phone
        ]
        
        contact_found = sum(1 for pattern in contact_patterns if re.search(pattern, content))
        score += min(contact_found * 15, 30)  # Max 30 points for contact info
        
        # Action verbs check
        action_verbs = ['managed', 'developed', 'created', 'implemented', 'led', 'designed',
                       'analyzed', 'improved', 'increased', 'reduced', 'achieved', 'delivered']
        
        action_verb_count = sum(1 for verb in action_verbs if verb in content.lower())
        score += min(action_verb_count * 2, 20)  # Max 20 points for action verbs
        
        return min(score, 100.0)
    
    def _calculate_formatting_score(self, content: str) -> float:
        """Calculate formatting score."""
        score = 100.0
        
        lines = content.split('\n')
        
        # Check for consistent formatting
        if len(lines) < 5:
            score -= 30  # Too short
        
        # Check for proper spacing
        empty_lines = sum(1 for line in lines if not line.strip())
        if empty_lines > len(lines) * 0.3:
            score -= 20  # Too much whitespace
        
        # Check for section headers
        section_headers = sum(1 for line in lines if re.match(r'^[A-Z][A-Z\s]+:$', line.strip()))
        if section_headers < 3:
            score -= 25  # Not enough clear sections
        
        # Check for bullet points consistency
        bullet_lines = sum(1 for line in lines if re.match(r'^\s*[-•*]\s+', line))
        if bullet_lines > 0:
            # Check consistency of bullet styles
            bullet_styles = set()
            for line in lines:
                bullet_match = re.match(r'^\s*([-•*])\s+', line)
                if bullet_match:
                    bullet_styles.add(bullet_match.group(1))
            
            if len(bullet_styles) > 1:
                score -= 15  # Inconsistent bullet styles
        
        # Check for proper capitalization
        title_case_lines = sum(1 for line in lines if re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+', line.strip()))
        if title_case_lines < 2:
            score -= 10  # Not enough proper capitalization
        
        return max(score, 0.0)
    
    def _calculate_keyword_score(self, content: str, job_description: str) -> float:
        """Calculate keyword optimization score."""
        if not job_description:
            return 70.0  # Default score when no job description provided
        
        # Extract keywords from job description
        job_keywords = self._extract_keywords(job_description)
        resume_keywords = self._extract_keywords(content)
        
        if not job_keywords:
            return 70.0
        
        # Calculate keyword match percentage
        matched_keywords = job_keywords.intersection(resume_keywords)
        match_percentage = len(matched_keywords) / len(job_keywords)
        
        # Score based on match percentage
        if match_percentage >= 0.8:
            return 100.0
        elif match_percentage >= 0.6:
            return 85.0
        elif match_percentage >= 0.4:
            return 70.0
        elif match_percentage >= 0.2:
            return 55.0
        else:
            return 40.0
    
    def _calculate_experience_score(self, content: str, job_description: str) -> float:
        """Calculate experience relevance score."""
        score = 0.0
        
        # Years of experience
        years_score = self._calculate_years_experience(content)
        score += years_score * self.experience_criteria['years_experience']
        
        # Leadership roles
        leadership_score = self._calculate_leadership_roles(content)
        score += leadership_score * self.experience_criteria['leadership_roles']
        
        # Quantified achievements
        achievements_score = self._calculate_quantified_achievements(content)
        score += achievements_score * self.experience_criteria['quantified_achievements']
        
        # Relevant industries
        industry_score = self._calculate_industry_relevance(content, job_description)
        score += industry_score * self.experience_criteria['relevant_industries']
        
        # Career progression
        progression_score = self._calculate_career_progression(content)
        score += progression_score * self.experience_criteria['career_progression']
        
        return min(score * 100, 100.0)
    
    def _calculate_skills_score(self, content: str, job_description: str) -> float:
        """Calculate skills match score."""
        score = 0.0
        
        # Technical skills
        technical_score = self._calculate_technical_skills(content, job_description)
        score += technical_score * self.skills_criteria['technical_skills']
        
        # Soft skills
        soft_skills_score = self._calculate_soft_skills(content, job_description)
        score += soft_skills_score * self.skills_criteria['soft_skills']
        
        # Certifications
        cert_score = self._calculate_certifications(content)
        score += cert_score * self.skills_criteria['certifications']
        
        # Tools and technologies
        tools_score = self._calculate_tools_technologies(content, job_description)
        score += tools_score * self.skills_criteria['tools_technologies']
        
        return min(score * 100, 100.0)
    
    def _extract_keywords(self, text: str) -> set:
        """Extract relevant keywords from text."""
        # Simple keyword extraction
        words = re.findall(r'\b[A-Za-z]{3,}\b', text.lower())
        
        # Filter out common words
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does',
            'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this',
            'that', 'these', 'those', 'our', 'their', 'your', 'my', 'me', 'you', 'us',
            'them', 'him', 'her', 'it', 'we', 'they', 'he', 'she', 'i'
        }
        
        keywords = {word for word in words if word not in stop_words and len(word) > 3}
        return keywords
    
    def _calculate_years_experience(self, content: str) -> float:
        """Calculate years of experience score."""
        # Look for years patterns
        years_patterns = [
            r'(\d+)\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)',
            r'(?:experience|exp)[:\s]*(\d+)\s*(?:years?|yrs?)',
            r'(\d+)\+?\s*(?:years?|yrs?)'
        ]
        
        years_found = []
        for pattern in years_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            years_found.extend([int(match) for match in matches if match.isdigit()])
        
        if not years_found:
            return 0.3  # Default score if no years found
        
        max_years = max(years_found)
        
        # Score based on years of experience
        if max_years >= 10:
            return 1.0
        elif max_years >= 7:
            return 0.9
        elif max_years >= 5:
            return 0.8
        elif max_years >= 3:
            return 0.7
        elif max_years >= 2:
            return 0.6
        elif max_years >= 1:
            return 0.5
        else:
            return 0.3
    
    def _calculate_leadership_roles(self, content: str) -> float:
        """Calculate leadership roles score."""
        leadership_keywords = [
            'manager', 'director', 'lead', 'senior', 'principal', 'head', 'chief',
            'supervisor', 'team lead', 'project manager', 'coordinator', 'administrator'
        ]
        
        leadership_count = sum(1 for keyword in leadership_keywords 
                              if re.search(keyword, content, re.IGNORECASE))
        
        if leadership_count >= 3:
            return 1.0
        elif leadership_count >= 2:
            return 0.8
        elif leadership_count >= 1:
            return 0.6
        else:
            return 0.3
    
    def _calculate_quantified_achievements(self, content: str) -> float:
        """Calculate quantified achievements score."""
        quantified_patterns = [
            r'\d+%',  # Percentages
            r'\$\d+',  # Money amounts
            r'\d+\+',  # Numbers with plus
            r'\d+x',  # Multipliers
            r'\d+\s*(?:years?|months?|days?)',  # Time periods
            r'\d+\s*(?:people|employees|users|customers)',  # People counts
        ]
        
        achievement_count = sum(1 for pattern in quantified_patterns 
                               if re.search(pattern, content))
        
        if achievement_count >= 5:
            return 1.0
        elif achievement_count >= 3:
            return 0.8
        elif achievement_count >= 2:
            return 0.6
        elif achievement_count >= 1:
            return 0.4
        else:
            return 0.2
    
    def _calculate_industry_relevance(self, content: str, job_description: str) -> float:
        """Calculate industry relevance score."""
        if not job_description:
            return 0.5  # Default score
        
        # Extract industry keywords from job description
        job_keywords = self._extract_keywords(job_description)
        resume_keywords = self._extract_keywords(content)
        
        # Calculate overlap
        overlap = job_keywords.intersection(resume_keywords)
        
        if len(job_keywords) == 0:
            return 0.5
        
        relevance_ratio = len(overlap) / len(job_keywords)
        
        if relevance_ratio >= 0.6:
            return 1.0
        elif relevance_ratio >= 0.4:
            return 0.8
        elif relevance_ratio >= 0.2:
            return 0.6
        else:
            return 0.3
    
    def _calculate_career_progression(self, content: str) -> float:
        """Calculate career progression score."""
        # Look for progression indicators
        progression_keywords = [
            'promoted', 'advanced', 'increased', 'grew', 'expanded',
            'senior', 'lead', 'principal', 'director', 'manager'
        ]
        
        progression_count = sum(1 for keyword in progression_keywords 
                               if re.search(keyword, content, re.IGNORECASE))
        
        if progression_count >= 3:
            return 1.0
        elif progression_count >= 2:
            return 0.8
        elif progression_count >= 1:
            return 0.6
        else:
            return 0.4
    
    def _calculate_technical_skills(self, content: str, job_description: str) -> float:
        """Calculate technical skills score."""
        # Common technical skills
        technical_skills = [
            'python', 'java', 'javascript', 'sql', 'html', 'css', 'react', 'angular',
            'node', 'aws', 'azure', 'docker', 'kubernetes', 'git', 'linux', 'unix',
            'machine learning', 'ai', 'data analysis', 'statistics', 'excel', 'powerbi',
            'tableau', 'salesforce', 'crm', 'erp', 'agile', 'scrum', 'devops'
        ]
        
        if job_description:
            job_keywords = self._extract_keywords(job_description)
            technical_job_skills = {skill for skill in technical_skills 
                                   if skill in job_keywords}
        else:
            technical_job_skills = set(technical_skills)
        
        resume_skills = {skill for skill in technical_skills 
                        if re.search(skill, content, re.IGNORECASE)}
        
        if not technical_job_skills:
            return 0.5  # Default score
        
        match_ratio = len(resume_skills.intersection(technical_job_skills)) / len(technical_job_skills)
        
        if match_ratio >= 0.8:
            return 1.0
        elif match_ratio >= 0.6:
            return 0.8
        elif match_ratio >= 0.4:
            return 0.6
        elif match_ratio >= 0.2:
            return 0.4
        else:
            return 0.2
    
    def _calculate_soft_skills(self, content: str, job_description: str) -> float:
        """Calculate soft skills score."""
        soft_skills = [
            'communication', 'leadership', 'teamwork', 'problem solving', 'analytical',
            'creative', 'innovative', 'collaborative', 'adaptable', 'flexible',
            'organized', 'detail oriented', 'time management', 'project management'
        ]
        
        resume_soft_skills = {skill for skill in soft_skills 
                             if re.search(skill, content, re.IGNORECASE)}
        
        # Score based on number of soft skills mentioned
        if len(resume_soft_skills) >= 5:
            return 1.0
        elif len(resume_soft_skills) >= 3:
            return 0.8
        elif len(resume_soft_skills) >= 2:
            return 0.6
        elif len(resume_soft_skills) >= 1:
            return 0.4
        else:
            return 0.2
    
    def _calculate_certifications(self, content: str) -> float:
        """Calculate certifications score."""
        cert_keywords = [
            'certified', 'certification', 'certificate', 'license', 'credential',
            'pmp', 'cissp', 'aws', 'azure', 'google', 'microsoft', 'cisco',
            'comptia', 'itil', 'scrum', 'agile', 'six sigma'
        ]
        
        cert_count = sum(1 for keyword in cert_keywords 
                        if re.search(keyword, content, re.IGNORECASE))
        
        if cert_count >= 3:
            return 1.0
        elif cert_count >= 2:
            return 0.8
        elif cert_count >= 1:
            return 0.6
        else:
            return 0.3
    
    def _calculate_tools_technologies(self, content: str, job_description: str) -> float:
        """Calculate tools and technologies score."""
        tools = [
            'excel', 'powerpoint', 'word', 'outlook', 'sharepoint', 'teams',
            'slack', 'zoom', 'trello', 'asana', 'jira', 'confluence',
            'salesforce', 'hubspot', 'mailchimp', 'google analytics',
            'adobe', 'photoshop', 'illustrator', 'figma', 'sketch'
        ]
        
        resume_tools = {tool for tool in tools 
                       if re.search(tool, content, re.IGNORECASE)}
        
        if len(resume_tools) >= 5:
            return 1.0
        elif len(resume_tools) >= 3:
            return 0.8
        elif len(resume_tools) >= 2:
            return 0.6
        elif len(resume_tools) >= 1:
            return 0.4
        else:
            return 0.2
