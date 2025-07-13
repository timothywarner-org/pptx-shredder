# MCP Server Setup for PPTX Shredder

This document explains how to set up the Model Context Protocol (MCP) server for PPTX Shredder to use with Claude Desktop and other MCP clients.

## Prerequisites

1. **Install MCP package**:
   ```bash
   pip install mcp
   ```

2. **Ensure PPTX Shredder dependencies are installed**:
   ```bash
   pip install -r requirements.txt
   ```

## Claude Desktop Configuration

### Method 1: Global npm Package (Recommended)

1. **Add the global MCP server** (works from any directory):
   ```bash
   claude mcp add pptx-shredder npx -y @timothywarner/pptx-shredder-mcp
   ```

2. **Verify the server is added**:
   ```bash
   claude mcp list
   ```

### Method 2: Local Development Setup

1. **Add the local MCP server** (for development/testing):
   ```bash
   claude mcp add pptx-shredder-local python mcp_server.py --cwd /path/to/pptx-shredder
   ```

### Method 2: Manual Configuration

1. **Open Claude Desktop settings**
2. **Navigate to MCP Servers section**
3. **Add the following configuration**:
   ```json
   {
     "mcpServers": {
       "pptx-shredder": {
         "command": "python",
         "args": ["mcp_server.py"],
         "cwd": "C:\\github\\pptx-shredder",
         "description": "PPTX Shredder - Convert PowerPoint presentations to LLM-optimized markdown",
         "env": {
           "PYTHONPATH": "."
         }
       }
     }
   }
   ```

### Method 3: Project-based Configuration

The project includes a `.mcp.json` file for project-based MCP configuration:

```bash
# From within the pptx-shredder directory
claude mcp import .mcp.json
```

## Available Tools

Once configured, you'll have access to these tools in Claude Desktop:

### 1. `shred_pptx`
Convert a PowerPoint presentation to LLM-optimized markdown.

**Parameters**:
- `file_path` (required): Path to the PPTX file
- `output_dir` (optional): Output directory (default: "output")
- `dry_run` (optional): Preview processing without creating files

**Example usage in Claude Desktop**:
```
Please use the shred_pptx tool to process my presentation at input/training.pptx
```

### 2. `list_input_files`
List all PPTX files in the input directory.

**Parameters**:
- `input_dir` (optional): Input directory to scan (default: "input")

**Example usage**:
```
Show me what PPTX files are available to process using list_input_files
```

### 3. `get_shredder_config`
Get the current PPTX Shredder configuration.

**Example usage**:
```
What are the current shredder settings? Use get_shredder_config
```

## Usage Examples

### Process a specific file
```
Use shred_pptx to convert input/azure_training.pptx to markdown
```

### Dry run to preview processing
```
Run shred_pptx with dry_run=true on input/my_presentation.pptx to see what would be processed
```

### List available files
```
Use list_input_files to show me all available PPTX files
```

## Troubleshooting

### Server not starting
1. Verify Python path and working directory in configuration
2. Check that all dependencies are installed
3. Ensure `mcp_server.py` has execute permissions

### Tools not appearing
1. Restart Claude Desktop after configuration changes
2. Verify the MCP server is listed in Claude Desktop settings
3. Check server logs for errors

### Path issues on Windows
- Use forward slashes or double backslashes in paths
- Ensure the `cwd` points to the correct project directory
- Consider using absolute paths for reliability

## Security Considerations

- The MCP server runs locally and only processes files on your machine
- No network calls are made - completely offline processing
- All PPTX processing happens locally, respecting NDA requirements
- The server only exposes specific, safe operations (no file system access beyond configured directories)

## Advanced Configuration

### Custom Environment Variables
Add environment variables to the MCP configuration:

```json
{
  "env": {
    "PYTHONPATH": ".",
    "PPTX_SHREDDER_CONFIG": "custom_config.yaml",
    "LOG_LEVEL": "INFO"
  }
}
```

### Multiple Configurations
You can have different configurations for different environments:

```json
{
  "mcpServers": {
    "pptx-shredder-dev": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "C:\\dev\\pptx-shredder"
    },
    "pptx-shredder-prod": {
      "command": "python", 
      "args": ["mcp_server.py"],
      "cwd": "C:\\production\\pptx-shredder"
    }
  }
}
```