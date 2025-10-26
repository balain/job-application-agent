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

Please provide your assessment in the following JSON format:

```json
{{
    "rating": <integer between 1-10>,
    "strengths": "<detailed analysis of candidate strengths>",
    "gaps": "<areas where candidate lacks compared to requirements>",
    "missing_requirements": "<key requirements completely absent from candidate's background>",
    "recommendation": "<Yes/No/Unknown>",
    "confidence": "<High/Medium/Low>"
}}
```

Guidelines:
- Rating: 1 = not a fit, 10 = perfect fit
- Recommendation: "Yes" if candidate should proceed, "No" if not recommended, "Unknown" if unclear
- Confidence: "High" for clear-cut cases, "Medium" for some uncertainty, "Low" for ambiguous situations
- Be specific and reference concrete examples from both the job description and resume
- Keep responses concise but comprehensive"""

    @staticmethod
    def get_resume_improvement_prompt(
        job_description: str, resume: str, assessment: str
    ) -> str:
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

Please provide your recommendations in the following JSON format:

```json
{{
    "keywords": ["<keyword1>", "<keyword2>", "<keyword3>"],
    "sections": ["<section1>", "<section2>", "<section3>"],
    "formatting": ["<formatting1>", "<formatting2>", "<formatting3>"],
    "content": ["<content1>", "<content2>", "<content3>"],
    "priority": ["<high_priority_change1>", "<high_priority_change2>", "<high_priority_change3>"],
    "quick_wins": ["<quick_win1>", "<quick_win2>", "<quick_win3>"]
}}
```

Guidelines:
- Keywords: Important terms from job description to include
- Sections: Resume sections to add, modify, or reorganize
- Formatting: Visual or structural improvements
- Content: Specific content changes or additions
- Priority: Top 3 most impactful changes
- Quick wins: Simple changes that can be made immediately
- Focus on making the resume more aligned with job requirements while maintaining honesty"""

    @staticmethod
    def get_cover_letter_prompt(
        job_description: str, resume: str, assessment: str
    ) -> str:
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

Please provide the cover letter in the following JSON format:

```json
{{
    "opening": "<engaging opening paragraph>",
    "body": "<main content highlighting relevant qualifications>",
    "closing": "<professional closing paragraph>",
    "full_letter": "<complete cover letter ready to send>"
}}
```

Guidelines:
- Opening: Engaging first paragraph that shows enthusiasm
- Body: 2-3 paragraphs highlighting most relevant qualifications and addressing gaps
- Closing: Professional closing with call to action
- Full letter: Complete, formatted cover letter ready to send
- Be professional, engaging, and tailored specifically to this job
- Address any concerns from the assessment while maintaining honesty"""

    @staticmethod
    def get_interview_questions_prompt(
        job_description: str, resume: str, assessment: str
    ) -> str:
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

Please provide your interview preparation in the following JSON format:

```json
{{
    "for_employer": ["<question1>", "<question2>", "<question3>", "<question4>", "<question5>"],
    "anticipated": ["<question1>", "<question2>", "<question3>", "<question4>", "<question5>"],
    "suggested_answers": ["<answer1>", "<answer2>", "<answer3>", "<answer4>", "<answer5>"]
}}
```

Guidelines:
- For employer: 5-7 questions to ask the hiring manager about role, team, company culture
- Anticipated: 5-7 questions the interviewer is likely to ask (technical and behavioral)
- Suggested answers: Strong, specific answers for each anticipated question using candidate's background
- Make questions and answers specific to this role and candidate
- Address potential weaknesses identified in the assessment"""

    @staticmethod
    def get_next_steps_prompt(
        job_description: str, resume: str, assessment: str
    ) -> str:
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

Please provide your action plan in the following JSON format:

```json
{{
    "immediate_actions": ["<action1>", "<action2>", "<action3>"],
    "short_term_preparation": ["<action1>", "<action2>", "<action3>"],
    "long_term_development": ["<action1>", "<action2>", "<action3>"],
    "application_strategy": ["<strategy1>", "<strategy2>"],
    "risk_mitigation": ["<challenge1 and solution1>", "<challenge2 and solution2>"]
}}
```

Guidelines:
- immediate_actions: Actions for next 1-2 days (resume updates, application prep, research)
- short_term_preparation: Preparation for next week (skills practice, networking, application strategy)
- long_term_development: Development for next month (skills to develop, experience to gain)
- application_strategy: Best way to apply, timeline, follow-up approach
- risk_mitigation: Potential challenges and backup plans
- Make recommendations specific, actionable, and realistic"""
