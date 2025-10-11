"""Input parsers for job descriptions and resumes."""

import os
import re
from pathlib import Path
from typing import Optional, Union
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from docx import Document
from rich.console import Console

from .cache import resume_cache

console = Console()


class JobDescriptionParser:
    """Parser for job descriptions from files or URLs."""
    
    @staticmethod
    def parse(input_source: str) -> str:
        """
        Parse job description from file or URL.
        
        Args:
            input_source: File path or URL to job description
            
        Returns:
            Extracted job description text
            
        Raises:
            ValueError: If input source is invalid or parsing fails
        """
        if JobDescriptionParser._is_url(input_source):
            return JobDescriptionParser._parse_url(input_source)
        else:
            return JobDescriptionParser._parse_file(input_source)
    
    @staticmethod
    def _is_url(text: str) -> bool:
        """Check if input is a URL."""
        try:
            result = urlparse(text)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    @staticmethod
    def _parse_url(url: str) -> str:
        """Parse job description from URL."""
        try:
            console.print(f"[blue]Fetching job description from: {url}[/blue]")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Try to find job description content
            # Look for common job description selectors
            selectors = [
                '[class*="job-description"]',
                '[class*="description"]',
                '[id*="job-description"]',
                '[id*="description"]',
                'article',
                '.content',
                '#content'
            ]
            
            content = None
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    content = max(elements, key=len)
                    break
            
            if not content:
                content = soup.get_text()
            else:
                content = content.get_text()
            
            # Clean up the text
            content = re.sub(r'\s+', ' ', content).strip()
            
            if len(content) < 100:
                raise ValueError("Could not extract meaningful job description content")
            
            return content
            
        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch URL: {e}")
        except Exception as e:
            raise ValueError(f"Failed to parse job description from URL: {e}")
    
    @staticmethod
    def _parse_file(file_path: str) -> str:
        """Parse job description from file."""
        path = Path(file_path)
        
        if not path.exists():
            raise ValueError(f"File not found: {file_path}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            if len(content) < 50:
                raise ValueError("File appears to be empty or too short")
            
            return content
            
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(path, 'r', encoding='latin-1') as f:
                    content = f.read().strip()
                return content
            except Exception as e:
                raise ValueError(f"Failed to read file: {e}")
        except Exception as e:
            raise ValueError(f"Failed to parse file: {e}")


class ResumeParser:
    """Parser for resumes from various file formats."""
    
    @staticmethod
    def parse(file_path: str) -> str:
        """
        Parse resume from file with caching support.
        
        Args:
            file_path: Path to resume file
            
        Returns:
            Extracted resume text
            
        Raises:
            ValueError: If file cannot be parsed
        """
        # Check cache first
        cached_content = resume_cache.get_resume(file_path)
        if cached_content:
            return cached_content
        
        # Parse file if not cached
        path = Path(file_path)
        
        if not path.exists():
            raise ValueError(f"File not found: {file_path}")
        
        suffix = path.suffix.lower()
        
        if suffix == '.docx':
            content = ResumeParser._parse_docx(file_path)
        elif suffix in ['.txt', '.md', '.markdown']:
            content = ResumeParser._parse_text(file_path)
        else:
            # Try to parse as text file
            content = ResumeParser._parse_text(file_path)
        
        # Cache the parsed content
        resume_cache.set_resume(file_path, content)
        
        return content
    
    @staticmethod
    def _parse_docx(file_path: str) -> str:
        """Parse Word document resume."""
        try:
            console.print(f"[blue]Parsing Word document: {file_path}[/blue]")
            doc = Document(file_path)
            
            # Extract text from all paragraphs
            text_parts = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_parts.append(paragraph.text.strip())
            
            content = '\n'.join(text_parts)
            
            if len(content) < 50:
                raise ValueError("Document appears to be empty or too short")
            
            return content
            
        except Exception as e:
            raise ValueError(f"Failed to parse Word document: {e}")
    
    @staticmethod
    def _parse_text(file_path: str) -> str:
        """Parse text-based resume."""
        try:
            console.print(f"[blue]Parsing text file: {file_path}[/blue]")
            
            # Try UTF-8 first
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
            except UnicodeDecodeError:
                # Try with different encodings
                for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                    try:
                        with open(file_path, 'r', encoding=encoding) as f:
                            content = f.read().strip()
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    raise ValueError("Could not decode file with any supported encoding")
            
            if len(content) < 50:
                raise ValueError("File appears to be empty or too short")
            
            return content
            
        except Exception as e:
            raise ValueError(f"Failed to parse text file: {e}")


def validate_inputs(job_source: str, resume_path: str) -> tuple[str, str]:
    """
    Validate and parse both job description and resume inputs.
    
    Args:
        job_source: Job description file path or URL
        resume_path: Resume file path
        
    Returns:
        Tuple of (job_description, resume_text)
        
    Raises:
        ValueError: If inputs are invalid
    """
    try:
        job_description = JobDescriptionParser.parse(job_source)
        resume_text = ResumeParser.parse(resume_path)
        
        console.print("[green]✓ Successfully parsed inputs[/green]")
        return job_description, resume_text
        
    except Exception as e:
        console.print(f"[red]✗ Error parsing inputs: {e}[/red]")
        raise
