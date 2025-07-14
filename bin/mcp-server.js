#!/usr/bin/env node
/**
 * MCP Server Entry Point for PPTX Shredder
 * This wrapper ensures the Python MCP server can be run from anywhere
 */

import { spawn } from 'child_process';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';
import { existsSync } from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectRoot = join(__dirname, '..');

// Path to the Python MCP server
const pythonServerPath = join(projectRoot, 'mcp_server.py');

// Check if Python server exists
if (!existsSync(pythonServerPath)) {
    console.error(`Error: Python MCP server not found at ${pythonServerPath}`);
    process.exit(1);
}

// Set up environment
const env = {
    ...process.env,
    PYTHONPATH: projectRoot
};

// Spawn the Python MCP server
const pythonProcess = spawn('python', [pythonServerPath], {
    stdio: ['inherit', 'inherit', 'inherit'],
    env: env,
    cwd: projectRoot
});

// Handle process events
pythonProcess.on('error', (error) => {
    console.error(`Failed to start Python MCP server: ${error.message}`);
    process.exit(1);
});

pythonProcess.on('close', (code) => {
    process.exit(code || 0);
});

// Handle termination signals
process.on('SIGINT', () => {
    pythonProcess.kill('SIGINT');
});

process.on('SIGTERM', () => {
    pythonProcess.kill('SIGTERM');
});