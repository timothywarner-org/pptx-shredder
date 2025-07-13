# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Status: 🚀 PRODUCTION READY

PPTX Shredder is a **fully implemented, tested, and deployed** Python CLI tool that transforms PowerPoint presentations into LLM-optimized markdown. Built for technical trainers who need to convert PPTX → LLM-ready markdown.

**GitHub Repository**: https://github.com/timothywarner-org/pptx-shredder

## Core Workflow

**Simple production workflow:**
1. Drop PPTX files into `input/` folder
2. Run: `python shred.py` (scans input folder automatically)
3. Pick up markdown files from `output/` folder
4. Use with LLMs for training development

## Quick Commands

```bash
# Production use (recommended)
python shred.py                    # Process all files in input/
python shred.py --dry-run          # Preview what will be processed

# MCP Integration (Claude Desktop)
claude mcp add pptx-shredder npx -y @timothywarner/pptx-shredder-mcp  # Global access
# Use in Claude Desktop: "Use shred_pptx to process my presentation.pptx"

# Development
make test                          # Run all 64 tests
make test-cov                      # Generate coverage report
make format                        # Format code with black
make build                         # Full build pipeline

# Docker/DevContainer
# Open in VS Code → "Reopen in Container" → Instant dev environment
```

## Architecture (IMPLEMENTED)

### Core Components
- **shred.py**: Main entry point (wrapper for module imports)
- **src/shred.py**: CLI with rich console UI (Click + Rich)
- **src/extractor.py**: PPTX content extraction with instructional pattern recognition
- **src/formatter.py**: Intelligent markdown chunking with token optimization
- **src/utils.py**: Configuration and helper utilities

### MCP Integration Components
- **mcp_server.py**: MCP server exposing shredder functionality
- **package.json**: npm package for global MCP access
- **bin/mcp-server.js**: Node.js wrapper for cross-directory accessibility
- **.mcp.json**: Local and global MCP configurations

### Key Features Implemented
- ✅ Module/section detection (keywords: Module, Section, Chapter, Unit, Lesson)
- ✅ Activity recognition (Lab, Exercise, Demo, Assessment, Troubleshooting, Case Study)
- ✅ Learning objective extraction from content and speaker notes
- ✅ Code block detection with language identification
- ✅ Token-optimized chunking (1500-2000 tokens)
- ✅ Rich YAML frontmatter with metadata
- ✅ Speaker notes as instructor context
- ✅ Progress bars, tables, and beautiful console output
- ✅ MCP server for Claude Desktop integration
- ✅ Global npm package accessibility (@timothywarner/pptx-shredder-mcp)

### Enterprise Training Features
- ✅ **Categorized instructor notes** (timing, emphasis, examples, tips, warnings, context, delivery)
- ✅ **Prerequisites detection** from content and speaker notes
- ✅ **Difficulty level assessment** (beginner, intermediate, advanced)
- ✅ **Time estimation** with activity-based multipliers
- ✅ **Visual elements** extraction (images, tables, charts, diagrams)
- ✅ **Structured content** preservation (lists, emphasis, formatting)
- ✅ **Assessment items** extraction (questions, knowledge checks)
- ✅ **Compliance markers** detection (GDPR, HIPAA, SOX, ISO, NIST, PCI)
- ✅ **Slide layout** semantic detection (data-table, visualization, image-focused)
- ✅ **Learning context** analysis (cognitive load, interaction level, learning mode)
- ✅ **Enhanced YAML frontmatter** with 20+ pedagogical metadata fields

## Testing & Quality

**64 comprehensive tests** covering:
- Unit tests for extractor and formatter
- Integration tests for full pipeline
- Cross-platform compatibility tests
- Performance benchmarks
- Error handling scenarios

**CI/CD Pipeline** includes:
- Cross-platform testing (Ubuntu/Windows/macOS)
- Python 3.9-3.12 support
- Security scanning (Safety + Bandit)
- Code quality (Black, Pylint, MyPy)
- Coverage reporting

## Development Environment

### VS Code Launch Configurations (9 scenarios)
- 🎯 Run PPTX Shredder
- 🔍 Debug with Dry Run
- 🗂️ Debug with Sample File
- 🧪 Run All Tests
- 🔬 Run Tests with Coverage
- ⚡ Debug Single Test
- 🏃‍♂️ Quick Test (No Coverage)
- 📊 Debug Extractor Only
- 🎨 Debug Formatter Only

### DevContainer (Lightning Fast)
- Python 3.11 optimized image
- Pre-installed dependencies
- 2GB RAM limit for efficiency
- Cached workspace mounts
- Instant startup

