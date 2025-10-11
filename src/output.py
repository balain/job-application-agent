"""Output formatting for the job application agent."""

import json
from typing import Dict, Any, Optional
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.markdown import Markdown

from .analyzer import AssessmentResult, ApplicationMaterials

console = Console()


class OutputFormatter:
    """Formats and displays analysis results."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
    
    def display_results(self, results: Dict[str, Any], output_format: str = "text") -> None:
        """
        Display analysis results in the specified format.
        
        Args:
            results: Analysis results dictionary
            output_format: Output format ('text' or 'json')
        """
        if output_format == "json":
            self._display_json(results)
        else:
            self._display_text(results)
    
    def _display_text(self, results: Dict[str, Any]) -> None:
        """Display results in plain text format."""
        assessment = results['assessment']
        materials = results.get('materials')
        should_proceed = results['should_proceed']
        
        # Header
        print("\n" + "="*80)
        print("JOB APPLICATION ANALYSIS RESULTS")
        print("="*80)
        
        # Assessment Summary
        self._display_assessment_summary_text(assessment, should_proceed)
        
        # Detailed Assessment
        self._display_detailed_assessment_text(assessment)
        
        # Application Materials (if available)
        if materials:
            self._display_application_materials_text(materials)
        else:
            print("\nNo additional materials generated - application not recommended")
    
    def _display_assessment_summary_text(self, assessment: AssessmentResult, should_proceed: bool) -> None:
        """Display assessment summary in plain text."""
        print("\nASSESSMENT SUMMARY")
        print("-" * 50)
        print(f"Suitability Rating: {assessment.rating}/10")
        print(f"Recommendation: {assessment.recommendation}")
        print(f"Confidence Level: {assessment.confidence}")
    
    def _display_assessment_summary(self, assessment: AssessmentResult, should_proceed: bool) -> None:
        """Display assessment summary."""
        # Rating with color coding
        rating_color = "green" if assessment.rating >= 8 else "yellow" if assessment.rating >= 6 else "red"
        rating_text = f"[{rating_color}]{assessment.rating}/10[/{rating_color}]"
        
        # Recommendation with color
        rec_color = "green" if should_proceed else "red"
        rec_text = f"[{rec_color}]{assessment.recommendation}[/{rec_color}]"
        
        # Create summary table
        table = Table(title="Assessment Summary", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")
        
        table.add_row("Suitability Rating", rating_text)
        table.add_row("Recommendation", rec_text)
        table.add_row("Confidence Level", assessment.confidence)
        
        console.print(table)
    
    def _display_detailed_assessment_text(self, assessment: AssessmentResult) -> None:
        """Display detailed assessment breakdown in plain text."""
        print("\nDETAILED ASSESSMENT")
        print("=" * 50)
        
        # Strengths
        print("\nSTRENGTHS:")
        print("-" * 20)
        print(assessment.strengths)
        
        # Gaps
        print("\nAREAS FOR IMPROVEMENT:")
        print("-" * 30)
        print(assessment.gaps)
        
        # Missing Requirements
        print("\nMISSING REQUIREMENTS:")
        print("-" * 25)
        print(assessment.missing_requirements)
    
    def _display_detailed_assessment(self, assessment: AssessmentResult) -> None:
        """Display detailed assessment breakdown."""
        console.print("\n[bold cyan]DETAILED ASSESSMENT[/bold cyan]")
        
        # Strengths
        strengths_panel = Panel(
            assessment.strengths,
            title="[green]Strengths[/green]",
            border_style="green"
        )
        console.print(strengths_panel)
        
        # Gaps
        gaps_panel = Panel(
            assessment.gaps,
            title="[yellow]Areas for Improvement[/yellow]",
            border_style="yellow"
        )
        console.print(gaps_panel)
        
        # Missing Requirements
        missing_panel = Panel(
            assessment.missing_requirements,
            title="[red]Missing Requirements[/red]",
            border_style="red"
        )
        console.print(missing_panel)
    
    def _display_application_materials_text(self, materials: ApplicationMaterials) -> None:
        """Display generated application materials in plain text."""
        print("\nAPPLICATION MATERIALS")
        print("=" * 50)
        
        # Resume Improvements
        print("\nRESUME IMPROVEMENT SUGGESTIONS:")
        print("-" * 35)
        print(materials.resume_improvements)
        
        # Cover Letter
        print("\nCOVER LETTER:")
        print("-" * 15)
        print(materials.cover_letter)
        
        # Interview Questions
        print("\nQUESTIONS TO ASK THE HIRING MANAGER:")
        print("-" * 40)
        print(materials.questions_for_employer)
        
        print("\nANTICIPATED INTERVIEW QUESTIONS:")
        print("-" * 35)
        print(materials.anticipated_questions)
        
        # Suggested Answers
        print("\nSUGGESTED INTERVIEW ANSWERS:")
        print("-" * 32)
        print(materials.suggested_answers)
        
        # Next Steps
        print("\nNEXT STEPS ACTION PLAN:")
        print("-" * 25)
        print(materials.next_steps)
    
    def _display_application_materials(self, materials: ApplicationMaterials) -> None:
        """Display generated application materials."""
        console.print("\n[bold cyan]APPLICATION MATERIALS[/bold cyan]")
        
        # Resume Improvements
        resume_panel = Panel(
            materials.resume_improvements,
            title="[blue]Resume Improvement Suggestions[/blue]",
            border_style="blue"
        )
        console.print(resume_panel)
        
        # Cover Letter
        cover_letter_panel = Panel(
            materials.cover_letter,
            title="[blue]Cover Letter[/blue]",
            border_style="blue"
        )
        console.print(cover_letter_panel)
        
        # Interview Questions
        questions_panel = Panel(
            f"{materials.questions_for_employer}\n\n{materials.anticipated_questions}",
            title="[blue]Interview Questions[/blue]",
            border_style="blue"
        )
        console.print(questions_panel)
        
        # Suggested Answers
        answers_panel = Panel(
            materials.suggested_answers,
            title="[blue]Suggested Interview Answers[/blue]",
            border_style="blue"
        )
        console.print(answers_panel)
        
        # Next Steps
        next_steps_panel = Panel(
            materials.next_steps,
            title="[blue]Next Steps Action Plan[/blue]",
            border_style="blue"
        )
        console.print(next_steps_panel)
    
    def _display_json(self, results: Dict[str, Any]) -> None:
        """Display results in JSON format."""
        # Convert results to JSON-serializable format
        json_results = {
            "assessment": {
                "rating": results['assessment'].rating,
                "strengths": results['assessment'].strengths,
                "gaps": results['assessment'].gaps,
                "missing_requirements": results['assessment'].missing_requirements,
                "recommendation": results['assessment'].recommendation,
                "confidence": results['assessment'].confidence
            },
            "should_proceed": results['should_proceed']
        }
        
        if results.get('materials'):
            json_results["materials"] = {
                "resume_improvements": results['materials'].resume_improvements,
                "cover_letter": results['materials'].cover_letter,
                "questions_for_employer": results['materials'].questions_for_employer,
                "anticipated_questions": results['materials'].anticipated_questions,
                "suggested_answers": results['materials'].suggested_answers,
                "next_steps": results['materials'].next_steps
            }
        
        console.print(json.dumps(json_results, indent=2))
    
    def save_results(self, results: Dict[str, Any], output_file: str) -> None:
        """
        Save results to a file.
        
        Args:
            results: Analysis results dictionary
            output_file: Output file path
        """
        output_path = Path(output_file)
        
        # Always save as JSON for structured data, regardless of file extension
        # This ensures consistent, parseable output for programmatic use
        self._save_json(results, output_file)
    
    def _save_json(self, results: Dict[str, Any], output_file: str) -> None:
        """Save results as JSON file."""
        json_results = {
            "assessment": {
                "rating": results['assessment'].rating,
                "strengths": results['assessment'].strengths,
                "gaps": results['assessment'].gaps,
                "missing_requirements": results['assessment'].missing_requirements,
                "recommendation": results['assessment'].recommendation,
                "confidence": results['assessment'].confidence
            },
            "should_proceed": results['should_proceed']
        }
        
        if results.get('materials'):
            json_results["materials"] = {
                "resume_improvements": results['materials'].resume_improvements,
                "cover_letter": results['materials'].cover_letter,
                "questions_for_employer": results['materials'].questions_for_employer,
                "anticipated_questions": results['materials'].anticipated_questions,
                "suggested_answers": results['materials'].suggested_answers,
                "next_steps": results['materials'].next_steps
            }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json_results, f, indent=2, ensure_ascii=False)
        
        console.print(f"[green]Results saved to: {output_file}[/green]")
    
    def _save_text(self, results: Dict[str, Any], output_file: str) -> None:
        """Save results as text file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("JOB APPLICATION ANALYSIS RESULTS\n")
            f.write("="*50 + "\n\n")
            
            assessment = results['assessment']
            f.write(f"SUITABILITY RATING: {assessment.rating}/10\n")
            f.write(f"RECOMMENDATION: {assessment.recommendation}\n")
            f.write(f"CONFIDENCE: {assessment.confidence}\n\n")
            
            f.write("STRENGTHS:\n")
            f.write(assessment.strengths + "\n\n")
            
            f.write("AREAS FOR IMPROVEMENT:\n")
            f.write(assessment.gaps + "\n\n")
            
            f.write("MISSING REQUIREMENTS:\n")
            f.write(assessment.missing_requirements + "\n\n")
            
            if results.get('materials'):
                materials = results['materials']
                f.write("RESUME IMPROVEMENTS:\n")
                f.write(materials.resume_improvements + "\n\n")
                
                f.write("COVER LETTER:\n")
                f.write(materials.cover_letter + "\n\n")
                
                f.write("INTERVIEW QUESTIONS:\n")
                f.write(materials.questions_for_employer + "\n\n")
                f.write("ANTICIPATED QUESTIONS:\n")
                f.write(materials.anticipated_questions + "\n\n")
                
                f.write("SUGGESTED ANSWERS:\n")
                f.write(materials.suggested_answers + "\n\n")
                
                f.write("NEXT STEPS:\n")
                f.write(materials.next_steps + "\n")
        
        console.print(f"[green]Results saved to: {output_file}[/green]")
