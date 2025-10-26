"""
Structured parser for LLM responses.

This module implements robust parsing of LLM responses using JSON parsing
with regex fallback mechanisms for maximum reliability.
"""

import json
import re
import logging
from typing import Dict, Any, Optional, Union
from pydantic import ValidationError

from .models import (
    JobAssessment, 
    ResumeImprovements, 
    CoverLetter, 
    InterviewQuestions, 
    NextSteps,
    RecommendationType,
    ConfidenceLevel
)
from .llm_provider import LLMProvider

logger = logging.getLogger(__name__)


class StructuredParser:
    """Parser for structured LLM responses with fallback mechanisms."""
    
    def __init__(self, llm_provider: LLMProvider):
        """Initialize the structured parser.
        
        Args:
            llm_provider: The LLM provider instance to use
        """
        self.llm = llm_provider
        self.logger = logging.getLogger(__name__)
    
    def parse_assessment_response(self, response: str) -> JobAssessment:
        """Parse assessment response with structured fallback.
        
        Args:
            response: Raw LLM response string
            
        Returns:
            JobAssessment: Parsed and validated assessment
            
        Raises:
            ValueError: If parsing fails completely
        """
        try:
            # Try JSON parsing first
            json_data = self._extract_json_from_response(response)
            if json_data:
                return JobAssessment(**json_data)
        except (json.JSONDecodeError, ValidationError, KeyError) as e:
            self.logger.warning(f"JSON parsing failed: {e}, falling back to regex")
        
        # Fallback to regex parsing
        return self._parse_assessment_regex(response)
    
    def parse_resume_improvements(self, response: str) -> ResumeImprovements:
        """Parse resume improvements response with structured fallback.
        
        Args:
            response: Raw LLM response string
            
        Returns:
            ResumeImprovements: Parsed and validated improvements
        """
        try:
            # Try JSON parsing first
            json_data = self._extract_json_from_response(response)
            if json_data:
                return ResumeImprovements(**json_data)
        except (json.JSONDecodeError, ValidationError, KeyError) as e:
            self.logger.warning(f"JSON parsing failed: {e}, falling back to regex")
        
        # Fallback to regex parsing
        return self._parse_improvements_regex(response)
    
    def parse_cover_letter(self, response: str) -> CoverLetter:
        """Parse cover letter response.
        
        Args:
            response: Raw LLM response string
            
        Returns:
            CoverLetter: Parsed and validated cover letter
        """
        try:
            json_data = self._extract_json_from_response(response)
            if json_data:
                return CoverLetter(**json_data)
        except (json.JSONDecodeError, ValidationError, KeyError) as e:
            self.logger.warning(f"JSON parsing failed: {e}, falling back to regex")
        
        return self._parse_cover_letter_regex(response)
    
    def parse_interview_questions(self, response: str) -> InterviewQuestions:
        """Parse interview questions response.
        
        Args:
            response: Raw LLM response string
            
        Returns:
            InterviewQuestions: Parsed and validated questions
        """
        try:
            json_data = self._extract_json_from_response(response)
            if json_data:
                return InterviewQuestions(**json_data)
        except (json.JSONDecodeError, ValidationError, KeyError) as e:
            self.logger.warning(f"JSON parsing failed: {e}, falling back to regex")
        
        return self._parse_interview_questions_regex(response)
    
    def parse_next_steps(self, response: str) -> NextSteps:
        """Parse next steps response.
        
        Args:
            response: Raw LLM response string
            
        Returns:
            NextSteps: Parsed and validated next steps
        """
        try:
            json_data = self._extract_json_from_response(response)
            if json_data:
                return NextSteps(**json_data)
        except (json.JSONDecodeError, ValidationError, KeyError) as e:
            self.logger.warning(f"JSON parsing failed: {e}, falling back to regex")
        
        return self._parse_next_steps_regex(response)
    
    def _extract_json_from_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Extract JSON data from LLM response.
        
        Args:
            response: Raw LLM response string
            
        Returns:
            Dict containing parsed JSON data, or None if not found
        """
        # Look for JSON blocks in various formats
        json_patterns = [
            r'```json\s*(\{.*?\})\s*```',  # Markdown JSON blocks
            r'```\s*(\{.*?\})\s*```',      # Generic code blocks
            r'(\{.*?\})',                  # Any JSON object
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, response, re.DOTALL)
            for match in matches:
                try:
                    return json.loads(match.strip())
                except json.JSONDecodeError:
                    continue
        
        return None
    
    def _parse_assessment_regex(self, response: str) -> JobAssessment:
        """Fallback regex parsing for assessment.
        
        Args:
            response: Raw LLM response string
            
        Returns:
            JobAssessment: Parsed assessment from regex
        """
        # Extract rating
        rating_match = re.search(r'(?:rating|score|suitability)[:\s]*(\d+)', response, re.IGNORECASE)
        rating = int(rating_match.group(1)) if rating_match else 5
        
        # Extract strengths
        strengths_patterns = [
            r'strengths?[:\s]*(.*?)(?=\n\s*(?:gaps?|weaknesses?|areas for improvement)|$)',
            r'strengths?[:\s]*(.*?)(?=\n\n|\n[A-Z])',
            r'what.*?good[:\s]*(.*?)(?=\n\n|\n[A-Z])',
        ]
        strengths = self._extract_section_content(response, strengths_patterns, "Not specified")
        
        # Extract gaps/weaknesses
        gaps_patterns = [
            r'(?:gaps?|weaknesses?|areas for improvement)[:\s]*(.*?)(?=\n\s*(?:missing|requirements?)|$)',
            r'(?:gaps?|weaknesses?)[:\s]*(.*?)(?=\n\n|\n[A-Z])',
            r'what.*?improve[:\s]*(.*?)(?=\n\n|\n[A-Z])',
        ]
        gaps = self._extract_section_content(response, gaps_patterns, "Not specified")
        
        # Extract missing requirements
        missing_patterns = [
            r'(?:missing|requirements?)[:\s]*(.*?)(?=\n\s*(?:recommendation|should)|$)',
            r'(?:missing|requirements?)[:\s]*(.*?)(?=\n\n|\n[A-Z])',
            r'what.*?missing[:\s]*(.*?)(?=\n\n|\n[A-Z])',
        ]
        missing_requirements = self._extract_section_content(response, missing_patterns, "Not specified")
        
        # Clean up the extracted content
        if missing_requirements != "Not specified":
            missing_requirements = missing_requirements.replace("REQUIREMENTS:", "").strip()
        
        # Extract recommendation
        rec_patterns = [
            r'(?:recommendation|should|advice)[:\s]*(yes|no|maybe|unknown)',
            r'(?:proceed|apply)[:\s]*(yes|no|maybe|unknown)',
            r'(?:fit|suitable)[:\s]*(yes|no|maybe|unknown)',
        ]
        recommendation = self._extract_recommendation(response, rec_patterns)
        
        # Extract confidence
        conf_patterns = [
            r'(?:confidence|certainty)[:\s]*(high|medium|low)',
            r'(?:confidence level)[:\s]*(high|medium|low)',
            r'(?:sure|certain)[:\s]*(high|medium|low)',
        ]
        confidence = self._extract_confidence(response, conf_patterns)
        
        return JobAssessment(
            rating=rating,
            strengths=strengths,
            gaps=gaps,
            missing_requirements=missing_requirements,
            recommendation=recommendation,
            confidence=confidence
        )
    
    def _parse_improvements_regex(self, response: str) -> ResumeImprovements:
        """Fallback regex parsing for resume improvements.
        
        Args:
            response: Raw LLM response string
            
        Returns:
            ResumeImprovements: Parsed improvements from regex
        """
        # Extract keyword suggestions
        keyword_patterns = [
            r'(?:keywords? to add|keywords?)[:\s]*(.*?)(?=\n\s*(?:formatting|content|priority)|$)',
            r'(?:keywords?|terms?)[:\s]*(.*?)(?=\n\n|\n[A-Z])',
            r'(?:add|include)[:\s]*(.*?)(?=\n\n|\n[A-Z])',
        ]
        keywords = self._extract_list_content(response, keyword_patterns)
        
        # Clean up keywords (remove section headers)
        keywords = [kw for kw in keywords if not kw.lower().endswith(':') and len(kw.strip()) > 2]
        
        # Extract formatting fixes
        format_patterns = [
            r'(?:formatting fixes|formatting|format)[:\s]*(.*?)(?=\n\s*(?:content|priority)|$)',
            r'(?:formatting fixes|formatting|format)[:\s]*(.*?)(?=\n\n|\n[A-Z])',
            r'(?:fix|correct)[:\s]*(.*?)(?=\n\n|\n[A-Z])',
        ]
        formatting = self._extract_list_content(response, format_patterns)
        formatting = [fmt for fmt in formatting if not fmt.lower().endswith(':') and len(fmt.strip()) > 2]
        
        # Extract content enhancements
        content_patterns = [
            r'(?:content enhancements|content|enhance|improve)[:\s]*(.*?)(?=\n\s*(?:priority|quick)|$)',
            r'(?:content enhancements|content|enhance|improve)[:\s]*(.*?)(?=\n\n|\n[A-Z])',
            r'(?:better|stronger)[:\s]*(.*?)(?=\n\n|\n[A-Z])',
        ]
        content_enhancements = self._extract_list_content(response, content_patterns)
        content_enhancements = [ce for ce in content_enhancements if not ce.lower().endswith(':') and len(ce.strip()) > 2]
        
        # Extract priority changes (top 3)
        priority_patterns = [
            r'(?:priority changes|priority|important|top)[:\s]*(.*?)(?=\n\s*(?:quick|win)|$)',
            r'(?:priority changes|priority|important|top)[:\s]*(.*?)(?=\n\n|\n[A-Z])',
            r'(?:focus|concentrate)[:\s]*(.*?)(?=\n\n|\n[A-Z])',
        ]
        priority_changes = self._extract_list_content(response, priority_patterns)[:3]  # Limit to 3
        priority_changes = [pc for pc in priority_changes if not pc.lower().endswith(':') and len(pc.strip()) > 2]
        
        # Extract quick wins
        quick_patterns = [
            r'(?:quick wins|quick|easy|simple)[:\s]*(.*?)(?=\n\n|\n[A-Z]|$)',
            r'(?:quick wins|quick|easy|simple)[:\s]*(.*?)(?=\n\n|\n[A-Z])',
            r'(?:immediate|fast)[:\s]*(.*?)(?=\n\n|\n[A-Z])',
        ]
        quick_wins = self._extract_list_content(response, quick_patterns)
        quick_wins = [qw for qw in quick_wins if not qw.lower().endswith(':') and len(qw.strip()) > 2]
        
        return ResumeImprovements(
            keyword_suggestions=keywords,
            section_improvements={},  # Would need more complex parsing
            formatting_fixes=formatting,
            content_enhancements=content_enhancements,
            priority_changes=priority_changes,
            quick_wins=quick_wins
        )
    
    def _parse_cover_letter_regex(self, response: str) -> CoverLetter:
        """Fallback regex parsing for cover letter.
        
        Args:
            response: Raw LLM response string
            
        Returns:
            CoverLetter: Parsed cover letter from regex
        """
        # Extract opening paragraph
        opening_patterns = [
            r'(?:dear|to)[:\s]*(.*?)(?=\n\n|\n[A-Z])',
            r'(?:opening|greeting)[:\s]*(.*?)(?=\n\n|\n[A-Z])',
        ]
        opening = self._extract_section_content(response, opening_patterns, "Dear Hiring Manager,")
        
        # Extract body paragraphs
        body_patterns = [
            r'(?:body|main|content)[:\s]*(.*?)(?=\n\s*(?:closing|sincerely)|$)',
            r'(?:paragraph|text)[:\s]*(.*?)(?=\n\n|\n[A-Z])',
        ]
        body = self._extract_section_content(response, body_patterns, "I am writing to express my interest...")
        
        # Extract closing paragraph
        closing_patterns = [
            r'(?:closing|sincerely|thank)[:\s]*(.*?)(?=\n\n|\n[A-Z]|$)',
            r'(?:end|conclusion)[:\s]*(.*?)(?=\n\n|\n[A-Z]|$)',
        ]
        closing = self._extract_section_content(response, closing_patterns, "Thank you for your consideration.")
        
        # Combine into full letter
        full_letter = f"{opening}\n\n{body}\n\n{closing}"
        
        return CoverLetter(
            opening=opening,
            body=body,
            closing=closing,
            full_letter=full_letter
        )
    
    def _parse_interview_questions_regex(self, response: str) -> InterviewQuestions:
        """Fallback regex parsing for interview questions.
        
        Args:
            response: Raw LLM response string
            
        Returns:
            InterviewQuestions: Parsed questions from regex
        """
        # Extract questions for employer
        employer_patterns = [
            r'(?:questions to ask employer|ask|questions? for)[:\s]*(.*?)(?=\n\s*(?:anticipated|expected)|$)',
            r'(?:questions to ask employer|employer|hiring manager)[:\s]*(.*?)(?=\n\n|\n[A-Z])',
            r'(?:questions to ask)[:\s]*(.*?)(?=\n\n|\n[A-Z])',
        ]
        questions_for_employer = self._extract_list_content(response, employer_patterns)
        questions_for_employer = [q for q in questions_for_employer if not q.lower().endswith(':') and len(q.strip()) > 2]
        
        # Extract anticipated questions
        anticipated_patterns = [
            r'(?:anticipated questions|anticipated|expected|might ask)[:\s]*(.*?)(?=\n\s*(?:suggested|answers)|$)',
            r'(?:anticipated questions|anticipated|expected|might ask)[:\s]*(.*?)(?=\n\n|\n[A-Z])',
            r'(?:interviewer|they)[:\s]*(.*?)(?=\n\n|\n[A-Z])',
        ]
        anticipated_questions = self._extract_list_content(response, anticipated_patterns)
        anticipated_questions = [q for q in anticipated_questions if not q.lower().endswith(':') and len(q.strip()) > 2]
        
        # Extract suggested answers
        answers_patterns = [
            r'(?:suggested answers|answers?|responses?)[:\s]*(.*?)(?=\n\n|\n[A-Z]|$)',
            r'(?:suggested answers|answers?|responses?)[:\s]*(.*?)(?=\n\n|\n[A-Z])',
            r'(?:suggest|recommend)[:\s]*(.*?)(?=\n\n|\n[A-Z])',
        ]
        suggested_answers = self._extract_list_content(response, answers_patterns)
        suggested_answers = [a for a in suggested_answers if not a.lower().endswith(':') and len(a.strip()) > 2]
        
        return InterviewQuestions(
            questions_for_employer=questions_for_employer,
            anticipated_questions=anticipated_questions,
            suggested_answers=suggested_answers
        )
    
    def _parse_next_steps_regex(self, response: str) -> NextSteps:
        """Fallback regex parsing for next steps.
        
        Args:
            response: Raw LLM response string
            
        Returns:
            NextSteps: Parsed next steps from regex
        """
        # Extract immediate actions
        immediate_patterns = [
            r'(?:immediate actions|immediate|now|today)[:\s]*(.*?)(?=\n\s*(?:short.?term|week)|$)',
            r'(?:immediate actions|immediate|now|today)[:\s]*(.*?)(?=\n\n|\n[A-Z])',
            r'(?:first|start)[:\s]*(.*?)(?=\n\n|\n[A-Z])',
        ]
        immediate_actions = self._extract_list_content(response, immediate_patterns)
        immediate_actions = [ia for ia in immediate_actions if not ia.lower().endswith(':') and len(ia.strip()) > 2]
        
        # Extract short-term preparation
        short_term_patterns = [
            r'(?:short.?term preparation|short.?term|week|soon)[:\s]*(.*?)(?=\n\s*(?:long.?term|month)|$)',
            r'(?:short.?term preparation|short.?term|week|soon)[:\s]*(.*?)(?=\n\n|\n[A-Z])',
            r'(?:prepare|ready)[:\s]*(.*?)(?=\n\n|\n[A-Z])',
        ]
        short_term_preparation = self._extract_list_content(response, short_term_patterns)
        short_term_preparation = [st for st in short_term_preparation if not st.lower().endswith(':') and len(st.strip()) > 2]
        
        # Extract long-term development
        long_term_patterns = [
            r'(?:long.?term development|long.?term|month|future)[:\s]*(.*?)(?=\n\s*(?:application|strategy)|$)',
            r'(?:long.?term development|long.?term|month|future)[:\s]*(.*?)(?=\n\n|\n[A-Z])',
            r'(?:develop|improve)[:\s]*(.*?)(?=\n\n|\n[A-Z])',
        ]
        long_term_development = self._extract_list_content(response, long_term_patterns)
        long_term_development = [lt for lt in long_term_development if not lt.lower().endswith(':') and len(lt.strip()) > 2]
        
        # Extract application strategy
        strategy_patterns = [
            r'(?:application strategy|strategy|approach|plan)[:\s]*(.*?)(?=\n\s*(?:risk|mitigate)|$)',
            r'(?:application strategy|strategy|approach|plan)[:\s]*(.*?)(?=\n\n|\n[A-Z])',
            r'(?:apply|application)[:\s]*(.*?)(?=\n\n|\n[A-Z])',
        ]
        application_strategy = self._extract_list_content(response, strategy_patterns)
        application_strategy = [as_item for as_item in application_strategy if not as_item.lower().endswith(':') and len(as_item.strip()) > 2]
        
        # Extract risk mitigation
        risk_patterns = [
            r'(?:risk mitigation|risk|challenge|mitigate)[:\s]*(.*?)(?=\n\n|\n[A-Z]|$)',
            r'(?:risk mitigation|risk|challenge|mitigate)[:\s]*(.*?)(?=\n\n|\n[A-Z])',
            r'(?:avoid|prevent)[:\s]*(.*?)(?=\n\n|\n[A-Z])',
        ]
        risk_mitigation = self._extract_list_content(response, risk_patterns)
        risk_mitigation = [rm for rm in risk_mitigation if not rm.lower().endswith(':') and len(rm.strip()) > 2]
        
        return NextSteps(
            immediate_actions=immediate_actions,
            short_term_preparation=short_term_preparation,
            long_term_development=long_term_development,
            application_strategy=application_strategy,
            risk_mitigation=risk_mitigation
        )
    
    def _extract_section_content(self, response: str, patterns: list, default: str) -> str:
        """Extract content from a section using multiple patterns.
        
        Args:
            response: Raw LLM response string
            patterns: List of regex patterns to try
            default: Default value if no pattern matches
            
        Returns:
            Extracted content or default
        """
        for pattern in patterns:
            match = re.search(pattern, response, re.IGNORECASE | re.DOTALL)
            if match:
                content = match.group(1).strip()
                if content and len(content) > 10:  # Ensure meaningful content
                    return content
        return default
    
    def _extract_list_content(self, response: str, patterns: list) -> list:
        """Extract list content from response using multiple patterns.
        
        Args:
            response: Raw LLM response string
            patterns: List of regex patterns to try
            
        Returns:
            List of extracted items
        """
        for pattern in patterns:
            match = re.search(pattern, response, re.IGNORECASE | re.DOTALL)
            if match:
                content = match.group(1).strip()
                if content:
                    # Split by common list separators and clean up
                    items = re.split(r'[•\-\*\n]+', content)
                    items = [item.strip() for item in items if item.strip() and len(item.strip()) > 2]
                    if items:
                        return items
        return []
    
    def _extract_recommendation(self, response: str, patterns: list) -> RecommendationType:
        """Extract recommendation from response.
        
        Args:
            response: Raw LLM response string
            patterns: List of regex patterns to try
            
        Returns:
            RecommendationType enum value
        """
        for pattern in patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                rec_text = match.group(1).lower().strip()
                if rec_text in ['yes', 'y', 'proceed', 'apply']:
                    return RecommendationType.YES
                elif rec_text in ['no', 'n', 'don\'t', 'avoid']:
                    return RecommendationType.NO
                elif rec_text in ['maybe', 'unknown', 'unclear']:
                    return RecommendationType.UNKNOWN
        
        # Default to UNKNOWN if no clear recommendation found
        return RecommendationType.UNKNOWN
    
    def _extract_confidence(self, response: str, patterns: list) -> ConfidenceLevel:
        """Extract confidence level from response.
        
        Args:
            response: Raw LLM response string
            patterns: List of regex patterns to try
            
        Returns:
            ConfidenceLevel enum value
        """
        for pattern in patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                conf_text = match.group(1).lower().strip()
                if conf_text in ['high', 'very', 'extremely']:
                    return ConfidenceLevel.HIGH
                elif conf_text in ['medium', 'moderate', 'somewhat']:
                    return ConfidenceLevel.MEDIUM
                elif conf_text in ['low', 'little', 'not']:
                    return ConfidenceLevel.LOW
        
        # Default to MEDIUM if no clear confidence found
        return ConfidenceLevel.MEDIUM
    
    def validate_parsing_success(self, response: str, expected_fields: list) -> bool:
        """Validate that parsing was successful by checking for expected fields.
        
        Args:
            response: Raw LLM response string
            expected_fields: List of fields that should be present
            
        Returns:
            True if parsing appears successful, False otherwise
        """
        try:
            json_data = self._extract_json_from_response(response)
            if json_data:
                return all(field in json_data for field in expected_fields)
        except:
            pass
        
        # Check if regex parsing would find key information
        if 'rating' in expected_fields:
            rating_match = re.search(r'(?:rating|score)[:\s]*(\d+)', response, re.IGNORECASE)
            if not rating_match:
                return False
        
        if 'recommendation' in expected_fields:
            rec_match = re.search(r'(?:recommendation|should)[:\s]*(yes|no)', response, re.IGNORECASE)
            if not rec_match:
                return False
        
        return True
