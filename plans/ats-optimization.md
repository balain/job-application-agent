# ATS Optimization & Resume Scoring

## Overview

Implement comprehensive ATS (Applicant Tracking System) optimization features including compatibility checking, keyword analysis, resume scoring, and automated improvement suggestions. This focuses on making resumes more likely to pass through ATS filters and reach human reviewers.

## Prerequisites

- Structured output parsing implemented
- Application tracking database implemented
- LLM provider configured and working

## Implementation Steps

### 1. Create ATS Analyzer (`src/ats_analyzer.py`)

**New file**: `src/ats_analyzer.py`

Implement comprehensive ATS compatibility checking:

```python
import re
import json
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ATSReport:
    """ATS compatibility report"""
    overall_score: float
    formatting_score: float
    structure_score: float
    keyword_score: float
    issues: List[Dict[str, str]]
    recommendations: List[str]
    ats_friendly: bool

class ATSAnalyzer:
    def __init__(self):
        self.ats_rules = self._load_ats_rules()
    
    def analyze_resume(self, resume_text: str, job_description: str = None) -> ATSReport:
        """Comprehensive ATS analysis"""
        
        # Check formatting issues
        formatting_issues = self._check_formatting(resume_text)
        formatting_score = self._calculate_formatting_score(formatting_issues)
        
        # Check structure
        structure_issues = self._check_structure(resume_text)
        structure_score = self._calculate_structure_score(structure_issues)
        
        # Check keywords if job description provided
        keyword_score = 0
        keyword_issues = []
        if job_description:
            keyword_analysis = self._analyze_keywords(resume_text, job_description)
            keyword_score = keyword_analysis['score']
            keyword_issues = keyword_analysis['issues']
        
        # Calculate overall score
        overall_score = (formatting_score * 0.4 + structure_score * 0.4 + keyword_score * 0.2)
        
        # Combine all issues
        all_issues = formatting_issues + structure_issues + keyword_issues
        
        # Generate recommendations
        recommendations = self._generate_recommendations(all_issues, overall_score)
        
        return ATSReport(
            overall_score=overall_score,
            formatting_score=formatting_score,
            structure_score=structure_score,
            keyword_score=keyword_score,
            issues=all_issues,
            recommendations=recommendations,
            ats_friendly=overall_score >= 80
        )
    
    def _check_formatting(self, resume_text: str) -> List[Dict[str, str]]:
        """Check for ATS-unfriendly formatting"""
        issues = []
        
        # Check for tables
        if re.search(r'\|.*\|', resume_text):
            issues.append({
                'type': 'formatting',
                'severity': 'high',
                'issue': 'Tables detected',
                'description': 'Tables are not ATS-friendly and may cause parsing issues'
            })
        
        # Check for headers/footers
        if re.search(r'^(Header|Footer):', resume_text, re.MULTILINE):
            issues.append({
                'type': 'formatting',
                'severity': 'medium',
                'issue': 'Headers/Footers detected',
                'description': 'Headers and footers may not be parsed correctly by ATS'
            })
        
        # Check for text boxes
        if re.search(r'\[.*\]', resume_text):
            issues.append({
                'type': 'formatting',
                'severity': 'medium',
                'issue': 'Text boxes detected',
                'description': 'Text boxes may not be parsed by ATS systems'
            })
        
        # Check for images/graphics
        if re.search(r'\[Image\]|\[Graphic\]|\[Chart\]', resume_text):
            issues.append({
                'type': 'formatting',
                'severity': 'high',
                'issue': 'Images/Graphics detected',
                'description': 'Images and graphics are not parsed by ATS systems'
            })
        
        # Check for unusual fonts
        if re.search(r'[^\x00-\x7F]', resume_text):
            issues.append({
                'type': 'formatting',
                'severity': 'medium',
                'issue': 'Non-standard characters detected',
                'description': 'Special characters may not display correctly in ATS'
            })
        
        # Check for excessive formatting
        bold_count = len(re.findall(r'\*\*.*?\*\*', resume_text))
        italic_count = len(re.findall(r'\*.*?\*', resume_text))
        if bold_count > 10 or italic_count > 10:
            issues.append({
                'type': 'formatting',
                'severity': 'low',
                'issue': 'Excessive formatting',
                'description': 'Too much bold or italic text may confuse ATS parsing'
            })
        
        return issues
    
    def _check_structure(self, resume_text: str) -> List[Dict[str, str]]:
        """Check resume structure for ATS compatibility"""
        issues = []
        
        # Check for standard section headers
        required_sections = ['experience', 'education', 'skills']
        found_sections = []
        
        for section in required_sections:
            if re.search(rf'\b{section}\b', resume_text, re.IGNORECASE):
                found_sections.append(section)
        
        missing_sections = set(required_sections) - set(found_sections)
        for section in missing_sections:
            issues.append({
                'type': 'structure',
                'severity': 'high',
                'issue': f'Missing {section.title()} section',
                'description': f'ATS systems expect a {section} section'
            })
        
        # Check contact information
        contact_issues = self._check_contact_info(resume_text)
        issues.extend(contact_issues)
        
        # Check for proper date formatting
        date_issues = self._check_date_formatting(resume_text)
        issues.extend(date_issues)
        
        # Check for proper bullet points
        bullet_issues = self._check_bullet_points(resume_text)
        issues.extend(bullet_issues)
        
        return issues
    
    def _check_contact_info(self, resume_text: str) -> List[Dict[str, str]]:
        """Check contact information format"""
        issues = []
        
        # Check for email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if not re.search(email_pattern, resume_text):
            issues.append({
                'type': 'structure',
                'severity': 'high',
                'issue': 'No email address found',
                'description': 'Email address is required for ATS systems'
            })
        
        # Check for phone number
        phone_pattern = r'(\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}'
        if not re.search(phone_pattern, resume_text):
            issues.append({
                'type': 'structure',
                'severity': 'medium',
                'issue': 'No phone number found',
                'description': 'Phone number helps ATS systems contact you'
            })
        
        # Check for location
        location_pattern = r'\b[A-Z][a-z]+,\s*[A-Z]{2}\b'
        if not re.search(location_pattern, resume_text):
            issues.append({
                'type': 'structure',
                'severity': 'low',
                'issue': 'No location found',
                'description': 'Location helps ATS systems filter candidates'
            })
        
        return issues
    
    def _check_date_formatting(self, resume_text: str) -> List[Dict[str, str]]:
        """Check date formatting"""
        issues = []
        
        # Look for dates
        date_patterns = [
            r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b',
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',
            r'\b\d{4}-\d{1,2}-\d{1,2}\b'
        ]
        
        dates_found = []
        for pattern in date_patterns:
            dates_found.extend(re.findall(pattern, resume_text))
        
        if not dates_found:
            issues.append({
                'type': 'structure',
                'severity': 'medium',
                'issue': 'No dates found',
                'description': 'Dates help ATS systems understand experience timeline'
            })
        
        return issues
    
    def _check_bullet_points(self, resume_text: str) -> List[Dict[str, str]]:
        """Check bullet point formatting"""
        issues = []
        
        # Check for various bullet point styles
        bullet_patterns = [
            r'^\s*[-•*]\s+',  # Standard bullets
            r'^\s*\d+\.\s+',  # Numbered lists
            r'^\s*[a-zA-Z]\.\s+',  # Lettered lists
        ]
        
        bullets_found = False
        for pattern in bullet_patterns:
            if re.search(pattern, resume_text, re.MULTILINE):
                bullets_found = True
                break
        
        if not bullets_found:
            issues.append({
                'type': 'structure',
                'severity': 'low',
                'issue': 'No bullet points found',
                'description': 'Bullet points help organize information for ATS systems'
            })
        
        return issues
    
    def _analyze_keywords(self, resume_text: str, job_description: str) -> Dict[str, Any]:
        """Analyze keyword match between resume and job description"""
        
        # Extract keywords from job description
        job_keywords = self._extract_keywords(job_description)
        
        # Extract keywords from resume
        resume_keywords = self._extract_keywords(resume_text)
        
        # Calculate match score
        matched_keywords = set(job_keywords) & set(resume_keywords)
        total_keywords = len(job_keywords)
        match_score = (len(matched_keywords) / total_keywords * 100) if total_keywords > 0 else 0
        
        # Find missing keywords
        missing_keywords = set(job_keywords) - set(resume_keywords)
        
        issues = []
        if missing_keywords:
            issues.append({
                'type': 'keywords',
                'severity': 'medium',
                'issue': f'Missing {len(missing_keywords)} important keywords',
                'description': f'Missing keywords: {", ".join(list(missing_keywords)[:5])}'
            })
        
        return {
            'score': match_score,
            'matched_keywords': list(matched_keywords),
            'missing_keywords': list(missing_keywords),
            'issues': issues
        }
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        # Convert to lowercase for comparison
        text_lower = text.lower()
        
        # Common technical keywords
        technical_keywords = [
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node.js',
            'sql', 'mysql', 'postgresql', 'mongodb', 'aws', 'azure', 'docker',
            'kubernetes', 'git', 'agile', 'scrum', 'api', 'rest', 'graphql',
            'machine learning', 'ai', 'data science', 'analytics', 'tableau',
            'power bi', 'excel', 'project management', 'leadership', 'teamwork'
        ]
        
        # Extract keywords that appear in the text
        found_keywords = []
        for keyword in technical_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        # Also extract capitalized words (likely proper nouns/company names)
        capitalized_words = re.findall(r'\b[A-Z][a-z]+\b', text)
        found_keywords.extend([word.lower() for word in capitalized_words[:10]])  # Limit to first 10
        
        return list(set(found_keywords))  # Remove duplicates
    
    def _calculate_formatting_score(self, issues: List[Dict]) -> float:
        """Calculate formatting score based on issues"""
        if not issues:
            return 100.0
        
        high_severity = sum(1 for issue in issues if issue['severity'] == 'high')
        medium_severity = sum(1 for issue in issues if issue['severity'] == 'medium')
        low_severity = sum(1 for issue in issues if issue['severity'] == 'low')
        
        # Deduct points based on severity
        score = 100.0
        score -= high_severity * 20
        score -= medium_severity * 10
        score -= low_severity * 5
        
        return max(0, score)
    
    def _calculate_structure_score(self, issues: List[Dict]) -> float:
        """Calculate structure score based on issues"""
        if not issues:
            return 100.0
        
        high_severity = sum(1 for issue in issues if issue['severity'] == 'high')
        medium_severity = sum(1 for issue in issues if issue['severity'] == 'medium')
        low_severity = sum(1 for issue in issues if issue['severity'] == 'low')
        
        # Deduct points based on severity
        score = 100.0
        score -= high_severity * 25
        score -= medium_severity * 15
        score -= low_severity * 5
        
        return max(0, score)
    
    def _generate_recommendations(self, issues: List[Dict], overall_score: float) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if overall_score < 60:
            recommendations.append("Resume needs significant ATS optimization")
        
        # Group issues by type
        formatting_issues = [i for i in issues if i['type'] == 'formatting']
        structure_issues = [i for i in issues if i['type'] == 'structure']
        keyword_issues = [i for i in issues if i['type'] == 'keywords']
        
        if formatting_issues:
            recommendations.append("Remove tables, images, and complex formatting")
            recommendations.append("Use standard fonts and simple formatting")
        
        if structure_issues:
            recommendations.append("Add missing required sections (Experience, Education, Skills)")
            recommendations.append("Ensure contact information is properly formatted")
        
        if keyword_issues:
            recommendations.append("Add missing keywords from job description")
            recommendations.append("Use industry-specific terminology")
        
        # General recommendations
        recommendations.append("Use standard section headers")
        recommendations.append("Include quantifiable achievements")
        recommendations.append("Keep formatting simple and clean")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def _load_ats_rules(self) -> Dict[str, Any]:
        """Load ATS rules and patterns"""
        return {
            'required_sections': ['experience', 'education', 'skills'],
            'preferred_formats': ['.docx', '.pdf', '.txt'],
            'avoid_formats': ['.doc', '.rtf', '.odt'],
            'max_file_size': 5 * 1024 * 1024,  # 5MB
            'max_pages': 2
        }
```

