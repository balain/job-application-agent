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
from src.ats_analyzer import ATSAnalyzer
from src.resume_scorer import ResumeScorer
from src.file_parser import ResumeFileParser
from src.analytics_dashboard import AnalyticsDashboard
from src.personalized_recommendation_engine import PersonalizedRecommendationEngine
from src.career_progression_tracker import CareerProgressionTracker
from src.industry_trend_analyzer import IndustryTrendAnalyzer
from src.langchain_analyzer import LangChainJobApplicationAnalyzer
from src.langchain_observability import get_metrics, reset_metrics, export_metrics

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
      
      # Resume optimization
      python main.py --analyze-resume resume.pdf
      python main.py --analyze-resume resume.docx --job job.txt
      python main.py --score-resume resume.pdf --job job.txt
      
      # Career analytics
      python main.py --career-analytics --resume resume.pdf
      python main.py --career-dashboard --resume resume.pdf --email user@example.com
      python main.py --industry-trends --resume resume.pdf
      
      # LangChain integration
      python main.py --job job.txt --resume resume.pdf --langchain
      python main.py --job job.txt --resume resume.pdf --langchain --enable-rag --enable-tailoring
      python main.py --langchain-metrics
      python main.py --export-metrics metrics.json
      
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
    
    # Resume optimization commands
    parser.add_argument(
        "--analyze-resume",
        metavar="RESUME_FILE",
        help="Analyze resume for ATS compatibility and optimization"
    )
    
    parser.add_argument(
        "--score-resume",
        metavar="RESUME_FILE",
        help="Calculate comprehensive resume score"
    )
    
    parser.add_argument(
        "--optimization-output",
        metavar="FILE",
        help="Save optimization results to file"
    )
    
    # Career analytics commands
    parser.add_argument(
        "--career-analytics",
        action="store_true",
        help="Generate comprehensive career analytics"
    )
    
    parser.add_argument(
        "--career-dashboard",
        action="store_true",
        help="Display career analytics dashboard"
    )
    
    parser.add_argument(
        "--industry-trends",
        action="store_true",
        help="Analyze industry trends and market insights"
    )
    
    parser.add_argument(
        "--career-output",
        metavar="FILE",
        help="Save career analytics results to file"
    )

    # LangChain integration options
    parser.add_argument(
        "--langchain",
        action="store_true",
        help="Use LangChain-enhanced analysis with structured outputs and advanced features"
    )

    parser.add_argument(
        "--enable-rag",
        action="store_true",
        help="Enable RAG (Retrieval-Augmented Generation) for similar application insights"
    )

    parser.add_argument(
        "--enable-tailoring",
        action="store_true",
        help="Enable iterative resume tailoring using LangGraph workflows"
    )

    parser.add_argument(
        "--langchain-metrics",
        action="store_true",
        help="Show LangChain operation metrics and exit"
    )

    parser.add_argument(
        "--reset-metrics",
        action="store_true",
        help="Reset LangChain metrics and exit"
    )

    parser.add_argument(
        "--export-metrics",
        metavar="FILE",
        help="Export LangChain metrics to file"
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

        # Handle LangChain metrics commands
        if args.langchain_metrics:
            metrics = get_metrics()
            console.print(Panel(str(metrics), title="LangChain Metrics"))
            sys.exit(0)

        if args.reset_metrics:
            reset_metrics()
            console.print("[green]LangChain metrics reset successfully[/green]")
            sys.exit(0)

        if args.export_metrics:
            file_path = export_metrics(args.export_metrics)
            console.print(f"[green]Metrics exported to {file_path}[/green]")
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

        # Handle resume optimization commands
        if args.analyze_resume:
            console.print("[blue]Starting resume analysis...[/blue]")
            
            ats_analyzer = ATSAnalyzer()
            job_description = ""
            
            # Get job description if provided
            if args.job:
                try:
                    job_description, _ = validate_inputs(args.job, "")
                except Exception as e:
                    console.print(f"[yellow]Warning: Could not parse job description: {e}[/yellow]")
                    console.print("[yellow]Continuing with resume analysis only...[/yellow]")
            
            # Analyze resume
            optimization = ats_analyzer.analyze_resume(args.analyze_resume, job_description)
            
            # Display results
            console.print("\n[bold cyan]RESUME OPTIMIZATION ANALYSIS[/bold cyan]")
            console.print("=" * 50)
            
            # Overall score
            ats_score = optimization.ats_compatibility.overall_score * 100
            console.print(f"\n[bold]Overall ATS Score: {ats_score:.1f}/100[/bold]")
            console.print(f"Compatibility Level: {optimization.ats_compatibility.compatibility_level.value.title()}")
            
            # Priority fixes
            if optimization.priority_fixes:
                console.print("\n[bold red]Priority Fixes:[/bold red]")
                for i, fix in enumerate(optimization.priority_fixes, 1):
                    console.print(f"  {i}. {fix}")
            
            # Content improvements
            if optimization.content_improvements:
                console.print("\n[bold yellow]Content Improvements:[/bold yellow]")
                for i, improvement in enumerate(optimization.content_improvements, 1):
                    console.print(f"  {i}. {improvement}")
            
            # Formatting suggestions
            if optimization.formatting_suggestions:
                console.print("\n[bold blue]Formatting Suggestions:[/bold blue]")
                for i, suggestion in enumerate(optimization.formatting_suggestions, 1):
                    console.print(f"  {i}. {suggestion}")
            
            # Keyword additions
            if optimization.keyword_additions:
                console.print("\n[bold green]Keywords to Add:[/bold green]")
                for i, keyword in enumerate(optimization.keyword_additions, 1):
                    console.print(f"  {i}. {keyword}")
            
            # Save results if requested
            if args.optimization_output:
                import json
                with open(args.optimization_output, 'w', encoding='utf-8') as f:
                    json.dump(optimization.model_dump(), f, indent=2, ensure_ascii=False, default=str)
                console.print(f"\n[green]✓ Optimization results saved to: {args.optimization_output}[/green]")
            
            sys.exit(0)
        
        if args.score_resume:
            console.print("[blue]Calculating resume score...[/blue]")
            
            resume_scorer = ResumeScorer()
            job_description = ""
            
            # Get job description if provided
            if args.job:
                try:
                    job_description, _ = validate_inputs(args.job, "")
                except Exception as e:
                    console.print(f"[yellow]Warning: Could not parse job description: {e}[/yellow]")
                    console.print("[yellow]Continuing with resume scoring only...[/yellow]")
            
            # Score resume
            score = resume_scorer.score_resume("", job_description, args.score_resume)
            
            # Display results
            console.print("\n[bold cyan]RESUME SCORING RESULTS[/bold cyan]")
            console.print("=" * 40)
            
            console.print(f"\n[bold]Total Score: {score.total_score:.1f}/100[/bold]")
            console.print(f"ATS Compatibility: {score.ats_score:.1f}/100")
            console.print(f"Content Quality: {score.content_score:.1f}/100")
            console.print(f"Formatting: {score.formatting_score:.1f}/100")
            console.print(f"Keyword Optimization: {score.keyword_score:.1f}/100")
            console.print(f"Experience Relevance: {score.experience_score:.1f}/100")
            console.print(f"Skills Match: {score.skills_score:.1f}/100")
            
            # Overall assessment
            if score.total_score >= 80:
                console.print(f"\n[bold green]Excellent resume! Score: {score.total_score:.1f}/100[/bold green]")
            elif score.total_score >= 70:
                console.print(f"\n[bold yellow]Good resume with room for improvement. Score: {score.total_score:.1f}/100[/bold yellow]")
            elif score.total_score >= 60:
                console.print(f"\n[bold orange]Fair resume, significant improvements needed. Score: {score.total_score:.1f}/100[/bold orange]")
            else:
                console.print(f"\n[bold red]Resume needs major improvements. Score: {score.total_score:.1f}/100[/bold red]")
            
            # Save results if requested
            if args.optimization_output:
                import json
                with open(args.optimization_output, 'w', encoding='utf-8') as f:
                    json.dump(score.model_dump(), f, indent=2, ensure_ascii=False, default=str)
                console.print(f"\n[green]✓ Scoring results saved to: {args.optimization_output}[/green]")
            
            sys.exit(0)

        # Handle career analytics commands
        if args.career_analytics or args.career_dashboard or args.industry_trends:
            if not args.resume:
                console.print("[red]Error: --resume is required for career analytics[/red]")
                sys.exit(1)
            
            console.print("[blue]Starting career analytics...[/blue]")
            
            # Parse resume file
            file_parser = ResumeFileParser()
            parse_result = file_parser.parse_file(args.resume)
            
            if not parse_result.parse_success:
                console.print(f"[red]Failed to parse resume: {parse_result.error_message}[/red]")
                sys.exit(1)
            
            # Create user profile
            user_profile = {
                'user_id': args.email or 'anonymous',
                'email': args.email or 'anonymous@example.com',
                'resume_content': parse_result.content,
                'skills': [],  # Will be extracted from resume
                'current_title': 'Software Developer',  # Will be extracted from resume
                'location': 'United States'
            }
            
            # Extract basic info from resume
            resume_content = parse_result.content.lower()
            
            # Extract skills (simple keyword matching)
            skill_keywords = ['python', 'javascript', 'java', 'sql', 'react', 'node', 'aws', 'docker', 'kubernetes', 'git', 'linux', 'machine learning', 'data analysis']
            user_skills = [skill for skill in skill_keywords if skill in resume_content]
            user_profile['skills'] = user_skills
            
            # Extract job title (first line or common patterns)
            lines = parse_result.content.split('\n')
            if lines:
                first_line = lines[0].strip()
                if len(first_line) < 50:  # Reasonable length for job title
                    user_profile['current_title'] = first_line
            
            if args.career_dashboard:
                # Create and display analytics dashboard
                dashboard_creator = AnalyticsDashboard()
                dashboard = dashboard_creator.create_dashboard(user_profile)
                dashboard_creator.display_dashboard(dashboard)
                
                # Save results if requested
                if args.career_output:
                    dashboard_creator.export_dashboard(dashboard, args.career_output)
                    console.print(f"\n[green]✓ Dashboard exported to: {args.career_output}[/green]")
            
            elif args.career_analytics:
                # Generate career analytics
                recommendation_engine = PersonalizedRecommendationEngine()
                career_analytics = recommendation_engine.create_career_analytics(user_profile)
                
                # Display results
                console.print("\n[bold cyan]CAREER ANALYTICS[/bold cyan]")
                console.print("=" * 40)
                
                console.print(f"\n[bold]Career Score: {career_analytics.career_score:.1f}/100[/bold]")
                console.print(f"Current Stage: {career_analytics.career_progression.current_stage.value.replace('_', ' ').title()}")
                console.print(f"Next Stage: {career_analytics.career_progression.next_stage.value.replace('_', ' ').title()}")
                console.print(f"Progression Score: {career_analytics.career_progression.progression_score:.1%}")
                console.print(f"Time to Next Stage: {career_analytics.career_progression.time_to_next_stage} months")
                console.print(f"Market Position: {career_analytics.market_position}")
                
                # Skill gaps
                if career_analytics.career_progression.skill_gaps:
                    console.print(f"\n[bold red]Skill Gaps:[/bold red]")
                    for gap in career_analytics.career_progression.skill_gaps:
                        console.print(f"  • {gap}")
                
                # Top recommendations
                high_priority_recs = [rec for rec in career_analytics.personalized_recommendations if rec.priority == 'high']
                if high_priority_recs:
                    console.print(f"\n[bold yellow]High Priority Recommendations:[/bold yellow]")
                    for rec in high_priority_recs[:3]:
                        console.print(f"  • {rec.title}")
                
                # Save results if requested
                if args.career_output:
                    import json
                    with open(args.career_output, 'w', encoding='utf-8') as f:
                        json.dump(career_analytics.model_dump(), f, indent=2, ensure_ascii=False, default=str)
                    console.print(f"\n[green]✓ Career analytics saved to: {args.career_output}[/green]")
            
            elif args.industry_trends:
                # Analyze industry trends
                trend_analyzer = IndustryTrendAnalyzer()
                industry_insights = trend_analyzer.analyze_industry_trends(user_profile)
                skill_trends = trend_analyzer.analyze_skill_trends(user_profile['skills'])
                
                # Display results
                console.print("\n[bold cyan]INDUSTRY TRENDS ANALYSIS[/bold cyan]")
                console.print("=" * 40)
                
                for insight in industry_insights:
                    console.print(f"\n[bold]{insight.industry.value.title()} Industry[/bold]")
                    console.print(f"Growth Rate: {insight.growth_rate}%")
                    console.print(f"Top Skills: {', '.join(insight.top_skills[:5])}")
                    console.print(f"Outlook: {insight.future_outlook}")
                
                if skill_trends:
                    console.print(f"\n[bold]Skill Trends:[/bold]")
                    for trend in skill_trends[:5]:
                        trend_icon = "📈" if trend.trend_direction.value == "rising" else "📊" if trend.trend_direction.value == "stable" else "📉"
                        console.print(f"  {trend_icon} {trend.skill_name}: {trend.demand_score:.1%} demand, {trend.growth_rate:.1f}% growth")
                
                # Save results if requested
                if args.career_output:
                    import json
                    results = {
                        'industry_insights': [insight.model_dump() for insight in industry_insights],
                        'skill_trends': [trend.model_dump() for trend in skill_trends]
                    }
                    with open(args.career_output, 'w', encoding='utf-8') as f:
                        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
                    console.print(f"\n[green]✓ Industry trends saved to: {args.career_output}[/green]")
            
            sys.exit(0)

        # Validate that job and resume are provided for CLI mode
        if not args.job or not args.resume:
            # Check if this is a resume optimization or career analytics command
            if args.analyze_resume or args.score_resume or args.career_analytics or args.career_dashboard or args.industry_trends:
                # These commands don't require both job and resume
                pass
            else:
                console.print(
                    "[red]Error: --job and --resume are required for CLI mode[/red]"
                )
                console.print("Use --mcp-server to run in MCP server mode")
                console.print("Or use --analyze-resume, --score-resume, or career analytics commands")
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
        
        # Choose analyzer based on LangChain flag
        if args.langchain:
            analyzer = LangChainJobApplicationAnalyzer(llm_provider)
            results = analyzer.analyze_application(
                job_description=job_description,
                resume=resume_text,
                enable_rag=args.enable_rag,
                enable_tailoring=args.enable_tailoring
            )
        else:
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
