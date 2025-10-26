"""Job Application Agent - CLI entry point."""

import argparse
import sys

from rich.console import Console
from rich.panel import Panel

from config import Config
from src.parsers import validate_inputs
from src.llm_provider import create_llm_provider
from src.analyzer import JobApplicationAnalyzer
from src.output import OutputFormatter
from src.cache import resume_cache

# console = Console()
console = Console(file=sys.stderr)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AI agent to analyze job applications and provide recommendations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
    Examples:
      # CLI mode
      python main.py --job "https://example.com/job" --resume resume.docx
      python main.py --job job.txt --resume resume.md --provider claude
      python main.py --job job.txt --resume resume.docx --output results.json
      
      # Application tracking
      python main.py --job job.txt --resume resume.docx --track --email user@example.com --name "Jane Doe"
      python main.py --list-applications
      python main.py --update-status applied --application-id 1
      python main.py --delete-application 1
      python main.py --analytics
      
      # MCP server mode
      python main.py --mcp-server
        """,
    )

    parser.add_argument(
        "--job",
        "-j",
        help="Job description file path or URL (not required for MCP server mode)",
    )

    parser.add_argument(
        "--resume", "-r", help="Resume file path (not required for MCP server mode)"
    )

    parser.add_argument(
        "--provider",
        "-p",
        choices=["claude", "ollama"],
        help="LLM provider to use (auto-detect if not specified)",
    )

    parser.add_argument(
        "--output",
        "-o",
        help="Output file path (optional). If specified, saves JSON to file while also displaying console output",
    )

    parser.add_argument(
        "--format",
        "-f",
        choices=["text", "json"],
        default="text",
        help="Output format for console display (default: text). JSON file output is always in JSON format",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    parser.add_argument(
        "--clear-cache", action="store_true", help="Clear resume cache and exit"
    )

    parser.add_argument(
        "--cache-stats", action="store_true", help="Show cache statistics and exit"
    )

    parser.add_argument(
        "--export-cache", metavar="OUTPUT", help="Export all cached data to JSON file"
    )

    parser.add_argument(
        "--mcp-server",
        action="store_true",
        help="Run as MCP server for AI assistant integration",
    )

    # Application tracking commands
    parser.add_argument(
        "--track", action="store_true", help="Track this application in the database"
    )

    parser.add_argument(
        "--email", help="Email address for application tracking (required with --track)"
    )

    parser.add_argument(
        "--name", help="Your name for application tracking (required with --track)"
    )

    parser.add_argument(
        "--list-applications", action="store_true", help="List all tracked applications"
    )

    parser.add_argument(
        "--update-status",
        metavar="STATUS",
        help="Update application status (draft, applied, under_review, interview_scheduled, interview_completed, offer_received, rejected, withdrawn, accepted)",
    )

    parser.add_argument(
        "--application-id", type=int, help="Application ID for status updates"
    )

    parser.add_argument(
        "--delete-application",
        type=int,
        metavar="APPLICATION_ID",
        help="Delete an application and all related records (requires confirmation)",
    )

    parser.add_argument(
        "--force-delete",
        action="store_true",
        help="Skip confirmation prompt when deleting applications (use with caution)",
    )

    parser.add_argument(
        "--analytics",
        action="store_true",
        help="Show application analytics and insights",
    )

    parser.add_argument(
        "--export-data", metavar="FILE", help="Export all application data to JSON file"
    )

    args = parser.parse_args()

    try:
        # Handle cache management commands
        if args.clear_cache:
            resume_cache.clear_cache()
            console.print("[green]Cache cleared successfully[/green]")
            sys.exit(0)

        if args.export_cache:
            resume_cache.export_cache(args.export_cache)
            sys.exit(0)

        if args.cache_stats:
            resume_cache.display_cache_info()
            sys.exit(0)

        if args.mcp_server:
            console.print("[blue]Starting MCP server...[/blue]")
            from src.fallback_mcp_server import main as mcp_main

            mcp_main()
            sys.exit(0)

        # Handle application tracking commands
        if args.list_applications:
            from src.database_manager import db_manager
            from src.database_schema import ApplicationStatus

            console.print("[blue]Listing tracked applications...[/blue]")
            applications = db_manager.get_applications(limit=100)

            if not applications:
                console.print("[yellow]No applications found.[/yellow]")
            else:
                from rich.table import Table

                table = Table(title="Tracked Applications")
                table.add_column("ID", style="cyan")
                table.add_column("Company", style="white")
                table.add_column("Job Title", style="white")
                table.add_column("Status", style="green")
                table.add_column("Applied Date", style="blue")

                for app in applications:
                    status_color = (
                        "green"
                        if app["status"]
                        in [
                            ApplicationStatus.OFFER_RECEIVED,
                            ApplicationStatus.ACCEPTED,
                        ]
                        else "yellow"
                        if app["status"] == ApplicationStatus.UNDER_REVIEW
                        else "red"
                    )
                    applied_date = (
                        app["applied_date"].strftime("%Y-%m-%d")
                        if app["applied_date"]
                        else "N/A"
                    )
                    table.add_row(
                        str(app["id"]),
                        app["company_name"],
                        app["job_title"],
                        f"[{status_color}]{app['status'].value}[/{status_color}]",
                        applied_date,
                    )

                console.print(table)
            sys.exit(0)

        if args.update_status:
            from src.database_manager import db_manager
            from src.database_schema import ApplicationStatus

            if not args.application_id:
                console.print(
                    "[red]Error: --application-id is required when updating status[/red]"
                )
                sys.exit(1)

            try:
                status = ApplicationStatus(args.update_status)
            except ValueError:
                console.print(
                    f"[red]Error: Invalid status '{args.update_status}'. Valid options: {', '.join([s.value for s in ApplicationStatus])}[/red]"
                )
                sys.exit(1)

            success = db_manager.update_application_status(args.application_id, status)
            if success:
                console.print(
                    f"[green]✓ Application {args.application_id} status updated to {status.value}[/green]"
                )
            else:
                console.print(
                    f"[red]Error: Application {args.application_id} not found[/red]"
                )
                sys.exit(1)
            sys.exit(0)

        if args.delete_application:
            from src.database_manager import db_manager

            application_id = args.delete_application

            # Get application details for confirmation
            applications = db_manager.get_applications(
                limit=1000
            )  # Get all to find the one we want
            target_app = None
            for app in applications:
                if app["id"] == application_id:
                    target_app = app
                    break

            if not target_app:
                console.print(
                    f"[red]Error: Application {application_id} not found[/red]"
                )
                sys.exit(1)

            # Show application details
            console.print("[yellow]Application to delete:[/yellow]")
            console.print(f"  ID: {target_app['id']}")
            console.print(f"  Company: {target_app['company_name']}")
            console.print(f"  Job Title: {target_app['job_title']}")
            console.print(f"  Status: {target_app['status'].value}")
            console.print(f"  Notes: {target_app['notes'] or 'None'}")

            # Confirmation prompt
            if not args.force_delete:
                console.print(
                    "\n[red]⚠️  WARNING: This will permanently delete the application and all related records![/red]"
                )
                console.print(
                    "[red]This includes analysis results, interviews, and any associated data.[/red]"
                )

                try:
                    confirm = input("\nType 'DELETE' to confirm deletion: ").strip()
                    if confirm != "DELETE":
                        console.print("[yellow]Deletion cancelled.[/yellow]")
                        sys.exit(0)
                except KeyboardInterrupt:
                    console.print("\n[yellow]Deletion cancelled.[/yellow]")
                    sys.exit(0)

            # Perform deletion
            console.print(f"[blue]Deleting application {application_id}...[/blue]")
            success = db_manager.delete_application(application_id)

            if success:
                console.print(
                    f"[green]✓ Application {application_id} and all related records deleted successfully[/green]"
                )
            else:
                console.print(
                    f"[red]Error: Failed to delete application {application_id}[/red]"
                )
                sys.exit(1)
            sys.exit(0)

        if args.analytics:
            from src.database_manager import db_manager

            console.print("[blue]Application Analytics[/blue]")
            analytics = db_manager.get_analytics_summary()

            analytics_text = f"""