### 2. Create Resume Scorer (`src/resume_scorer.py`)

**New file**: `src/resume_scorer.py`

Implement comprehensive resume scoring:

```python
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import re
from datetime import datetime

@dataclass
class ResumeScore:
    """Comprehensive resume score"""
    overall_score: float
    ats_score: float
    content_score: float
    format_score: float
    keyword_score: float
    experience_score: float
    education_score: float
    skills_score: float
    achievements_score: float
    recommendations: List[str]

class ResumeScorer:
    def __init__(self):
        self.scoring_weights = {
            'ats_compatibility': 0.25,
            'content_quality': 0.20,
            'formatting': 0.15,
            'keywords': 0.15,
            'experience': 0.10,
            'education': 0.05,
            'skills': 0.05,
            'achievements': 0.05
        }
    
    def score_resume(self, resume_text: str, job_description: str = None) -> ResumeScore:
        """Calculate comprehensive resume score"""
        
        # ATS compatibility score
        from .ats_analyzer import ATSAnalyzer
        ats_analyzer = ATSAnalyzer()
        ats_report = ats_analyzer.analyze_resume(resume_text, job_description)
        ats_score = ats_report.overall_score
        
        # Content quality score
        content_score = self._score_content_quality(resume_text)
        
        # Formatting score
        format_score = self._score_formatting(resume_text)
        
        # Keyword score
        keyword_score = ats_report.keyword_score if job_description else self._score_keywords_general(resume_text)
        
        # Experience score
        experience_score = self._score_experience(resume_text)
        
        # Education score
        education_score = self._score_education(resume_text)
        
        # Skills score
        skills_score = self._score_skills(resume_text)
        
        # Achievements score
        achievements_score = self._score_achievements(resume_text)
        
        # Calculate weighted overall score
        overall_score = (
            ats_score * self.scoring_weights['ats_compatibility'] +
            content_score * self.scoring_weights['content_quality'] +
            format_score * self.scoring_weights['formatting'] +
            keyword_score * self.scoring_weights['keywords'] +
            experience_score * self.scoring_weights['experience'] +
            education_score * self.scoring_weights['education'] +
            skills_score * self.scoring_weights['skills'] +
            achievements_score * self.scoring_weights['achievements']
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations({
            'ats_score': ats_score,
            'content_score': content_score,
            'format_score': format_score,
            'keyword_score': keyword_score,
            'experience_score': experience_score,
            'education_score': education_score,
            'skills_score': skills_score,
            'achievements_score': achievements_score
        })
        
        return ResumeScore(
            overall_score=overall_score,
            ats_score=ats_score,
            content_score=content_score,
            format_score=format_score,
            keyword_score=keyword_score,
            experience_score=experience_score,
            education_score=education_score,
            skills_score=skills_score,
            achievements_score=achievements_score,
            recommendations=recommendations
        )
    
    def _score_content_quality(self, resume_text: str) -> float:
        """Score content quality"""
        score = 0
        
        # Check for quantifiable achievements
        numbers = re.findall(r'\b\d+(?:\.\d+)?%?\b', resume_text)
        if len(numbers) >= 3:
            score += 30
        elif len(numbers) >= 1:
            score += 15
        
        # Check for action verbs
        action_verbs = [
            'achieved', 'managed', 'led', 'developed', 'created', 'implemented',
            'increased', 'decreased', 'improved', 'optimized', 'designed', 'built'
        ]
        verb_count = sum(1 for verb in action_verbs if verb in resume_text.lower())
        if verb_count >= 5:
            score += 25
        elif verb_count >= 3:
            score += 15
        
        # Check for professional language
        professional_terms = [
            'strategic', 'collaborative', 'innovative', 'comprehensive', 'proven',
            'expertise', 'proficiency', 'specialized', 'advanced', 'certified'
        ]
        term_count = sum(1 for term in professional_terms if term in resume_text.lower())
        if term_count >= 3:
            score += 20
        
        # Check resume length (not too short, not too long)
        word_count = len(resume_text.split())
        if 300 <= word_count <= 800:
            score += 25
        elif 200 <= word_count <= 1000:
            score += 15
        
        return min(100, score)
    
    def _score_formatting(self, resume_text: str) -> float:
        """Score formatting quality"""
        score = 100
        
        # Check for consistent formatting
        lines = resume_text.split('\n')
        header_lines = [line for line in lines if re.match(r'^[A-Z][A-Z\s]+$', line.strip())]
        
        if len(header_lines) >= 3:
            score -= 0  # Good
        else:
            score -= 20  # Missing headers
        
        # Check for proper spacing
        double_spaces = resume_text.count('  ')
        if double_spaces > 10:
            score -= 10
        
        # Check for bullet points
        bullet_count = len(re.findall(r'^\s*[-•*]\s+', resume_text, re.MULTILINE))
        if bullet_count >= 5:
            score -= 0  # Good
        elif bullet_count >= 2:
            score -= 10
        else:
            score -= 20
        
        return max(0, score)
    
    def _score_keywords_general(self, resume_text: str) -> float:
        """Score keywords without job description"""
        score = 0
        
        # Technical keywords
        tech_keywords = [
            'python', 'java', 'javascript', 'react', 'sql', 'aws', 'docker',
            'git', 'agile', 'api', 'machine learning', 'data analysis'
        ]
        
        found_keywords = sum(1 for keyword in tech_keywords if keyword in resume_text.lower())
        score = min(100, found_keywords * 8)  # 8 points per keyword, max 100
        
        return score
    
    def _score_experience(self, resume_text: str) -> float:
        """Score experience section"""
        score = 0
        
        # Look for experience section
        experience_section = self._extract_section(resume_text, 'experience')
        if not experience_section:
            return 0
        
        # Check for job titles
        job_titles = re.findall(r'\b(?:Senior|Lead|Principal|Manager|Director|Engineer|Developer|Analyst|Specialist)\b', experience_section)
        score += len(job_titles) * 15
        
        # Check for company names
        companies = re.findall(r'\b[A-Z][a-zA-Z\s&]+(?:Inc|Corp|LLC|Ltd|Company)\b', experience_section)
        score += len(companies) * 10
        
        # Check for dates
        dates = re.findall(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b', experience_section)
        score += len(dates) * 5
        
        return min(100, score)
    
    def _score_education(self, resume_text: str) -> float:
        """Score education section"""
        score = 0
        
        education_section = self._extract_section(resume_text, 'education')
        if not education_section:
            return 0
        
        # Check for degree types
        degrees = re.findall(r'\b(?:Bachelor|Master|PhD|Doctorate|Associate|Certificate)\b', education_section)
        score += len(degrees) * 25
        
        # Check for GPA
        gpa = re.search(r'\b(?:GPA|gpa):\s*(\d+\.\d+)', education_section)
        if gpa:
            gpa_value = float(gpa.group(1))
            if gpa_value >= 3.5:
                score += 20
            elif gpa_value >= 3.0:
                score += 10
        
        # Check for graduation year
        grad_year = re.search(r'\b(?:19|20)\d{2}\b', education_section)
        if grad_year:
            score += 15
        
        return min(100, score)
    
    def _score_skills(self, resume_text: str) -> float:
        """Score skills section"""
        score = 0
        
        skills_section = self._extract_section(resume_text, 'skills')
        if not skills_section:
            return 0
        
        # Count skills
        skill_indicators = [',', ';', '•', '-', '|']
        skill_count = 0
        for indicator in skill_indicators:
            skill_count += skills_section.count(indicator)
        
        if skill_count >= 10:
            score += 50
        elif skill_count >= 5:
            score += 30
        elif skill_count >= 2:
            score += 15
        
        # Check for skill categories
        categories = ['technical', 'soft', 'programming', 'tools', 'languages']
        category_count = sum(1 for cat in categories if cat in skills_section.lower())
        score += category_count * 10
        
        return min(100, score)
    
    def _score_achievements(self, resume_text: str) -> float:
        """Score achievements and accomplishments"""
        score = 0
        
        # Look for achievement indicators
        achievement_words = ['achieved', 'accomplished', 'awarded', 'recognized', 'honored']
        achievement_count = sum(1 for word in achievement_words if word in resume_text.lower())
        score += achievement_count * 15
        
        # Look for quantifiable results
        percentage_pattern = r'\b\d+(?:\.\d+)?%\b'
        percentages = re.findall(percentage_pattern, resume_text)
        score += len(percentages) * 10
        
        # Look for dollar amounts
        dollar_pattern = r'\$\d+(?:,\d{3})*(?:\.\d{2})?'
        dollars = re.findall(dollar_pattern, resume_text)
        score += len(dollars) * 10
        
        return min(100, score)
    
    def _extract_section(self, resume_text: str, section_name: str) -> str:
        """Extract a specific section from resume"""
        pattern = rf'\b{section_name}\b.*?(?=\n\b[A-Z][A-Z\s]*\b|\Z)'
        match = re.search(pattern, resume_text, re.IGNORECASE | re.DOTALL)
        return match.group(0) if match else ""
    
    def _generate_recommendations(self, scores: Dict[str, float]) -> List[str]:
        """Generate recommendations based on scores"""
        recommendations = []
        
        if scores['ats_score'] < 70:
            recommendations.append("Improve ATS compatibility by removing tables and complex formatting")
        
        if scores['content_score'] < 70:
            recommendations.append("Add more quantifiable achievements and action verbs")
        
        if scores['format_score'] < 70:
            recommendations.append("Improve formatting consistency and add proper section headers")
        
        if scores['keyword_score'] < 70:
            recommendations.append("Add more relevant keywords and industry terminology")
        
        if scores['experience_score'] < 70:
            recommendations.append("Enhance experience section with more detailed job descriptions")
        
        if scores['education_score'] < 70:
            recommendations.append("Add more education details including GPA and graduation year")
        
        if scores['skills_score'] < 70:
            recommendations.append("Expand skills section with more technical and soft skills")
        
        if scores['achievements_score'] < 70:
            recommendations.append("Add more quantifiable achievements and accomplishments")
        
        return recommendations[:5]  # Limit to top 5
```

