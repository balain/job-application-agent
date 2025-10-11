"""Prompt templates for different analysis tasks."""


class PromptTemplates:
    """Collection of prompt templates for the job application agent."""
    
    @staticmethod
    def get_assessment_prompt(job_description: str, resume: str) -> str:
        """
        Generate prompt for initial job suitability assessment.
        
        Args:
            job_description: The job description text
            resume: The resume text
            
        Returns:
            Formatted prompt string
        """
        return f"""You are an expert career advisor and hiring manager. Analyze the following job description and resume to assess the candidate's suitability for the position.

JOB DESCRIPTION:
{job_description}

CANDIDATE'S RESUME:
{resume}

Please provide a comprehensive assessment with the following structure:

1. SUITABILITY RATING: Rate the candidate's fit for this position on a scale of 1-10 (1 = not a fit, 10 = perfect fit)

2. DETAILED ANALYSIS:
   - STRENGTHS: What makes this candidate a good fit for the role
   - GAPS: What the candidate is missing or lacks compared to requirements
   - MISSING REQUIREMENTS: What key requirements are completely absent from the candidate's background

3. RECOMMENDATION: Should the candidate proceed with this application? (Yes/No)

4. CONFIDENCE LEVEL: How confident are you in this assessment? (High/Medium/Low)

Please be specific and reference concrete examples from both the job description and resume in your analysis."""

    @staticmethod
    def get_resume_improvement_prompt(job_description: str, resume: str, assessment: str) -> str:
        """
        Generate prompt for resume improvement suggestions.
        
        Args:
            job_description: The job description text
            resume: The resume text
            assessment: The previous assessment results
            
        Returns:
            Formatted prompt string
        """
        return f"""Based on the job description, resume, and assessment below, provide specific recommendations for improving the resume to better match the job requirements.

JOB DESCRIPTION:
{job_description}

CURRENT RESUME:
{resume}

PREVIOUS ASSESSMENT:
{assessment}

Please provide:

1. RESUME IMPROVEMENTS: Specific, actionable suggestions for:
   - Skills to highlight or add
   - Experience to emphasize or reframe
   - Keywords to include
   - Formatting or structure changes

2. PRIORITY CHANGES: The top 3 most important changes that would have the biggest impact

3. QUICK WINS: Simple changes that can be made immediately

Focus on making the resume more aligned with the job requirements while maintaining honesty and accuracy."""

    @staticmethod
    def get_cover_letter_prompt(job_description: str, resume: str, assessment: str) -> str:
        """
        Generate prompt for cover letter creation.
        
        Args:
            job_description: The job description text
            resume: The resume text
            assessment: The previous assessment results
            
        Returns:
            Formatted prompt string
        """
        return f"""Write a compelling cover letter for this job application based on the job description, resume, and assessment.

JOB DESCRIPTION:
{job_description}

CANDIDATE'S RESUME:
{resume}

ASSESSMENT:
{assessment}

The cover letter should:

1. Be professional and engaging (3-4 paragraphs)
2. Highlight the most relevant qualifications and experiences
3. Address any gaps or concerns from the assessment
4. Show enthusiasm for the role and company
5. Include a strong opening and closing
6. Be tailored specifically to this job description

Format the cover letter as a complete, ready-to-send document."""

    @staticmethod
    def get_interview_questions_prompt(job_description: str, resume: str, assessment: str) -> str:
        """
        Generate prompt for interview question preparation.
        
        Args:
            job_description: The job description text
            resume: The resume text
            assessment: The previous assessment results
            
        Returns:
            Formatted prompt string
        """
        return f"""Based on the job description, resume, and assessment, prepare interview questions and answers.

JOB DESCRIPTION:
{job_description}

CANDIDATE'S RESUME:
{resume}

ASSESSMENT:
{assessment}

Please provide:

1. QUESTIONS TO ASK THE HIRING MANAGER (5-7 questions):
   - Questions about the role, team, company culture
   - Questions that show interest and preparation
   - Questions that help evaluate if this is a good fit

2. ANTICIPATED INTERVIEW QUESTIONS (5-7 questions):
   - Questions the interviewer is likely to ask
   - Include both technical and behavioral questions
   - Focus on areas where the candidate might be challenged

3. SUGGESTED ANSWERS:
   - Provide strong, specific answers for each anticipated question
   - Use examples from the candidate's background
   - Address any potential weaknesses identified in the assessment

Make the questions and answers specific to this role and candidate."""

    @staticmethod
    def get_next_steps_prompt(job_description: str, resume: str, assessment: str) -> str:
        """
        Generate prompt for next steps recommendations.
        
        Args:
            job_description: The job description text
            resume: The resume text
            assessment: The previous assessment results
            
        Returns:
            Formatted prompt string
        """
        return f"""Based on the job description, resume, and assessment, provide a comprehensive action plan for applying to this position.

JOB DESCRIPTION:
{job_description}

CANDIDATE'S RESUME:
{resume}

ASSESSMENT:
{assessment}

Please provide:

1. IMMEDIATE ACTIONS (next 1-2 days):
   - Resume updates to make
   - Application materials to prepare
   - Research to conduct

2. SHORT-TERM PREPARATION (next week):
   - Skills to practice or learn
   - Networking opportunities
   - Application strategy

3. LONG-TERM DEVELOPMENT (next month):
   - Skills to develop for this role
   - Experience to gain
   - Career development steps

4. APPLICATION STRATEGY:
   - Best way to apply (direct, referral, etc.)
   - Timeline for application
   - Follow-up approach

5. RISK MITIGATION:
   - Potential challenges and how to address them
   - Backup plans if this application doesn't work out

Make the recommendations specific, actionable, and realistic."""
