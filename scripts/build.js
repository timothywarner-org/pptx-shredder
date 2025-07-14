#!/usr/bin/env node
/**
 * Build script for npm package preparation
 */

import { writeFileSync, readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectRoot = join(__dirname, '..');

console.log('🔨 Building PPTX Shredder MCP package...');

// Verify required files exist
const requiredFiles = [
    'mcp_server.py',
    'requirements.txt',
    'src/shred.py',
    'src/extractor.py',
    'src/formatter.py',
    'src/utils.py'
];

let allFilesExist = true;
for (const file of requiredFiles) {
    const filePath = join(projectRoot, file);
    if (!existsSync(filePath)) {
        console.error(`❌ Required file missing: ${file}`);
        allFilesExist = false;
    } else {
        console.log(`✅ Found: ${file}`);
    }
}

if (!allFilesExist) {
    console.error('❌ Build failed: Missing required files');
    process.exit(1);
}

// Create installation instructions
const installInstructions = `
# PPTX Shredder MCP Server

This package contains the MCP server for PPTX Shredder.

## Installation

\`\`\`bash
# Install Python dependencies (run once after npm install)
cd node_modules/@timothywarner/pptx-shredder-mcp
pip install -r requirements.txt
\`\`\`

## Usage in Claude Desktop

\`\`\`json
{
  "mcpServers": {
    "pptx-shredder": {
      "command": "npx",
      "args": ["-y", "@timothywarner/pptx-shredder-mcp"],
      "description": "PPTX Shredder - Convert PowerPoint to LLM-optimized markdown"
    }
  }
}
\`\`\`

## Tools Available

- \`shred_pptx\` - Convert PPTX to markdown
- \`list_input_files\` - List available PPTX files  
- \`get_shredder_config\` - View current configuration
`;

writeFileSync(join(projectRoot, 'NPM_INSTALL.md'), installInstructions.trim());

console.log('✅ Build completed successfully!');
console.log('📦 Package is ready for npm publish');
console.log('');
console.log('Next steps:');
console.log('1. npm login');
console.log('2. npm publish --access public');
console.log('3. Users can then use: npx @timothywarner/pptx-shredder-mcp');