### 3. Update Analyzer Integration (`src/analyzer.py`)

**Modify existing**: `src/analyzer.py`

Add ATS optimization to analysis workflow:

```python
# Add to analyze_application method after main analysis
def analyze_application(self, job_description: str, resume: str) -> Dict[str, Any]:
    """Perform comprehensive analysis with ATS optimization"""
    console.print("[bold blue]Starting job application analysis...[/bold blue]")
    
    # ... existing analysis code ...
    
    # NEW: Add ATS optimization analysis
    if Config.ATS_OPTIMIZATION_ENABLED:
        try:
            from .ats_analyzer import ATSAnalyzer
            from .resume_scorer import ResumeScorer
            
            ats_analyzer = ATSAnalyzer()
            resume_scorer = ResumeScorer()
            
            # Generate ATS report
            ats_report = ats_analyzer.analyze_resume(resume, job_description)
            
            # Generate resume score
            resume_score = resume_scorer.score_resume(resume, job_description)
            
            results['ats_optimization'] = {
                'ats_report': ats_report,
                'resume_score': resume_score,
                'optimization_needed': ats_report.overall_score < 80 or resume_score.overall_score < 70
            }
            
            console.print(f"[blue]ATS Score: {ats_report.overall_score:.1f}/100[/blue]")
            console.print(f"[blue]Resume Score: {resume_score.overall_score:.1f}/100[/blue]")
            
        except Exception as e:
            console.print(f"[yellow]Warning: Could not perform ATS analysis: {e}[/yellow]")
    
    return results
```