### Makefile Commands
```bash
make help          # Show all commands
make install       # Install dependencies
make run           # Run PPTX Shredder
make test          # Run tests
make test-cov      # Coverage report
make format        # Format code
make lint          # Lint code
make clean         # Clean cache
make build         # Full pipeline
make demo          # Create & process demo
```

## Automation & CI/CD

### Dependabot Configuration
- **Python deps**: Weekly updates (Monday 9 AM ET)
- **GitHub Actions**: Monthly updates
- **Docker images**: Monthly updates
- **Auto-merge**: Security patches and minor updates
- **Smart grouping**: Reduces PR noise

### PR Review Automation
- **Auto-assigns** @timothywarner for code review
- **Requests** @github-copilot review via comments
- **Smart labeling** based on PR content
- **CODEOWNERS** file for GitHub native protection
- **Different logic** for Dependabot vs manual PRs

### GitHub Workflows
1. **CI/CD Pipeline** - Comprehensive testing and quality checks
2. **Dependabot Auto-merge** - Smart handling of dependency updates
3. **Auto-assign Reviewers** - Intelligent PR review assignment

## Repository Configuration

### GitHub Settings
- **Branch**: `main` (modern naming)
- **License**: MIT
- **Topics**: powerpoint, markdown, llm, instructional-design, training, python, technical-training
- **Security**: Dependabot enabled, GHAS ready
- **Automation**: Full CI/CD, auto-review assignment

### Key Files
- `.github/dependabot.yml` - Dependency automation
- `.github/CODEOWNERS` - Review requirements
- `.github/workflows/` - CI/CD and automation
- `.vscode/` - Rich development experience
- `.devcontainer/` - Instant dev environment
- `Makefile` - Developer productivity commands
- `package.json` - npm package for global MCP access
- `mcp_server.py` - MCP server implementation
- `.mcp.json` - MCP configuration (local + global)

## Privacy & Security

- ✅ Completely offline - no network calls
- ✅ No telemetry or usage statistics
- ✅ All processing local to machine
- ✅ No API keys or credentials
- ✅ NDA-friendly design
- ✅ Security scanning in CI/CD
- ✅ MCP server runs locally (Python + Node.js wrapper)
- ✅ Global npm package only provides accessibility, not external dependencies

## Architecture

### Core Components (as defined in PRD)

- **src/shred.py**: Main CLI entry point using Click framework
- **src/extractor.py**: PPTX content extraction (text, speaker notes, slide titles)
- **src/chunker.py**: Intelligent chunking logic for instructional content
- **src/formatter.py**: Markdown formatting with YAML frontmatter
- **src/utils.py**: Helper functions and utilities

### Key Technical Patterns

**Instructional Design Preservation**: The chunking algorithm recognizes training patterns:
- Module detection via keywords ("Module", "Section", "Chapter", "Unit", "Lesson")
- Learning objective extraction from slides and speaker notes
- Activity recognition (labs, exercises, demos, assessments)
- Narrative flow preservation across related slides

**Token Optimization**: Chunks target 1500-2000 tokens with overlap for continuity, optimized for LLM consumption.

**Metadata Structure**: Each markdown output includes YAML frontmatter with:
```yaml
module_id: "unique-identifier"
module_title: "Human Readable Title" 
slide_range: [start, end]
learning_objective: "Primary learning outcome"
concepts: ["list", "of", "concepts"]
instructional_elements:
  - type: "theory|demo|assessment"
    slides: [slide_numbers]
estimated_duration: "duration"
prerequisites: ["prerequisite-modules"]
```

## Dependencies (from PRD)

### Core Runtime
- python-pptx>=0.6.21 (PPTX manipulation)
- pyyaml>=6.0 (configuration and frontmatter)
- click>=8.1.0 (CLI framework)
- rich>=13.0 (terminal output formatting)
- tiktoken>=0.5.0 (token counting for LLMs)

### Development
- pytest>=7.4.0 (testing)
- pytest-cov>=4.1.0 (coverage)
- black>=23.0 (formatting)
- pylint>=2.17.0 (linting)
- mypy>=1.5.0 (type checking)
- pre-commit>=3.4.0 (git hooks)

## Configuration System

Default config.yaml structure supports:
- Chunking strategies (instructional, sequential, module-based)
- Module detection markers
- Content processing options
- Output formatting preferences
- Instructional pattern detection

## Target Platform

- Primary: Windows 11 with PowerShell 7+
- Python 3.9+ required
- Cross-platform support (macOS, Linux)
- All processing local (no network calls)
- Performance target: <60 seconds for 200-slide deck

## Privacy and Security

- No network calls - completely offline processing
- No telemetry or usage statistics
- All files remain on user's machine
- No API keys or credentials required
- Designed for NDA-friendly environments

## Claude Code Memory

- When making substantial changes, update both your CLAUDE metadata as well as repo README.