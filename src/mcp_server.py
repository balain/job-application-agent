"""MCP server implementation for job application agent."""

import asyncio
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
    print(
        "MCP library not available. Please install with: pip install mcp",
        file=sys.stderr,
    )
    sys.exit(1)

from .parsers import JobDescriptionParser
from .llm_provider import create_llm_provider
from .analyzer import JobApplicationAnalyzer
from .output import OutputFormatter


class JobApplicationMCPServer:
    """MCP server for job application analysis."""

    def __init__(self):
        self.server = Server("job-application-agent")
        self.llm_provider = None
        self.analyzer = None
        self.formatter = OutputFormatter()
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
                                "description": "The job description text or URL",
                            },
                            "resume_content": {
                                "type": "string",
                                "description": "The resume content text",
                            },
                            "provider": {
                                "type": "string",
                                "enum": ["claude", "ollama"],
                                "description": "LLM provider to use (optional, auto-detect if not specified)",
                            },
                        },
                        "required": ["job_description", "resume_content"],
                    },
                ),
                Tool(
                    name="get_resume_improvements",
                    description="Get specific suggestions for improving a resume for a particular job",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "job_description": {
                                "type": "string",
                                "description": "The job description text",
                            },
                            "resume_content": {
                                "type": "string",
                                "description": "The resume content text",
                            },
                        },
                        "required": ["job_description", "resume_content"],
                    },
                ),
                Tool(
                    name="generate_cover_letter",
                    description="Generate a tailored cover letter for a specific job application",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "job_description": {
                                "type": "string",
                                "description": "The job description text",
                            },
                            "resume_content": {
                                "type": "string",
                                "description": "The resume content text",
                            },
                        },
                        "required": ["job_description", "resume_content"],
                    },
                ),
                Tool(
                    name="prepare_interview_questions",
                    description="Prepare interview questions and answers for a job application",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "job_description": {
                                "type": "string",
                                "description": "The job description text",
                            },
                            "resume_content": {
                                "type": "string",
                                "description": "The resume content text",
                            },
                        },
                        "required": ["job_description", "resume_content"],
                    },
                ),
                Tool(
                    name="get_next_steps",
                    description="Get a personalized action plan for applying to a job",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "job_description": {
                                "type": "string",
                                "description": "The job description text",
                            },
                            "resume_content": {
                                "type": "string",
                                "description": "The resume content text",
                            },
                        },
                        "required": ["job_description", "resume_content"],
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls."""
            try:
                if name == "analyze_job_application":
                    return await self._analyze_job_application(arguments)
                elif name == "get_resume_improvements":
                    return await self._get_resume_improvements(arguments)
                elif name == "generate_cover_letter":
                    return await self._generate_cover_letter(arguments)
                elif name == "prepare_interview_questions":
                    return await self._prepare_interview_questions(arguments)
                elif name == "get_next_steps":
                    return await self._get_next_steps(arguments)
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]
            except Exception as e:
                return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def _ensure_llm_provider(self, provider: Optional[str] = None):
        """Ensure LLM provider is initialized."""
        if self.llm_provider is None:
            self.llm_provider = create_llm_provider(provider)
            self.analyzer = JobApplicationAnalyzer(self.llm_provider)

    async def _analyze_job_application(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Analyze job application."""
        job_description = arguments["job_description"]
        resume_content = arguments["resume_content"]
        provider = arguments.get("provider")

        # Parse job description if it's a URL
        if job_description.startswith(("http://", "https://")):
            job_description = JobDescriptionParser.parse(job_description)

        await self._ensure_llm_provider(provider)

        # Perform analysis (run in thread pool to avoid blocking)
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None, self.analyzer.analyze_application, job_description, resume_content
        )

        # Format results as text
        output = []
        assessment = results["assessment"]

        output.append("**JOB APPLICATION ANALYSIS RESULTS**\n")
        output.append(f"Suitability Rating: {assessment.rating}/10")
        output.append(f"Recommendation: {assessment.recommendation}")
        output.append(f"Confidence Level: {assessment.confidence}\n")

        output.append(f"**STRENGTHS:**\n{assessment.strengths}\n")
        output.append(f"**AREAS FOR IMPROVEMENT:**\n{assessment.gaps}\n")
        output.append(f"**MISSING REQUIREMENTS:**\n{assessment.missing_requirements}\n")

        if results.get("materials"):
            materials = results["materials"]
            output.append(
                f"**RESUME IMPROVEMENTS:**\n{materials.resume_improvements}\n"
            )
            output.append(f"**COVER LETTER:**\n{materials.cover_letter}\n")
            output.append(
                f"**INTERVIEW QUESTIONS:**\n{materials.questions_for_employer}\n"
            )
            output.append(
                f"**ANTICIPATED QUESTIONS:**\n{materials.anticipated_questions}\n"
            )
            output.append(f"**SUGGESTED ANSWERS:**\n{materials.suggested_answers}\n")
            output.append(f"**NEXT STEPS:**\n{materials.next_steps}")

        return [TextContent(type="text", text="\n".join(output))]

    async def _get_resume_improvements(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Get resume improvement suggestions."""
        job_description = arguments["job_description"]
        resume_content = arguments["resume_content"]

        if job_description.startswith(("http://", "https://")):
            job_description = JobDescriptionParser.parse(job_description)

        await self._ensure_llm_provider()

        # Get initial assessment (run in thread pool)
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None, self.analyzer.analyze_application, job_description, resume_content
        )

        if results.get("materials"):
            return [
                TextContent(type="text", text=results["materials"].resume_improvements)
            ]
        else:
            return [
                TextContent(
                    type="text",
                    text="No resume improvements generated - application not recommended",
                )
            ]

    async def _generate_cover_letter(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Generate cover letter."""
        job_description = arguments["job_description"]
        resume_content = arguments["resume_content"]

        if job_description.startswith(("http://", "https://")):
            job_description = JobDescriptionParser.parse(job_description)

        await self._ensure_llm_provider()

        # Get initial assessment (run in thread pool)
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None, self.analyzer.analyze_application, job_description, resume_content
        )

        if results.get("materials"):
            return [TextContent(type="text", text=results["materials"].cover_letter)]
        else:
            return [
                TextContent(
                    type="text",
                    text="No cover letter generated - application not recommended",
                )
            ]

    async def _prepare_interview_questions(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Prepare interview questions."""
        job_description = arguments["job_description"]
        resume_content = arguments["resume_content"]

        if job_description.startswith(("http://", "https://")):
            job_description = JobDescriptionParser.parse(job_description)

        await self._ensure_llm_provider()

        # Get initial assessment (run in thread pool)
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None, self.analyzer.analyze_application, job_description, resume_content
        )

        if results.get("materials"):
            materials = results["materials"]
            output = []
            output.append(
                f"**QUESTIONS TO ASK THE HIRING MANAGER:**\n{materials.questions_for_employer}\n"
            )
            output.append(
                f"**ANTICIPATED INTERVIEW QUESTIONS:**\n{materials.anticipated_questions}\n"
            )
            output.append(f"**SUGGESTED ANSWERS:**\n{materials.suggested_answers}")
            return [TextContent(type="text", text="\n".join(output))]
        else:
            return [
                TextContent(
                    type="text",
                    text="No interview questions prepared - application not recommended",
                )
            ]

    async def _get_next_steps(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Get next steps action plan."""
        job_description = arguments["job_description"]
        resume_content = arguments["resume_content"]

        if job_description.startswith(("http://", "https://")):
            job_description = JobDescriptionParser.parse(job_description)

        await self._ensure_llm_provider()

        # Get initial assessment (run in thread pool)
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None, self.analyzer.analyze_application, job_description, resume_content
        )

        if results.get("materials"):
            return [TextContent(type="text", text=results["materials"].next_steps)]
        else:
            return [
                TextContent(
                    type="text",
                    text="No next steps generated - application not recommended",
                )
            ]

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
    server = JobApplicationMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
