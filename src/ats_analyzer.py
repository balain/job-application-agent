"""
ATS (Applicant Tracking System) compatibility analyzer.
"""

import re
import logging
from typing import List, Dict, Set, Tuple, Optional
from pathlib import Path

from rich.console import Console

from .ats_models import (
    ATSCompatibilityReport, ATSIssue, IssueSeverity, ATSCompatibilityLevel,
    KeywordMatch, SectionScore, ResumeOptimization
)
from .file_parser import ResumeFileParser

logger = logging.getLogger(__name__)
console = Console()


class ATSAnalyzer:
    """Analyzes resume compatibility with Applicant Tracking Systems."""
    
    def __init__(self):
        self.logger = logger
        self.file_parser = ResumeFileParser()
        
        # Common ATS-problematic elements
        self.problematic_elements = {
            'headers_footers': [
                r'header\s*:', r'footer\s*:', r'page\s*number',
                r'confidential', r'proprietary'
            ],
            'tables': [r'<table>', r'<tr>', r'<td>', r'<th>'],
            'images': [r'<img>', r'<image>', r'\.jpg', r'\.png', r'\.gif'],
            'columns': [r'column\s*:', r'two\s*column', r'multi\s*column'],
            'text_boxes': [r'text\s*box', r'textbox', r'<div>'],
            'special_chars': [r'[^\x00-\x7F]', r'[^\w\s\.,;:!?\-\(\)]'],
            'fonts': [r'font\s*:', r'font-family', r'font-size']
        }
        
        # Common resume sections
        self.resume_sections = {
            'contact': [r'contact\s*info', r'personal\s*info', r'address', r'phone', r'email'],
            'summary': [r'summary', r'profile', r'objective', r'about'],
            'experience': [r'experience', r'work\s*history', r'employment', r'career'],
            'education': [r'education', r'academic', r'degree', r'university', r'college'],
            'skills': [r'skills', r'technical\s*skills', r'competencies', r'expertise'],
            'certifications': [r'certification', r'certificate', r'license', r'credential'],
            'projects': [r'project', r'portfolio', r'work\s*sample'],
            'awards': [r'award', r'honor', r'recognition', r'achievement']
        }
    
    def analyze_resume(self, resume_path: str, job_description: str = "") -> ResumeOptimization:
        """
        Analyze resume for ATS compatibility and provide optimization recommendations.
        
        Args:
            resume_path: Path to the resume file
            job_description: Optional job description for keyword matching
            
        Returns:
            ResumeOptimization with analysis results and recommendations
        """
        console.print(f"[blue]Analyzing resume: {resume_path}[/blue]")
        
        # Parse the resume file
        parse_result = self.file_parser.parse_file(resume_path)
        
        if not parse_result.parse_success:
            console.print(f"[red]Failed to parse resume: {parse_result.error_message}[/red]")
            # Return minimal optimization with error
            return ResumeOptimization(
                priority_fixes=[f"File parsing error: {parse_result.error_message}"],
                ats_compatibility=ATSCompatibilityReport(
                    overall_score=0.0,
                    compatibility_level=ATSCompatibilityLevel.POOR,
                    formatting_score=0.0,
                    content_score=0.0,
                    keyword_score=0.0
                )
            )
        
        resume_content = parse_result.content
        
        # Perform ATS compatibility analysis
        ats_report = self._analyze_ats_compatibility(resume_content)
        
        # Generate optimization recommendations
        optimization = self._generate_optimization_recommendations(
            resume_content, ats_report, job_description
        )
        
        console.print(f"[green]✓ Resume analysis complete[/green]")
        console.print(f"[blue]Overall ATS Score: {ats_report.overall_score:.1%}[/blue]")
        
        return optimization
    
    def _analyze_ats_compatibility(self, resume_content: str) -> ATSCompatibilityReport:
        """Analyze ATS compatibility of resume content."""
        
        # Check for problematic elements
        issues = self._check_problematic_elements(resume_content)
        
        # Analyze formatting
        formatting_score = self._analyze_formatting(resume_content)
        
        # Analyze content structure
        content_score = self._analyze_content_structure(resume_content)
        
        # Analyze keyword optimization
        keyword_score = self._analyze_keyword_optimization(resume_content)
        
        # Calculate section scores
        section_scores = self._analyze_sections(resume_content)
        
        # Calculate overall score
        overall_score = (formatting_score + content_score + keyword_score) / 3
        
        # Determine compatibility level
        if overall_score >= 0.9:
            compatibility_level = ATSCompatibilityLevel.EXCELLENT
        elif overall_score >= 0.7:
            compatibility_level = ATSCompatibilityLevel.GOOD
        elif overall_score >= 0.5:
            compatibility_level = ATSCompatibilityLevel.FAIR
        else:
            compatibility_level = ATSCompatibilityLevel.POOR
        
        return ATSCompatibilityReport(
            overall_score=overall_score,
            compatibility_level=compatibility_level,
            issues=issues,
            formatting_score=formatting_score,
            content_score=content_score,
            keyword_score=keyword_score,
            section_scores=section_scores
        )
    
    def _check_problematic_elements(self, content: str) -> List[ATSIssue]:
        """Check for ATS-problematic elements in resume."""
        issues = []
        
        # Check for headers/footers
        for pattern in self.problematic_elements['headers_footers']:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(ATSIssue(
                    issue_type="Headers/Footers",
                    description="Resume contains headers or footers that may not parse correctly",
                    severity=IssueSeverity.MEDIUM,
                    suggestion="Remove headers and footers, include contact info in body"
                ))
                break
        
        # Check for tables
        for pattern in self.problematic_elements['tables']:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(ATSIssue(
                    issue_type="Tables",
                    description="Resume contains tables that may not parse correctly",
                    severity=IssueSeverity.HIGH,
                    suggestion="Convert tables to simple text format with clear separators"
                ))
                break
        
        # Check for images
        for pattern in self.problematic_elements['images']:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(ATSIssue(
                    issue_type="Images",
                    description="Resume contains images that cannot be read by ATS",
                    severity=IssueSeverity.CRITICAL,
                    suggestion="Remove all images and graphics, use text only"
                ))
                break
        
        # Check for special characters
        special_chars = re.findall(self.problematic_elements['special_chars'][0], content)
        if special_chars:
            issues.append(ATSIssue(
                issue_type="Special Characters",
                description=f"Resume contains {len(special_chars)} special characters",
                severity=IssueSeverity.MEDIUM,
                suggestion="Replace special characters with standard ASCII equivalents"
            ))
        
        # Check for font specifications
        for pattern in self.problematic_elements['fonts']:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(ATSIssue(
                    issue_type="Font Specifications",
                    description="Resume contains font specifications that may not be preserved",
                    severity=IssueSeverity.LOW,
                    suggestion="Remove font specifications, use standard formatting"
                ))
                break
        
        return issues
    
    def _analyze_formatting(self, content: str) -> float:
        """Analyze formatting compatibility."""
        score = 1.0
        
        # Check for consistent formatting
        lines = content.split('\n')
        if len(lines) < 5:
            score -= 0.3  # Too short
        
        # Check for proper line breaks
        if not any(line.strip() for line in lines):
            score -= 0.5  # No content
        
        # Check for excessive whitespace
        excessive_whitespace = sum(1 for line in lines if len(line.strip()) == 0 and len(line) > 2)
        if excessive_whitespace > len(lines) * 0.3:
            score -= 0.2
        
        # Check for proper section headers
        section_headers = sum(1 for line in lines if re.match(r'^[A-Z][A-Z\s]+:$', line.strip()))
        if section_headers < 3:
            score -= 0.2  # Not enough clear sections
        
        return max(0.0, score)
    
    def _analyze_content_structure(self, content: str) -> float:
        """Analyze content structure and completeness."""
        score = 1.0
        
        # Check for essential sections
        essential_sections = ['contact', 'experience', 'education']
        found_sections = 0
        
        for section_name, patterns in self.resume_sections.items():
            if section_name in essential_sections:
                for pattern in patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        found_sections += 1
                        break
        
        if found_sections < len(essential_sections):
            score -= 0.3 * (len(essential_sections) - found_sections)
        
        # Check for contact information
        contact_patterns = [r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
                          r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # Phone
                          r'\b[A-Z][a-z]+ [A-Z][a-z]+\b']  # Name pattern
        
        contact_found = sum(1 for pattern in contact_patterns if re.search(pattern, content))
        if contact_found < 2:
            score -= 0.2
        
        # Check for experience details
        experience_patterns = [r'\d{4}',  # Years
                             r'january|february|march|april|may|june|july|august|september|october|november|december',
                             r'present|current']
        
        experience_found = sum(1 for pattern in experience_patterns if re.search(pattern, content, re.IGNORECASE))
        if experience_found < 2:
            score -= 0.2
        
        return max(0.0, score)
    
    def _analyze_keyword_optimization(self, content: str) -> float:
        """Analyze keyword optimization."""
        score = 1.0
        
        # Check for action verbs
        action_verbs = ['managed', 'developed', 'created', 'implemented', 'led', 'designed',
                       'analyzed', 'improved', 'increased', 'reduced', 'achieved', 'delivered']
        
        action_verb_count = sum(1 for verb in action_verbs if verb in content.lower())
        if action_verb_count < 3:
            score -= 0.2
        
        # Check for quantified achievements
        quantified_patterns = [r'\d+%', r'\$\d+', r'\d+\+', r'\d+x', r'\d+\s*(years?|months?)']
        quantified_found = sum(1 for pattern in quantified_patterns if re.search(pattern, content))
        if quantified_found < 2:
            score -= 0.2
        
        # Check for skills section
        skills_patterns = [r'skills?', r'technical', r'competencies', r'expertise']
        skills_found = any(re.search(pattern, content, re.IGNORECASE) for pattern in skills_patterns)
        if not skills_found:
            score -= 0.3
        
        return max(0.0, score)
    
    def _analyze_sections(self, content: str) -> List[SectionScore]:
        """Analyze individual resume sections."""
        section_scores = []
        
        for section_name, patterns in self.resume_sections.items():
            score = 0.0
            feedback = ""
            suggestions = []
            
            # Check if section exists
            section_found = any(re.search(pattern, content, re.IGNORECASE) for pattern in patterns)
            
            if section_found:
                score = 0.8  # Base score for having the section
                
                # Analyze section content
                if section_name == 'contact':
                    # Check for complete contact info
                    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content)
                    phone_match = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', content)
                    
                    if email_match and phone_match:
                        score = 1.0
                        feedback = "Complete contact information provided"
                    elif email_match or phone_match:
                        score = 0.7
                        feedback = "Partial contact information provided"
                        suggestions.append("Add missing contact information")
                    else:
                        score = 0.3
                        feedback = "Contact information missing"
                        suggestions.append("Add email and phone number")
                
                elif section_name == 'experience':
                    # Check for detailed experience
                    experience_lines = [line for line in content.split('\n') 
                                     if any(re.search(pattern, line, re.IGNORECASE) 
                                           for pattern in patterns)]
                    
                    if len(experience_lines) > 3:
                        score = 1.0
                        feedback = "Comprehensive experience section"
                    elif len(experience_lines) > 1:
                        score = 0.7
                        feedback = "Basic experience section"
                        suggestions.append("Add more detailed experience descriptions")
                    else:
                        score = 0.4
                        feedback = "Limited experience information"
                        suggestions.append("Expand experience section with details")
                
                elif section_name == 'education':
                    # Check for education details
                    degree_patterns = [r'bachelor', r'master', r'phd', r'associate', r'degree']
                    degree_found = any(re.search(pattern, content, re.IGNORECASE) for pattern in degree_patterns)
                    
                    if degree_found:
                        score = 1.0
                        feedback = "Education details provided"
                    else:
                        score = 0.6
                        feedback = "Education section present but lacks detail"
                        suggestions.append("Add degree information and graduation dates")
                
                elif section_name == 'skills':
                    # Check for skills variety
                    skills_lines = [line for line in content.split('\n') 
                                  if any(re.search(pattern, line, re.IGNORECASE) 
                                        for pattern in patterns)]
                    
                    if len(skills_lines) > 2:
                        score = 1.0
                        feedback = "Comprehensive skills section"
                    elif len(skills_lines) > 0:
                        score = 0.7
                        feedback = "Basic skills section"
                        suggestions.append("Add more skills and categorize them")
                    else:
                        score = 0.3
                        feedback = "Skills section needs improvement"
                        suggestions.append("Create a dedicated skills section")
            else:
                score = 0.0
                feedback = f"{section_name.title()} section not found"
                suggestions.append(f"Add a {section_name} section")
            
            section_scores.append(SectionScore(
                section_name=section_name.title(),
                score=score,
                feedback=feedback,
                suggestions=suggestions
            ))
        
        return section_scores
    
    def _generate_optimization_recommendations(
        self, 
        content: str, 
        ats_report: ATSCompatibilityReport, 
        job_description: str = ""
    ) -> ResumeOptimization:
        """Generate optimization recommendations based on analysis."""
        
        priority_fixes = []
        content_improvements = []
        formatting_suggestions = []
        keyword_additions = []
        section_recommendations = {}
        
        # Priority fixes based on critical issues
        for issue in ats_report.issues:
            if issue.severity == IssueSeverity.CRITICAL:
                priority_fixes.append(issue.suggestion)
            elif issue.severity == IssueSeverity.HIGH:
                priority_fixes.append(issue.suggestion)
        
        # Content improvements based on section scores
        for section in ats_report.section_scores:
            if section.score < 0.7:
                content_improvements.extend(section.suggestions)
                section_recommendations[section.section_name] = section.feedback
        
        # Formatting suggestions
        if ats_report.formatting_score < 0.8:
            formatting_suggestions.extend([
                "Use consistent formatting throughout the resume",
                "Ensure proper spacing between sections",
                "Use standard fonts (Arial, Calibri, Times New Roman)",
                "Avoid complex layouts and graphics"
            ])
        
        # Keyword suggestions based on job description
        if job_description:
            job_keywords = self._extract_keywords_from_job(job_description)
            resume_keywords = self._extract_keywords_from_resume(content)
            missing_keywords = job_keywords - resume_keywords
            
            if missing_keywords:
                keyword_additions.extend(list(missing_keywords)[:10])  # Top 10 missing keywords
        
        return ResumeOptimization(
            priority_fixes=priority_fixes,
            content_improvements=content_improvements,
            formatting_suggestions=formatting_suggestions,
            keyword_additions=keyword_additions,
            section_recommendations=section_recommendations,
            ats_compatibility=ats_report
        )
    
    def _extract_keywords_from_job(self, job_description: str) -> Set[str]:
        """Extract relevant keywords from job description."""
        # Simple keyword extraction - can be enhanced with NLP
        words = re.findall(r'\b[A-Za-z]{3,}\b', job_description.lower())
        
        # Filter out common words
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'}
        
        keywords = {word for word in words if word not in stop_words and len(word) > 3}
        return keywords
    
    def _extract_keywords_from_resume(self, resume_content: str) -> Set[str]:
        """Extract keywords from resume content."""
        words = re.findall(r'\b[A-Za-z]{3,}\b', resume_content.lower())
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'}
        
        keywords = {word for word in words if word not in stop_words and len(word) > 3}
        return keywords