### 4. Add ATS Commands (`main.py`)

**Modify existing**: `main.py`

Add new CLI commands for ATS optimization:

```python
# Add new arguments
parser.add_argument(
    "--check-ats",
    action="store_true",
    help="Check resume ATS compatibility"
)

parser.add_argument(
    "--score-resume",
    action="store_true",
    help="Generate comprehensive resume score"
)

parser.add_argument(
    "--ats-report",
    metavar="OUTPUT",
    help="Generate detailed ATS report and save to file"
)

parser.add_argument(
    "--optimize-for-ats",
    action="store_true",
    help="Show ATS optimization suggestions"
)

# Add command handlers
if args.check_ats:
    from src.ats_analyzer import ATSAnalyzer
    
    ats_analyzer = ATSAnalyzer()
    report = ats_analyzer.analyze_resume(resume, job_description)
    
    # Display ATS report
    from rich.panel import Panel
    from rich.table import Table
    
    # Overall score
    score_color = "green" if report.ats_friendly else "red"
    console.print(Panel(
        f"ATS Compatibility: [{score_color}]{report.overall_score:.1f}/100[/{score_color}]\n"
        f"Formatting: {report.formatting_score:.1f}/100\n"
        f"Structure: {report.structure_score:.1f}/100\n"
        f"Keywords: {report.keyword_score:.1f}/100",
        title="ATS Analysis Results",
        border_style=score_color
    ))
    
    # Issues table
    if report.issues:
        table = Table(title="Issues Found")
        table.add_column("Type", style="cyan")
        table.add_column("Severity", style="red")
        table.add_column("Issue", style="yellow")
        table.add_column("Description", style="white")
        
        for issue in report.issues:
            severity_color = {"high": "red", "medium": "yellow", "low": "green"}[issue['severity']]
            table.add_row(
                issue['type'].title(),
                f"[{severity_color}]{issue['severity'].title()}[/{severity_color}]",
                issue['issue'],
                issue['description']
            )
        
        console.print(table)
    
    # Recommendations
    if report.recommendations:
        rec_text = "\n".join([f"• {rec}" for rec in report.recommendations])
        console.print(Panel(rec_text, title="Recommendations", border_style="blue"))
    
    sys.exit(0)

if args.score_resume:
    from src.resume_scorer import ResumeScorer
    
    scorer = ResumeScorer()
    score = scorer.score_resume(resume, job_description)
    
    # Display comprehensive score
    from rich.panel import Panel
    from rich.progress import Progress, BarColumn, TextColumn
    
    console.print(Panel(
        f"Overall Resume Score: [bold green]{score.overall_score:.1f}/100[/bold green]",
        title="Resume Scoring Results",
        border_style="green"
    ))
    
    # Score breakdown
    scores_data = [
        ("ATS Compatibility", score.ats_score),
        ("Content Quality", score.content_score),
        ("Formatting", score.format_score),
        ("Keywords", score.keyword_score),
        ("Experience", score.experience_score),
        ("Education", score.education_score),
        ("Skills", score.skills_score),
        ("Achievements", score.achievements_score)
    ]
    
    for name, value in scores_data:
        color = "green" if value >= 80 else "yellow" if value >= 60 else "red"
        console.print(f"{name}: [{color}]{value:.1f}/100[/{color}]")
    
    # Recommendations
    if score.recommendations:
        rec_text = "\n".join([f"• {rec}" for rec in score.recommendations])
        console.print(Panel(rec_text, title="Improvement Recommendations", border_style="blue"))
    
    sys.exit(0)

if args.ats_report:
    from src.ats_analyzer import ATSAnalyzer
    from src.resume_scorer import ResumeScorer
    import json
    
    ats_analyzer = ATSAnalyzer()
    scorer = ResumeScorer()
    
    ats_report = ats_analyzer.analyze_resume(resume, job_description)
    resume_score = scorer.score_resume(resume, job_description)
    
    # Create comprehensive report
    report_data = {
        'timestamp': datetime.now().isoformat(),
        'ats_analysis': {
            'overall_score': ats_report.overall_score,
            'formatting_score': ats_report.formatting_score,
            'structure_score': ats_report.structure_score,
            'keyword_score': ats_report.keyword_score,
            'ats_friendly': ats_report.ats_friendly,
            'issues': ats_report.issues,
            'recommendations': ats_report.recommendations
        },
        'resume_scoring': {
            'overall_score': resume_score.overall_score,
            'ats_score': resume_score.ats_score,
            'content_score': resume_score.content_score,
            'format_score': resume_score.format_score,
            'keyword_score': resume_score.keyword_score,
            'experience_score': resume_score.experience_score,
            'education_score': resume_score.education_score,
            'skills_score': resume_score.skills_score,
            'achievements_score': resume_score.achievements_score,
            'recommendations': resume_score.recommendations
        }
    }
    
    with open(args.ats_report, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    console.print(f"[green]ATS report saved to: {args.ats_report}[/green]")
    sys.exit(0)

if args.optimize_for_ats:
    from src.ats_analyzer import ATSAnalyzer
    from src.resume_scorer import ResumeScorer
    
    ats_analyzer = ATSAnalyzer()
    scorer = ResumeScorer()
    
    ats_report = ats_analyzer.analyze_resume(resume, job_description)
    resume_score = scorer.score_resume(resume, job_description)
    
    # Combine recommendations
    all_recommendations = ats_report.recommendations + resume_score.recommendations
    unique_recommendations = list(dict.fromkeys(all_recommendations))  # Remove duplicates
    
    console.print(Panel(
        "\n".join([f"• {rec}" for rec in unique_recommendations]),
        title="ATS Optimization Recommendations",
        border_style="blue"
    ))
    
    sys.exit(0)
```