Total Applications: {analytics["total_applications"]}
Success Rate: {analytics["success_rate"]}%
Recent Applications (30 days): {analytics["recent_applications"]}

Status Breakdown:
"""
            for status, count in analytics["status_breakdown"].items():
                analytics_text += f"  • {status.replace('_', ' ').title()}: {count}\n"

            panel = Panel(
                analytics_text.strip(), title="Analytics Summary", border_style="blue"
            )
            console.print(panel)
            sys.exit(0)

        if args.export_data:
            from src.database_manager import db_manager
            import json

            console.print("[blue]Exporting application data...[/blue]")
            export_data = db_manager.export_data()

            with open(args.export_data, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)

            console.print(f"[green]✓ Data exported to: {args.export_data}[/green]")
            sys.exit(0)

        # Validate that job and resume are provided for CLI mode
        if not args.job or not args.resume:
            console.print(
                "[red]Error: --job and --resume are required for CLI mode[/red]"
            )
            console.print("Use --mcp-server to run in MCP server mode")
            sys.exit(1)

        # Display header
        console.print(
            Panel.fit(
                "[bold blue]Job Application Agent[/bold blue]\n"
                "AI-powered job application analysis and recommendations",
                border_style="blue",
            )
        )

        # Validate configuration
        if not Config.validate():
            console.print(
                "[red]Error: No LLM providers configured. Please set up your API keys.[/red]"
            )
            console.print("See .env.example for configuration details.")
            sys.exit(1)

        # Parse inputs
        console.print("[blue]Parsing inputs...[/blue]")
        job_description, resume_text = validate_inputs(args.job, args.resume)

        # Initialize LLM provider
        console.print("[blue]Initializing LLM provider...[/blue]")
        try:
            llm_provider = create_llm_provider(args.provider)
        except ValueError as e:
            console.print(f"[red]Error initializing LLM provider: {e}[/red]")
            sys.exit(1)

        # Perform analysis
        console.print("[blue]Starting analysis...[/blue]")
        analyzer = JobApplicationAnalyzer(llm_provider)
        results = analyzer.analyze_application(job_description, resume_text)

        # Display results
        formatter = OutputFormatter(verbose=args.verbose)
        formatter.display_results(results, args.format)

        # Save results if requested (always saves as JSON when output file specified)
        if args.output:
            formatter.save_results(results, args.output)
            console.print(f"[green]✓ Results also saved to: {args.output}[/green]")

        # Track application if requested
        if args.track:
            if not args.email or not args.name:
                console.print(
                    "[red]Error: --email and --name are required when using --track[/red]"
                )
                sys.exit(1)

            from src.database_manager import db_manager
            from src.database_schema import ApplicationStatus

            # Extract company name from job description (simple heuristic)
            company_name = "Unknown Company"
            lines = job_description.split("\n")
            for line in lines[:10]:  # Check first 10 lines
                if any(
                    keyword in line.lower()
                    for keyword in ["company", "corporation", "inc", "llc", "ltd"]
                ):
                    company_name = line.strip()
                    break

            # Extract job title (first line or look for common patterns)
            job_title = "Unknown Position"
            first_line = lines[0].strip()
            if first_line and len(first_line) < 100:  # Reasonable length for job title
                job_title = first_line

            # Determine initial status based on analysis result
            initial_status = (
                ApplicationStatus.APPLIED
                if results.should_proceed
                else ApplicationStatus.DRAFT
            )

            try:
                application = db_manager.create_application(
                    person_email=args.email,
                    person_name=args.name,
                    company_name=company_name,
                    job_title=job_title,
                    status=initial_status,
                    notes=f"Analysis rating: {results.assessment.rating}/10, Recommendation: {results.assessment.recommendation}",
                )

                console.print(
                    f"[green]✓ Application tracked with ID: {application.id}[/green]"
                )
                console.print(f"[blue]Company: {company_name}[/blue]")
                console.print(f"[blue]Position: {job_title}[/blue]")
                console.print(f"[blue]Status: {initial_status.value}[/blue]")

                # Save analysis result to database
                if results.assessment:
                    analysis_data = {
                        "rating": results.assessment.rating,
                        "recommendation": results.assessment.recommendation,
                        "confidence": results.assessment.confidence,
                        "strengths": results.assessment.strengths,
                        "gaps": results.assessment.gaps,
                        "missing_requirements": results.assessment.missing_requirements,
                        "resume_improvements": results.resume_improvements.model_dump()
                        if results.resume_improvements
                        else None,
                        "cover_letter": results.cover_letter.model_dump()
                        if results.cover_letter
                        else None,
                        "interview_questions": results.interview_questions.model_dump()
                        if results.interview_questions
                        else None,
                        "next_steps": results.next_steps.model_dump()
                        if results.next_steps
                        else None,
                    }

                    db_manager.save_analysis_result(application.id, analysis_data)
                    console.print("[green]✓ Analysis results saved to database[/green]")

            except Exception as e:
                console.print(f"[red]Error tracking application: {e}[/red]")
                console.print(
                    "[yellow]Analysis completed but application not tracked[/yellow]"
                )

        # Exit with appropriate code
        if results.should_proceed:
            console.print(
                "\n[green]✓ Analysis complete - Application recommended![/green]"
            )
            sys.exit(0)
        else:
            console.print(
                "\n[yellow]⚠ Analysis complete - Application not recommended[/yellow]"
            )
            sys.exit(1)

    except KeyboardInterrupt:
        console.print("\n[yellow]Analysis interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        if args.verbose:
            import traceback

            console.print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
