"""Output formatting for the job application agent."""

import sys
import json
from typing import Dict, Any
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .models import (
    AnalysisResult,
    JobAssessment,
    ResumeImprovements,
    CoverLetter,
    InterviewQuestions,
    NextSteps,
)

console = Console(file=sys.stderr)


class OutputFormatter:
    """Formats and displays analysis results."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def display_results(
        self, results: AnalysisResult, output_format: str = "text"
    ) -> None:
        """
        Display analysis results in the specified format.

        Args:
            results: AnalysisResult object
            output_format: Output format ('text' or 'json')
        """
        if output_format == "json":
            self._display_json(results)
        else:
            self._display_text(results)

    def _display_text(self, results: AnalysisResult) -> None:
        """Display results in plain text format."""
        if results.error_info:
            print("\n" + "=" * 80)
            print("ANALYSIS ERROR")
            print("=" * 80)
            print(f"Error: {results.error_info.user_message}")
            print(f"Category: {results.error_info.category}")
            print(f"Confidence: {results.error_info.confidence}")
            return

        assessment = results.assessment
        should_proceed = results.should_proceed

        # Header
        print("\n" + "=" * 80)
        print("JOB APPLICATION ANALYSIS RESULTS")
        print("=" * 80)

        # Assessment Summary
        self._display_assessment_summary_text(assessment, should_proceed)

        # Detailed Assessment
        self._display_detailed_assessment_text(assessment)

        # Application Materials (if available)
        if (
            results.resume_improvements
            or results.cover_letter
            or results.interview_questions
            or results.next_steps
        ):
            self._display_application_materials_text(results)
        else:
            print("\nNo additional materials generated - application not recommended")

    def _display_assessment_summary_text(
        self, assessment: JobAssessment, should_proceed: bool
    ) -> None:
        """Display assessment summary in plain text."""
        print("\nASSESSMENT SUMMARY")
        print("-" * 50)
        print(f"Suitability Rating: {assessment.rating}/10")
        print(f"Recommendation: {assessment.recommendation}")
        print(f"Confidence Level: {assessment.confidence}")

    def _display_assessment_summary(
        self, assessment: JobAssessment, should_proceed: bool
    ) -> None:
        """Display assessment summary."""
        # Rating with color coding
        rating_color = (
            "green"
            if assessment.rating >= 8
            else "yellow"
            if assessment.rating >= 6
            else "red"
        )
        rating_text = f"[{rating_color}]{assessment.rating}/10[/{rating_color}]"

        # Recommendation with color
        rec_color = "green" if should_proceed else "red"
        rec_text = f"[{rec_color}]{assessment.recommendation}[/{rec_color}]"

        # Create summary table
        table = Table(
            title="Assessment Summary", show_header=True, header_style="bold magenta"
        )
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")

        table.add_row("Suitability Rating", rating_text)
        table.add_row("Recommendation", rec_text)
        table.add_row("Confidence Level", assessment.confidence)

        console.print(table)

    def _display_detailed_assessment_text(self, assessment: JobAssessment) -> None:
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

    def _display_detailed_assessment(self, assessment: JobAssessment) -> None:
        """Display detailed assessment breakdown."""
        console.print("\n[bold cyan]DETAILED ASSESSMENT[/bold cyan]")

        # Strengths
        strengths_panel = Panel(
            assessment.strengths, title="[green]Strengths[/green]", border_style="green"
        )
        console.print(strengths_panel)

        # Gaps
        gaps_panel = Panel(
            assessment.gaps,
            title="[yellow]Areas for Improvement[/yellow]",
            border_style="yellow",
        )
        console.print(gaps_panel)

        # Missing Requirements
        missing_panel = Panel(
            assessment.missing_requirements,
            title="[red]Missing Requirements[/red]",
            border_style="red",
        )
        console.print(missing_panel)

    def _display_application_materials_text(self, results: AnalysisResult) -> None:
        """Display generated application materials in plain text."""
        print("\nAPPLICATION MATERIALS")
        print("=" * 50)

        # Resume Improvements
        if results.resume_improvements:
            print("\nRESUME IMPROVEMENT SUGGESTIONS:")
            print("-" * 35)
            self._display_resume_improvements_text(results.resume_improvements)

        # Cover Letter
        if results.cover_letter:
            print("\nCOVER LETTER:")
            print("-" * 15)
            self._display_cover_letter_text(results.cover_letter)

        # Interview Questions
        if results.interview_questions:
            print("\nINTERVIEW QUESTIONS:")
            print("-" * 20)
            self._display_interview_questions_text(results.interview_questions)

        # Next Steps
        if results.next_steps:
            print("\nNEXT STEPS ACTION PLAN:")
            print("-" * 25)
            self._display_next_steps_text(results.next_steps)

    def _display_resume_improvements_text(
        self, improvements: ResumeImprovements
    ) -> None:
        """Display resume improvements in text format."""
        if improvements.keyword_suggestions:
            print("Keywords to add:", ", ".join(improvements.keyword_suggestions))
        if improvements.section_improvements:
            print("Section improvements:")
            for section, improvement in improvements.section_improvements.items():
                print(f"  {section}: {improvement}")
        if improvements.formatting_fixes:
            print("Formatting fixes:", ", ".join(improvements.formatting_fixes))
        if improvements.content_enhancements:
            print("Content enhancements:", ", ".join(improvements.content_enhancements))
        if improvements.priority_changes:
            print("Priority changes:", ", ".join(improvements.priority_changes))
        if improvements.quick_wins:
            print("Quick wins:", ", ".join(improvements.quick_wins))

    def _display_cover_letter_text(self, cover_letter: CoverLetter) -> None:
        """Display cover letter in text format."""
        print(cover_letter.full_letter)

    def _display_interview_questions_text(self, questions: InterviewQuestions) -> None:
        """Display interview questions in text format."""
        print("QUESTIONS TO ASK THE HIRING MANAGER:")
        for i, q in enumerate(questions.questions_for_employer, 1):
            print(f"{i}. {q}")

        print("\nANTICIPATED INTERVIEW QUESTIONS:")
        for i, q in enumerate(questions.anticipated_questions, 1):
            print(f"{i}. {q}")

        print("\nSUGGESTED ANSWERS:")
        for i, a in enumerate(questions.suggested_answers, 1):
            print(f"{i}. {a}")

    def _display_next_steps_text(self, next_steps: NextSteps) -> None:
        """Display next steps in text format."""
        print("IMMEDIATE ACTIONS:")
        for i, action in enumerate(next_steps.immediate_actions, 1):
            print(f"{i}. {action}")

        print("\nSHORT-TERM PREPARATION:")
        for i, action in enumerate(next_steps.short_term_preparation, 1):
            print(f"{i}. {action}")

        print("\nLONG-TERM DEVELOPMENT:")
        for i, action in enumerate(next_steps.long_term_development, 1):
            print(f"{i}. {action}")

        print("\nAPPLICATION STRATEGY:")
        for i, strategy in enumerate(next_steps.application_strategy, 1):
            print(f"{i}. {strategy}")

        print("\nRISK MITIGATION:")
        for i, risk in enumerate(next_steps.risk_mitigation, 1):
            print(f"{i}. {risk}")

    def _display_json(self, results: AnalysisResult) -> None:
        """Display results in JSON format."""
        json_results = results.model_dump()
        console.print(json.dumps(json_results, indent=2, default=str))

        # Automatically create Markdown file when using JSON console output
        self._create_auto_markdown(json_results)

    def save_results(self, results: AnalysisResult, output_file: str) -> None:
        """
        Save results to a file.

        Args:
            results: AnalysisResult object
            output_file: Output file path
        """
        # Always save as JSON for structured data, regardless of file extension
        # This ensures consistent, parseable output for programmatic use
        self._save_json(results, output_file)

    def _save_json(self, results: AnalysisResult, output_file: str) -> None:
        """Save results as JSON file."""
        json_results = results.model_dump()

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(json_results, f, indent=2, ensure_ascii=False, default=str)

        console.print(f"[green]Results saved to: {output_file}[/green]")

        # Automatically create Markdown file from JSON
        self._create_markdown_from_json(json_results, output_file)

    def _create_markdown_from_json(
        self, json_results: Dict[str, Any], json_file: str
    ) -> None:
        """Create a Markdown file from JSON results."""

        # Create Markdown filename by replacing .json with .md
        json_path = Path(json_file)
        markdown_file = json_path.with_suffix(".md")

        with open(markdown_file, "w", encoding="utf-8") as f:
            f.write("# Job Application Analysis Results\n\n")
            f.write(f"*Generated on: {self._get_timestamp()}*\n\n")

            # Handle error case
            if json_results.get("error_info"):
                f.write("## Analysis Error\n\n")
                error_info = json_results["error_info"]
                f.write(f"**Error:** {error_info['user_message']}\n\n")
                f.write(f"**Category:** {error_info['category']}\n\n")
                f.write(f"**Confidence:** {error_info['confidence']}\n\n")
                return

            # Assessment Summary
            if json_results.get("assessment"):
                assessment = json_results["assessment"]
                f.write("## Assessment Summary\n\n")
                f.write(f"**Suitability Rating:** {assessment['rating']}/10\n\n")
                f.write(f"**Recommendation:** {assessment['recommendation']}\n\n")
                f.write(f"**Confidence Level:** {assessment['confidence']}\n\n")

                # Detailed Assessment
                f.write("## Detailed Assessment\n\n")

                f.write("### Strengths\n\n")
                f.write(f"{assessment['strengths']}\n\n")

                f.write("### Areas for Improvement\n\n")
                f.write(f"{assessment['gaps']}\n\n")

                f.write("### Missing Requirements\n\n")
                f.write(f"{assessment['missing_requirements']}\n\n")

            # Application Materials (if available)
            if (
                json_results.get("resume_improvements")
                or json_results.get("cover_letter")
                or json_results.get("interview_questions")
                or json_results.get("next_steps")
            ):
                f.write("## Application Materials\n\n")

                if json_results.get("resume_improvements"):
                    f.write("### Resume Improvement Suggestions\n\n")
                    improvements = json_results["resume_improvements"]
                    if improvements.get("keyword_suggestions"):
                        f.write(
                            "**Keywords to add:** "
                            + ", ".join(improvements["keyword_suggestions"])
                            + "\n\n"
                        )
                    if improvements.get("section_improvements"):
                        f.write("**Section improvements:**\n")
                        for section, improvement in improvements[
                            "section_improvements"
                        ].items():
                            f.write(f"- **{section}:** {improvement}\n")
                        f.write("\n")
                    if improvements.get("formatting_fixes"):
                        f.write(
                            "**Formatting fixes:** "
                            + ", ".join(improvements["formatting_fixes"])
                            + "\n\n"
                        )
                    if improvements.get("content_enhancements"):
                        f.write(
                            "**Content enhancements:** "
                            + ", ".join(improvements["content_enhancements"])
                            + "\n\n"
                        )
                    if improvements.get("priority_changes"):
                        f.write("**Priority changes:**\n")
                        for item in improvements["priority_changes"]:
                            f.write(f"- {item}\n")
                        f.write("\n")
                    if improvements.get("quick_wins"):
                        f.write("**Quick wins:**\n")
                        for item in improvements["quick_wins"]:
                            f.write(f"- {item}\n")
                        f.write("\n")

                if json_results.get("cover_letter"):
                    f.write("### Cover Letter\n\n")
                    f.write(f"{json_results['cover_letter']['full_letter']}\n\n")

                if json_results.get("interview_questions"):
                    f.write("### Interview Questions\n\n")
                    questions = json_results["interview_questions"]

                    f.write("#### Questions to Ask the Hiring Manager\n\n")
                    for i, q in enumerate(questions["questions_for_employer"], 1):
                        f.write(f"{i}. {q}\n")
                    f.write("\n")

                    f.write("#### Anticipated Interview Questions\n\n")
                    for i, q in enumerate(questions["anticipated_questions"], 1):
                        f.write(f"{i}. {q}\n")
                    f.write("\n")

                    f.write("#### Suggested Answers\n\n")
                    for i, a in enumerate(questions["suggested_answers"], 1):
                        f.write(f"{i}. {a}\n")
                    f.write("\n")

                if json_results.get("next_steps"):
                    f.write("### Next Steps Action Plan\n\n")
                    next_steps = json_results["next_steps"]

                    f.write("#### Immediate Actions\n\n")
                    for i, action in enumerate(next_steps["immediate_actions"], 1):
                        f.write(f"{i}. {action}\n")
                    f.write("\n")

                    f.write("#### Short-term Preparation\n\n")
                    for i, action in enumerate(next_steps["short_term_preparation"], 1):
                        f.write(f"{i}. {action}\n")
                    f.write("\n")

                    f.write("#### Long-term Development\n\n")
                    for i, action in enumerate(next_steps["long_term_development"], 1):
                        f.write(f"{i}. {action}\n")
                    f.write("\n")

                    f.write("#### Application Strategy\n\n")
                    for i, strategy in enumerate(next_steps["application_strategy"], 1):
                        f.write(f"{i}. {strategy}\n")
                    f.write("\n")

                    f.write("#### Risk Mitigation\n\n")
                    for i, risk in enumerate(next_steps["risk_mitigation"], 1):
                        f.write(f"{i}. {risk}\n")
                    f.write("\n")
            else:
                f.write("## Application Materials\n\n")
                f.write(
                    "*No additional materials generated - application not recommended*\n\n"
                )

            # Footer
            f.write("---\n\n")
            f.write("*This analysis was generated by the Job Application Agent*\n")

        console.print(f"[green]Markdown report created: {markdown_file}[/green]")

    def _create_auto_markdown(self, json_results: Dict[str, Any]) -> None:
        """Create an auto-generated Markdown file when using JSON console output."""
        from datetime import datetime

        # Create auto-generated filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        markdown_file = f"job_analysis_{timestamp}.md"

        with open(markdown_file, "w", encoding="utf-8") as f:
            f.write("# Job Application Analysis Results\n\n")
            f.write(f"*Generated on: {self._get_timestamp()}*\n\n")

            # Assessment Summary
            assessment = json_results["assessment"]
            f.write("## Assessment Summary\n\n")
            f.write(f"**Suitability Rating:** {assessment['rating']}/10\n\n")
            f.write(f"**Recommendation:** {assessment['recommendation']}\n\n")
            f.write(f"**Confidence Level:** {assessment['confidence']}\n\n")

            # Detailed Assessment
            f.write("## Detailed Assessment\n\n")

            f.write("### Strengths\n\n")
            f.write(f"{assessment['strengths']}\n\n")

            f.write("### Areas for Improvement\n\n")
            f.write(f"{assessment['gaps']}\n\n")

            f.write("### Missing Requirements\n\n")
            f.write(f"{assessment['missing_requirements']}\n\n")

            # Application Materials (if available)
            if json_results.get("materials"):
                materials = json_results["materials"]
                f.write("## Application Materials\n\n")

                f.write("### Resume Improvement Suggestions\n\n")
                f.write(f"{materials['resume_improvements']}\n\n")

                f.write("### Cover Letter\n\n")
                f.write(f"{materials['cover_letter']}\n\n")

                f.write("### Interview Questions\n\n")
                f.write("#### Questions to Ask the Hiring Manager\n\n")
                f.write(f"{materials['questions_for_employer']}\n\n")

                f.write("#### Anticipated Interview Questions\n\n")
                f.write(f"{materials['anticipated_questions']}\n\n")

                f.write("#### Suggested Answers\n\n")
                f.write(f"{materials['suggested_answers']}\n\n")

                f.write("### Next Steps Action Plan\n\n")
                f.write(f"{materials['next_steps']}\n\n")
            else:
                f.write("## Application Materials\n\n")
                f.write(
                    "*No additional materials generated - application not recommended*\n\n"
                )

            # Footer
            f.write("---\n\n")
            f.write("*This analysis was generated by the Job Application Agent*\n")

            console.print(
                f"[green]Auto-generated Markdown report: {markdown_file}[/green]"
            )

    def _get_timestamp(self) -> str:
        """Get current timestamp for report generation."""
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _save_text(self, results: Dict[str, Any], output_file: str) -> None:
        """Save results as text file."""
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("JOB APPLICATION ANALYSIS RESULTS\n")
            f.write("=" * 50 + "\n\n")

            assessment = results["assessment"]
            f.write(f"SUITABILITY RATING: {assessment.rating}/10\n")
            f.write(f"RECOMMENDATION: {assessment.recommendation}\n")
            f.write(f"CONFIDENCE: {assessment.confidence}\n\n")

            f.write("STRENGTHS:\n")
            f.write(assessment.strengths + "\n\n")

            f.write("AREAS FOR IMPROVEMENT:\n")
            f.write(assessment.gaps + "\n\n")

            f.write("MISSING REQUIREMENTS:\n")
            f.write(assessment.missing_requirements + "\n\n")

            if results.get("materials"):
                materials = results["materials"]
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