### 5. Update Configuration (`config.py`)

**Modify existing**: `config.py`

Add ATS optimization configuration:

```python
# ATS Optimization settings
ATS_OPTIMIZATION_ENABLED = os.getenv("ATS_OPTIMIZATION_ENABLED", "true").lower() == "true"
ATS_SCORE_THRESHOLD = float(os.getenv("ATS_SCORE_THRESHOLD", "80.0"))
RESUME_SCORE_THRESHOLD = float(os.getenv("RESUME_SCORE_THRESHOLD", "70.0"))

# ATS Analysis settings
ATS_STRICT_MODE = os.getenv("ATS_STRICT_MODE", "false").lower() == "true"
KEYWORD_MATCH_THRESHOLD = float(os.getenv("KEYWORD_MATCH_THRESHOLD", "70.0"))
```

### 6. Update Dependencies (`pyproject.toml`)

**Modify existing**: `pyproject.toml`

Add to dependencies (if needed):
```toml
"pypdf>=3.0.0",  # PDF parsing for ATS analysis
```

### 7. Update Documentation (`README.md`)

**Modify existing**: `README.md`

Add new sections:

**ATS Optimization** (new major section):
- Explain ATS compatibility checking
- Document `--check-ats` command
- Document `--score-resume` command
- Document `--ats-report` command
- Document `--optimize-for-ats` command
- Explain scoring system and thresholds

