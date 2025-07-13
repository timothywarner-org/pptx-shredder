#!/usr/bin/env python3
"""
MCP Server for PPTX Shredder
Model Context Protocol server that exposes PPTX Shredder functionality to Claude Desktop and other MCP clients.
"""

import json
import sys
import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging

# MCP imports (these would need to be installed via pip install mcp)
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
except ImportError:
    print("MCP package not found. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

# Import our shredder functionality
from src.shred import process_file
from src.utils import get_config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the MCP server
server = Server("pptx-shredder")

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools for the MCP client."""
    return [
        Tool(
            name="shred_pptx",
            description="Convert a PowerPoint presentation to LLM-optimized markdown",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the PPTX file to process"
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "Output directory for markdown files (optional)",
                        "default": "output"
                    },
                    "dry_run": {
                        "type": "boolean",
                        "description": "Preview processing without creating files",
                        "default": False
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="list_input_files",
            description="List all PPTX files in the input directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_dir": {
                        "type": "string",
                        "description": "Input directory to scan (optional)",
                        "default": "input"
                    }
                }
            }
        ),
        Tool(
            name="get_shredder_config",
            description="Get current PPTX Shredder configuration",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls from the MCP client."""
    
    if name == "shred_pptx":
        file_path = arguments.get("file_path")
        output_dir = arguments.get("output_dir", "output")
        dry_run = arguments.get("dry_run", False)
        
        if not file_path:
            return [TextContent(type="text", text="Error: file_path is required")]
        
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return [TextContent(type="text", text=f"Error: File not found: {file_path}")]
            
            if not file_path.suffix.lower() == '.pptx':
                return [TextContent(type="text", text=f"Error: File must be a .pptx file: {file_path}")]
            
            # Process the file
            result = process_file(
                file_path=file_path,
                output_dir=Path(output_dir),
                dry_run=dry_run
            )
            
            if dry_run:
                return [TextContent(
                    type="text", 
                    text=f"Dry run completed for {file_path}:\n{result}"
                )]
            else:
                return [TextContent(
                    type="text", 
                    text=f"Successfully processed {file_path} to {output_dir}\nResult: {result}"
                )]
                
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return [TextContent(type="text", text=f"Error processing file: {str(e)}")]
    
    elif name == "list_input_files":
        input_dir = Path(arguments.get("input_dir", "input"))
        
        try:
            if not input_dir.exists():
                return [TextContent(type="text", text=f"Input directory not found: {input_dir}")]
            
            pptx_files = list(input_dir.glob("*.pptx"))
            
            if not pptx_files:
                return [TextContent(type="text", text=f"No PPTX files found in {input_dir}")]
            
            file_list = "\n".join([f"- {f.name}" for f in pptx_files])
            return [TextContent(
                type="text", 
                text=f"PPTX files in {input_dir}:\n{file_list}"
            )]
            
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return [TextContent(type="text", text=f"Error listing files: {str(e)}")]
    
    elif name == "get_shredder_config":
        try:
            config = get_config()
            config_text = json.dumps(config, indent=2)
            return [TextContent(
                type="text",
                text=f"Current PPTX Shredder configuration:\n```json\n{config_text}\n```"
            )]
        except Exception as e:
            logger.error(f"Error getting config: {e}")
            return [TextContent(type="text", text=f"Error getting config: {str(e)}")]
    
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    """Main entry point for the MCP server."""
    try:
        # Run the stdio server
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())