#!/usr/bin/env python3
"""Example test script to demonstrate the job application agent."""

import os
import tempfile
from pathlib import Path

# Create sample files for testing
def create_sample_files():
    """Create sample job description and resume files for testing."""
    
    # Sample job description
    job_description = """
Software Engineer - Full Stack Developer

Company: TechCorp Inc.
Location: San Francisco, CA
Type: Full-time

Job Description:
We are seeking a talented Full Stack Developer to join our growing engineering team. 
The ideal candidate will have experience with modern web technologies and a passion 
for building scalable applications.

Responsibilities:
- Develop and maintain web applications using React, Node.js, and Python
- Design and implement RESTful APIs
- Collaborate with cross-functional teams
- Write clean, maintainable code
- Participate in code reviews and technical discussions

Requirements:
- 3+ years of experience in full-stack development
- Proficiency in JavaScript, Python, and SQL
- Experience with React, Node.js, and PostgreSQL
- Knowledge of cloud platforms (AWS, GCP, or Azure)
- Strong problem-solving and communication skills
- Bachelor's degree in Computer Science or related field

Preferred Qualifications:
- Experience with Docker and Kubernetes
- Knowledge of microservices architecture
- Previous startup experience
- Open source contributions
"""

    # Sample resume
    resume = """
John Doe
Software Engineer
Email: john.doe@email.com
Phone: (555) 123-4567
LinkedIn: linkedin.com/in/johndoe

PROFESSIONAL SUMMARY
Experienced software engineer with 4 years of experience in full-stack development. 
Passionate about building scalable web applications and working with modern technologies.

TECHNICAL SKILLS
- Programming Languages: JavaScript, Python, Java, SQL
- Frontend: React, HTML5, CSS3, TypeScript
- Backend: Node.js, Express.js, Django, Flask
- Databases: PostgreSQL, MongoDB, Redis
- Cloud: AWS (EC2, S3, Lambda), Docker
- Tools: Git, Jenkins, JIRA, VS Code

WORK EXPERIENCE

Software Engineer | TechStart Inc. | 2021 - Present
- Developed and maintained web applications serving 10,000+ users
- Built RESTful APIs using Node.js and Express
- Implemented responsive frontend components with React
- Collaborated with cross-functional teams in agile environment
- Reduced application load time by 40% through optimization

Junior Developer | WebSolutions LLC | 2020 - 2021
- Created and maintained client websites
- Developed backend services using Python and Django
- Worked with PostgreSQL databases
- Participated in code reviews and testing

EDUCATION
Bachelor of Science in Computer Science
University of California, Berkeley | 2016 - 2020

PROJECTS
- E-commerce Platform: Full-stack application with React and Node.js
- Task Management App: Built with Python and Django
- Weather API: RESTful service with real-time data
"""

    # Create temporary files
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(job_description)
        job_file = f.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(resume)
        resume_file = f.name
    
    return job_file, resume_file

def main():
    """Run the example test."""
    print("Creating sample files...")
    job_file, resume_file = create_sample_files()
    
    print(f"Job description file: {job_file}")
    print(f"Resume file: {resume_file}")
    
    print("\nTo test the agent, run:")
    print(f"python main.py --job '{job_file}' --resume '{resume_file}'")
    print("\nNote: You'll need to set up your API keys in a .env file first.")
    
    # Clean up
    try:
        os.unlink(job_file)
        os.unlink(resume_file)
    except:
        pass

if __name__ == "__main__":
    main()