**Resume Scoring** (new section):
- Explain comprehensive scoring system
- Show score breakdown and weights
- Explain improvement recommendations

**Environment Variables** (update existing):
```
ATS_OPTIMIZATION_ENABLED=true
ATS_SCORE_THRESHOLD=80.0
RESUME_SCORE_THRESHOLD=70.0
ATS_STRICT_MODE=false
KEYWORD_MATCH_THRESHOLD=70.0
```

## Testing Strategy

1. Test ATS compatibility checking with various resume formats
2. Test resume scoring with different resume types
3. Test keyword analysis and matching
4. Test issue detection and recommendations
5. Test integration with main analysis workflow
6. Test output formatting and report generation
7. Test with real resumes and job descriptions

## Integration Points

**With Phase 1 (Structured Output)**:
- Uses structured data models for ATS reports
- Leverages improved parsing reliability

**With Phase 2 (Application Tracking)**:
- Stores ATS scores in application database
- Tracks optimization improvements over time

**With existing analyzer**:
- Seamless integration with analysis workflow
- Optional ATS analysis (controlled by config)
- Preserves existing functionality

## Security Considerations

- Validate all resume content before analysis
- Sanitize output to prevent information leakage
- Secure handling of personal information
- Validate file inputs and paths

## Performance Considerations

- Cache ATS analysis results
- Optimize regex patterns for performance
- Limit analysis depth for large resumes
- Implement efficient keyword extraction

## Files to Create/Modify

**New Files**:
- `src/ats_analyzer.py` (ATS compatibility checking)
- `src/resume_scorer.py` (Comprehensive resume scoring)

**Modified Files**:
- `src/analyzer.py` (Add ATS optimization integration)
- `config.py` (Add ATS configuration)
- `main.py` (Add ATS commands)
- `pyproject.toml` (Add dependencies if needed)
- `README.md` (Add ATS documentation)

## Success Criteria

- ATS compatibility detection works for common issues
- Resume scoring provides actionable insights
- Keyword analysis identifies missing keywords accurately
- Issue detection covers major ATS problems
- Recommendations are specific and actionable
- Performance is acceptable (< 3s for full analysis)
- Integration with existing workflow works seamlessly
- Clear documentation and examples

## Future Enhancements

- Machine learning for ATS compatibility prediction
- Industry-specific ATS rules
- Resume template optimization
- A/B testing of different resume versions
- Integration with job board APIs
- Automated resume improvement suggestions

## To-dos

- [ ] Create src/ats_analyzer.py with comprehensive ATS compatibility checking
- [ ] Create src/resume_scorer.py with multi-dimensional resume scoring
- [ ] Update src/analyzer.py to integrate ATS optimization analysis
- [ ] Add ATS optimization CLI commands to main.py
- [ ] Add ATS configuration options to config.py
- [ ] Add pypdf dependency to pyproject.toml if needed
- [ ] Update README.md with ATS optimization and scoring documentation

### 2. Create Smart Tailoring Module (`src/resume_tailor.py`)

**New file**: `src/resume_tailor.py`

Implement automated resume tailoring:

```python
class ResumeTailor:
    def __init__(self, llm_provider):
        self.llm = llm_provider
    
    def tailor_resume(self, resume: str, job_desc: str, style: str = 'moderate') -> str:
        # Generate tailored resume version
        # style: 'conservative', 'moderate', 'aggressive'
        # Returns: tailored resume text
    
    def insert_keywords(self, resume: str, keywords: List[str], context: str) -> str:
        # Intelligently insert missing keywords
        # Returns: updated resume with keywords
    
    def rewrite_bullet_points(self, bullet_points: List[str], job_desc: str) -> List[str]:
        # Optimize bullet points for specific job
        # Returns: rewritten bullet points
    
    def reorder_sections(self, resume: str, job_desc: str) -> str:
        # Prioritize most relevant sections
        # Returns: reordered resume
    
    def optimize_length(self, resume: str, target_pages: int = 1) -> str:
        # Optimize resume to target length
        # Returns: optimized resume
    
    def generate_summary(self, resume: str, job_desc: str) -> str:
        # Generate job-specific professional summary
        # Returns: tailored summary paragraph
```

### 3. Create ATS Analyzer Module (`src/ats_analyzer.py`)

**New file**: `src/ats_analyzer.py`

Implement ATS compatibility checking:

