"""Simple MCP server implementation for job application agent."""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional

try:
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("MCP library not available. Please install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

from .parsers import JobDescriptionParser, ResumeParser
from .llm_provider import create_llm_provider
from .analyzer import JobApplicationAnalyzer
from .output import OutputFormatter
from config import Config


class SimpleJobApplicationMCPServer:
    """Simple MCP server for job application analysis."""
    
    def __init__(self):
        self.server = Server("job-application-agent")
        self.llm_provider = None
        self.analyzer = None
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up MCP server handlers."""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="analyze_job_application",
                    description="Analyze a job application by comparing job description with resume content",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "job_description": {
                                "type": "string",
                                "description": "The job description text or URL"
                            },
                            "resume_content": {
                                "type": "string", 
                                "description": "The resume content text"
                            }
                        },
                        "required": ["job_description", "resume_content"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls."""
            try:
                if name == "analyze_job_application":
                    return await self._analyze_job_application(arguments)
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]
            except Exception as e:
                return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def _ensure_llm_provider(self):
        """Ensure LLM provider is initialized."""
        if self.llm_provider is None:
            self.llm_provider = create_llm_provider()
            self.analyzer = JobApplicationAnalyzer(self.llm_provider)
    
    async def _analyze_job_application(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Analyze job application."""
        job_description = arguments["job_description"]
        resume_content = arguments["resume_content"]
        
        # Parse job description if it's a URL
        if job_description.startswith(("http://", "https://")):
            job_description = JobDescriptionParser.parse(job_description)
        
        await self._ensure_llm_provider()
        
        # Perform analysis synchronously
        try:
            results = self.analyzer.analyze_application(job_description, resume_content)
            
            # Format results as text
            output = []
            assessment = results['assessment']
            
            output.append(f"**JOB APPLICATION ANALYSIS RESULTS**\n")
            output.append(f"Suitability Rating: {assessment.rating}/10")
            output.append(f"Recommendation: {assessment.recommendation}")
            output.append(f"Confidence Level: {assessment.confidence}\n")
            
            output.append(f"**STRENGTHS:**\n{assessment.strengths}\n")
            output.append(f"**AREAS FOR IMPROVEMENT:**\n{assessment.gaps}\n")
            output.append(f"**MISSING REQUIREMENTS:**\n{assessment.missing_requirements}\n")
            
            if results.get('materials'):
                materials = results['materials']
                output.append(f"**RESUME IMPROVEMENTS:**\n{materials.resume_improvements}\n")
                output.append(f"**COVER LETTER:**\n{materials.cover_letter}\n")
                output.append(f"**INTERVIEW QUESTIONS:**\n{materials.questions_for_employer}\n")
                output.append(f"**ANTICIPATED QUESTIONS:**\n{materials.anticipated_questions}\n")
                output.append(f"**SUGGESTED ANSWERS:**\n{materials.suggested_answers}\n")
                output.append(f"**NEXT STEPS:**\n{materials.next_steps}")
            
            return [TextContent(type="text", text="\n".join(output))]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Analysis error: {str(e)}")]
    
    async def run(self):
        """Run the MCP server."""
        try:
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name="job-application-agent",
                        server_version="1.0.0",
                        capabilities=self.server.get_capabilities(
                            notification_options=None,
                            experimental_capabilities=None,
                        ),
                    ),
                )
        except Exception as e:
            print(f"MCP Server Error: {e}", file=sys.stderr)
            raise


async def main():
    """Main entry point for MCP server."""
    server = SimpleJobApplicationMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
