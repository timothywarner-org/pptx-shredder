# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PPTX Shredder is a Python CLI tool that transforms PowerPoint presentations into LLM-optimized markdown while preserving instructional design narrative. Built specifically for technical trainers who need to drop PPTX files into a folder, run the app, and pick up markdown files for LLM-assisted training development.

## Core Workflow

The application follows this simple user workflow:
1. Drop PPTX files into input folder
2. Run: `python shred.py presentation.pptx`
3. Pick up markdown files from output folder
4. Use with LLMs for training development

## Development Commands

**Note: This is a new repository - no Python environment or dependencies are currently installed.**

### Initial Setup (when implementing)
```bash
# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (when requirements.txt exists)
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install in development mode (when setup.py/pyproject.toml exists)
pip install -e .
```

### Testing Commands (when implemented)
```bash
pytest                           # Run all tests
pytest tests/test_extractor.py   # Run specific test file
pytest --cov=src                # Run with coverage
```

### Code Quality (when implemented)
```bash
black src/                       # Format code
pylint src/                      # Lint code
mypy src/                       # Type checking
```

### Running the Application (when implemented)
```bash
# Basic usage
python src/shred.py presentation.pptx

# With custom output directory
python src/shred.py presentation.pptx --output-dir ./custom-output

# Multiple files with configuration
python src/shred.py *.pptx --strategy instructional --chunk-size 1500

# With custom config
python src/shred.py deck.pptx --config my-config.yaml --verbose
```

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