```python
class ATSAnalyzer:
    def check_formatting(self, resume_text: str) -> dict:
        # Check for ATS-unfriendly formatting
        # Returns: {
        #   'has_tables': bool,
        #   'has_images': bool,
        #   'has_headers_footers': bool,
        #   'has_columns': bool,
        #   'has_text_boxes': bool,
        #   'issues': List[str]
        # }
    
    def check_file_format(self, file_path: str) -> dict:
        # Check if file format is ATS-friendly
        # Returns: {
        #   'format': str,  # .docx, .pdf, .txt
        #   'is_ats_friendly': bool,
        #   'recommendation': str
        # }
    
    def check_section_headers(self, resume_text: str) -> dict:
        # Check for standard section headers
        # Returns: {
        #   'standard_headers': List[str],
        #   'non_standard_headers': List[str],
        #   'missing_headers': List[str]
        # }
    
    def check_contact_info(self, resume_text: str) -> dict:
        # Verify contact information is parseable
        # Returns: {
        #   'has_email': bool,
        #   'has_phone': bool,
        #   'has_location': bool,
        #   'format_issues': List[str]
        # }
    
    def generate_ats_report(self, resume_text: str, file_path: str) -> dict:
        # Comprehensive ATS compatibility report
        # Returns: {
        #   'overall_score': float,
        #   'formatting_score': float,
        #   'structure_score': float,
        #   'issues': List[dict],
        #   'recommendations': List[str]
        # }
```

### 4. Create Resume Version Manager (`src/resume_versions.py`)

**New file**: `src/resume_versions.py`

Manage multiple resume versions:

```python
class ResumeVersionManager:
    def __init__(self, storage_dir: str = None):
        self.storage_dir = storage_dir or Path.home() / '.job-agent' / 'resumes'
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def save_version(self, resume_text: str, job_title: str, company: str, 
                    metadata: dict = None) -> str:
        # Save tailored resume version
        # Returns: version_id
    
    def list_versions(self) -> List[dict]:
        # List all saved resume versions
        # Returns: [{'version_id': str, 'job_title': str, 'company': str, ...}]
    
    def get_version(self, version_id: str) -> dict:
        # Retrieve specific resume version
        # Returns: {'text': str, 'metadata': dict}
    
    def compare_versions(self, version_id1: str, version_id2: str) -> dict:
        # Compare two resume versions
        # Returns: {
        #   'differences': List[str],
        #   'keyword_changes': dict,
        #   'structure_changes': List[str]
        # }
    
    def delete_version(self, version_id: str) -> bool:
        # Delete a resume version
        # Returns: success status
```

### 5. Update Analyzer with Optimization (`src/analyzer.py`)

**Modify existing**: `src/analyzer.py`

Add resume optimization to analysis workflow:

**Integration point** (after main analysis, around line 150+):
```python
def analyze(self, job_description: str, resume: str) -> dict:
    # ... existing analysis code ...
    
    # NEW: Add resume optimization analysis
    if Config.RESUME_OPTIMIZATION_ENABLED:
        optimization_results = self._analyze_resume_optimization(job_description, resume)
        results['resume_optimization'] = optimization_results
    
    return results

def _analyze_resume_optimization(self, job_desc: str, resume: str) -> dict:
    """Analyze resume optimization opportunities"""
    from src.resume_optimizer import ResumeOptimizer
    from src.ats_analyzer import ATSAnalyzer
    
    optimizer = ResumeOptimizer(self.llm)
    ats_analyzer = ATSAnalyzer()
    
    # Keyword analysis
    keywords = optimizer.extract_keywords(job_desc)
    keyword_analysis = optimizer.analyze_resume_keywords(resume, job_desc)
    
    # ATS compatibility
    ats_report = ats_analyzer.generate_ats_report(resume, "")
    
    # Overall score
    resume_score = optimizer.calculate_resume_score(resume, job_desc)
    
    # Improvement suggestions
    suggestions = optimizer.suggest_improvements(job_desc, resume)
    
    return {
        'keywords': keywords,
        'keyword_analysis': keyword_analysis,
        'ats_report': ats_report,
        'resume_score': resume_score,
        'suggestions': suggestions
    }
```

### 6. Add Optimization Commands (`main.py`)

**Modify existing**: `main.py`

Add new CLI commands for resume optimization:

```python
parser.add_argument(
    "--optimize-resume",
    action="store_true",
    help="Show resume optimization suggestions"
)

parser.add_argument(
    "--tailor-resume",
    metavar="OUTPUT",
    help="Generate tailored resume version and save to OUTPUT file"
)

parser.add_argument(
    "--check-ats",
    action="store_true",
    help="Check resume ATS compatibility"
)

parser.add_argument(
    "--list-resume-versions",
    action="store_true",
    help="List all saved resume versions"
)

parser.add_argument(
    "--tailoring-style",
    choices=["conservative", "moderate", "aggressive"],
    default="moderate",
    help="Resume tailoring aggressiveness"
)
```

**Command handlers**:
```python
# Handle optimization commands
if args.optimize_resume:
    from src.resume_optimizer import ResumeOptimizer
    optimizer = ResumeOptimizer(llm)
    suggestions = optimizer.suggest_improvements(job_description, resume)
    # Display optimization suggestions
    return 0

if args.tailor_resume:
    from src.resume_tailor import ResumeTailor
    from src.resume_versions import ResumeVersionManager
    
    tailor = ResumeTailor(llm)
    version_mgr = ResumeVersionManager()
    
    # Generate tailored resume
    tailored = tailor.tailor_resume(resume, job_description, args.tailoring_style)
    
    # Save version
    version_id = version_mgr.save_version(
        tailored, 
        job_title="Extracted from job desc",
        company="Extracted from job desc"
    )
    
    # Write to output file
    with open(args.tailor_resume, 'w') as f:
        f.write(tailored)
    
    console.print(f"[green]Tailored resume saved to: {args.tailor_resume}[/green]")
    console.print(f"[blue]Version ID: {version_id}[/blue]")
    return 0

if args.check_ats:
    from src.ats_analyzer import ATSAnalyzer
    ats = ATSAnalyzer()
    report = ats.generate_ats_report(resume, args.resume)
    # Display ATS report
    return 0

if args.list_resume_versions:
    from src.resume_versions import ResumeVersionManager
    version_mgr = ResumeVersionManager()
    versions = version_mgr.list_versions()
    # Display versions in table format
    return 0
```

### 7. Update Configuration (`config.py`)

**Modify existing**: `config.py`

Add resume optimization configuration:

