"""Job Application Agent - CLI entry point."""

import argparse
import sys
from pathlib import Path

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
  
  # MCP server mode
  python main.py --mcp-server
        """
    )
    
    parser.add_argument(
        "--job", "-j",
        help="Job description file path or URL (not required for MCP server mode)"
    )
    
    parser.add_argument(
        "--resume", "-r",
        help="Resume file path (not required for MCP server mode)"
    )
    
    parser.add_argument(
        "--provider", "-p",
        choices=["claude", "ollama"],
        help="LLM provider to use (auto-detect if not specified)"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Output file path (optional). If specified, saves JSON to file while also displaying console output"
    )
    
    parser.add_argument(
        "--format", "-f",
        choices=["text", "json"],
        default="text",
        help="Output format for console display (default: text). JSON file output is always in JSON format"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Clear resume cache and exit"
    )
    
    parser.add_argument(
        "--cache-stats",
        action="store_true",
        help="Show cache statistics and exit"
    )
    
    parser.add_argument(
        "--export-cache",
        metavar="OUTPUT",
        help="Export all cached data to JSON file"
    )
    
    parser.add_argument(
        "--mcp-server",
        action="store_true",
        help="Run as MCP server for AI assistant integration"
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
        
        # Validate that job and resume are provided for CLI mode
        if not args.job or not args.resume:
            console.print("[red]Error: --job and --resume are required for CLI mode[/red]")
            console.print("Use --mcp-server to run in MCP server mode")
            sys.exit(1)
        
        # Display header
        console.print(Panel.fit(
            "[bold blue]Job Application Agent[/bold blue]\n"
            "AI-powered job application analysis and recommendations",
            border_style="blue"
        ))
        
        # Validate configuration
        if not Config.validate():
            console.print("[red]Error: No LLM providers configured. Please set up your API keys.[/red]")
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
        
        # Exit with appropriate code
        if results.should_proceed:
            console.print("\n[green]✓ Analysis complete - Application recommended![/green]")
            sys.exit(0)
        else:
            console.print("\n[yellow]⚠ Analysis complete - Application not recommended[/yellow]")
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
