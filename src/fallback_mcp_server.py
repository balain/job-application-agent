"""Fallback MCP server implementation for job application agent."""

import json
import sys
from typing import Any, Dict, List

# Simple fallback MCP server that doesn't use the complex async patterns
def create_fallback_mcp_server():
    """Create a simple fallback MCP server."""
    
    def handle_request(request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP requests."""
        try:
            method = request.get("method")
            
            # Handle initialize method (required for MCP handshake)
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "protocolVersion": "2025-06-18",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "job-application-agent",
                            "version": "1.0.0"
                        }
                    }
                }
            
            # Handle initialized notification (no response needed)
            elif method == "notifications/initialized":
                return None  # Notifications don't need responses
            
            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "tools": [
                            {
                                "name": "analyze_job_application",
                                "description": "Analyze a job application by comparing job description with resume content",
                                "inputSchema": {
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
                            }
                        ]
                    }
                }
            
            elif method == "tools/call":
                # ... your existing tools/call code ...
                params = request.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name == "analyze_job_application":
                    # Import here to avoid circular imports
                    from .parsers import JobDescriptionParser
                    from .llm_provider import create_llm_provider
                    from .analyzer import JobApplicationAnalyzer
                    
                    job_description = arguments.get("job_description", "")
                    resume_content = arguments.get("resume_content", "")
                    
                    # Parse job description if it's a URL
                    if job_description.startswith(("http://", "https://")):
                        job_description = JobDescriptionParser.parse(job_description)
                    
                    # Initialize analyzer
                    llm_provider = create_llm_provider()
                    analyzer = JobApplicationAnalyzer(llm_provider)
                    
                    # Perform analysis
                    results = analyzer.analyze_application(job_description, resume_content)
                    
                    # Format results
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
                    
                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": "\n".join(output)
                                }
                            ]
                        }
                    }
                else:
                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {
                            "code": -32601,
                            "message": f"Unknown tool: {tool_name}"
                        }
                    }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {
                        "code": -32601,
                        "message": f"Unknown method: {request.get('method')}"
                    }
                }
                
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    def run_server():
        """Run the fallback MCP server."""
        print("Starting fallback MCP server...", file=sys.stderr)
        
        try:
            while True:
                line = sys.stdin.readline()
                if not line:
                    break
                
                try:
                    request = json.loads(line.strip())
                    response = handle_request(request)

                    if response is not None:
                        print(json.dumps(response))
                        sys.stdout.flush()

                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32700,
                            "message": f"Parse error: {str(e)}"
                        }
                    }
                    print(json.dumps(error_response))
                    sys.stdout.flush()
                    
        except KeyboardInterrupt:
            print("MCP server stopped", file=sys.stderr)
        except Exception as e:
            print(f"MCP server error: {e}", file=sys.stderr)
    
    return run_server


def main():
    """Main entry point for fallback MCP server."""
    server = create_fallback_mcp_server()
    server()


if __name__ == "__main__":
    main()