```python
# Resume Optimization settings
RESUME_OPTIMIZATION_ENABLED = os.getenv("RESUME_OPTIMIZATION_ENABLED", "true").lower() == "true"
DEFAULT_TAILORING_STYLE = os.getenv("DEFAULT_TAILORING_STYLE", "moderate")
RESUME_STORAGE_DIR = os.getenv("RESUME_STORAGE_DIR", "")
ATS_STRICT_MODE = os.getenv("ATS_STRICT_MODE", "false").lower() == "true"

# Optimization thresholds
KEYWORD_MATCH_THRESHOLD = float(os.getenv("KEYWORD_MATCH_THRESHOLD", "70.0"))
ATS_SCORE_THRESHOLD = float(os.getenv("ATS_SCORE_THRESHOLD", "80.0"))
```

### 8. Create Optimization Output Formatter (`src/optimization_formatter.py`)

**New file**: `src/optimization_formatter.py`

Format optimization results for display:

```python
class OptimizationFormatter:
    def format_keyword_analysis(self, analysis: dict) -> str:
        # Format keyword analysis for console output
        # Uses rich library for formatted display
    
    def format_ats_report(self, report: dict) -> str:
        # Format ATS report with color coding
    
    def format_suggestions(self, suggestions: dict) -> str:
        # Format improvement suggestions
    
    def format_resume_score(self, score: dict) -> str:
        # Format resume score with progress bars
    
    def generate_optimization_report(self, optimization_data: dict, output_path: str):
        # Generate comprehensive optimization report as markdown
```

### 9. Update Documentation

**Modify**: `README.md`

Add new sections:

**Resume Optimization** (new major section):
- Explain keyword analysis and matching
- Document `--optimize-resume` command
- Document `--tailor-resume` command
- Document `--check-ats` command
- Document `--list-resume-versions` command
- Explain tailoring styles (conservative, moderate, aggressive)

**ATS Compatibility** (new section):
- Explain what ATS systems look for
- List common ATS pitfalls
- Provide ATS-friendly formatting guidelines
- Explain ATS scoring system

**Resume Versioning** (new section):
- Explain why multiple versions are useful
- Document version management commands
- Show how to compare versions

**Environment Variables** (update existing):
```
RESUME_OPTIMIZATION_ENABLED=true
DEFAULT_TAILORING_STYLE=moderate
RESUME_STORAGE_DIR=/path/to/resumes
ATS_STRICT_MODE=false
KEYWORD_MATCH_THRESHOLD=70.0
ATS_SCORE_THRESHOLD=80.0
```

**Update**: `.env.example`

Add resume optimization configuration template.

### 10. Update Dependencies

**Modify**: `pyproject.toml`

Add to dependencies (if needed):
```toml
"python-docx>=1.1.0",  # Already included - for Word document handling
"pypdf>=3.0.0",  # PDF parsing for ATS analysis
```

## Testing Strategy

1. Test keyword extraction from various job descriptions
2. Test keyword matching with different resume formats
3. Test ATS compatibility checking with known good/bad resumes
4. Test resume tailoring with different styles
5. Test version management (save, list, retrieve, delete)
6. Test integration with main analysis workflow
7. Test output formatting for all optimization results
8. Test with real job descriptions and resumes

## Integration Points

**With Phase 1 (Encryption)**:
- Encrypted storage of resume versions
- Secure handling of personal information

**With Phase 2 (Graph Database)**:
- Store resume versions in graph
- Track which resume version was used for each application
- Analyze which resume styles perform better

**With existing analyzer**:
- Seamless integration with current analysis workflow
- Optional optimization (controlled by config)

## Security Considerations

- Encrypt stored resume versions
- Sanitize personal information in examples
- Secure file handling for resume uploads
- Validate all file inputs
- Prevent path traversal attacks in version storage

## Performance Considerations

- Cache keyword extraction results
- Batch process multiple resumes
- Optimize LLM calls for tailoring
- Limit resume version storage size
- Implement cleanup of old versions

## Files to Create/Modify

**New Files**:
- `src/resume_optimizer.py` (Keyword analysis and scoring)
- `src/resume_tailor.py` (Smart tailoring)
- `src/ats_analyzer.py` (ATS compatibility checking)
- `src/resume_versions.py` (Version management)
- `src/optimization_formatter.py` (Output formatting)

**Modified Files**:
- `src/analyzer.py` (Add optimization analysis)
- `config.py` (Add optimization config)
- `main.py` (Add optimization commands)
- `README.md` (Add optimization documentation)
- `.env.example` (Add optimization variables)
- `pyproject.toml` (Add dependencies if needed)

## Success Criteria

- Keyword extraction accuracy > 90%
- ATS compatibility detection works for common issues
- Tailored resumes maintain original meaning while improving keyword match
- Resume versions are properly stored and retrievable
- Optimization suggestions are actionable and specific
- ATS score correlates with actual ATS performance
- Performance is acceptable (< 5s for full optimization)
- Documentation is clear with examples

## Future Enhancements (Phase 3.5)

- A/B testing of different resume versions
- Machine learning for keyword importance prediction
- Integration with LinkedIn profile optimization
- Resume template library
- Visual resume builder
- Multi-language support
- Industry-specific optimization rules
- Automated follow-up on resume performance

## To-dos

- [ ] Create src/resume_optimizer.py with keyword analysis and scoring
- [ ] Create src/resume_tailor.py for intelligent resume tailoring
- [ ] Create src/ats_analyzer.py for ATS compatibility checking
- [ ] Create src/resume_versions.py for version management
- [ ] Create src/optimization_formatter.py for output formatting
- [ ] Update src/analyzer.py to include optimization analysis
- [ ] Add optimization configuration options to config.py
- [ ] Add optimization CLI commands to main.py (optimize, tailor, check-ats, list-versions)
- [ ] Update README.md with resume optimization, ATS, and versioning documentation
- [ ] Add pypdf dependency to pyproject.toml if needed
- [ ] Create .env.example entries for optimization settings
