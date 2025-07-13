# Product Requirements Document: PPTX Shredder

## Project Metadata and Repository Configuration

### Repository Details
- **Repository Name**: `pptx-shredder`
- **Visibility**: Public
- **License**: MIT
- **Description**: "Transform PowerPoint presentations into LLM-optimized markdown while preserving instructional design narrative. Built for technical trainers."
- **Topics/Tags**: `powerpoint`, `markdown`, `llm`, `instructional-design`, `training`, `python`, `content-extraction`, `technical-training`, `education-technology`
- **Security**: GitHub Advanced Security (GHAS) enabled
- **Features**: GitHub Copilot Enterprise enabled

### Repository Structure
```
pptx-shredder/
├── .github/
│   ├── workflows/
│   │   ├── tests.yml          # CI/CD pipeline
│   │   └── security.yml       # GHAS security scanning
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── PULL_REQUEST_TEMPLATE.md
├── .vscode/
│   ├── settings.json          # VS Code workspace settings
│   ├── extensions.json        # Recommended extensions
│   └── launch.json           # Debug configurations
├── .devcontainer/
│   └── devcontainer.json     # Dev container configuration
├── src/
│   ├── __init__.py
│   ├── shred.py              # Main entry point
│   ├── extractor.py          # PPTX content extraction
│   ├── chunker.py            # Intelligent chunking logic
│   ├── formatter.py          # Markdown formatting
│   └── utils.py              # Helper functions
├── tests/
│   ├── __init__.py
│   ├── test_extractor.py
│   ├── test_chunker.py
│   └── fixtures/             # Test PPTX files
├── samples/
│   ├── demo.pptx             # Sample presentation
│   ├── demo.md               # Sample output
│   └── README.md             # Explanation of samples
├── output/                   # User output directory (gitignored)
├── docs/
│   ├── ARCHITECTURE.md       # Technical design
│   ├── USAGE.md             # Detailed usage guide
│   └── INSTRUCTIONAL_DESIGN.md # ID methodology
├── .gitignore
├── .gitattributes
├── LICENSE
├── README.md
├── requirements.txt
├── requirements-dev.txt      # Development dependencies
├── config.yaml              # Default configuration
├── pyproject.toml           # Python project metadata
└── CHANGELOG.md

```

## Project Vision and Goals

### Problem Statement
Technical trainers and instructional designers need to repurpose PowerPoint content for various delivery formats while maintaining the pedagogical narrative structure. Current solutions either dump raw text or require manual restructuring, losing the instructional flow that makes content effective for learning.

### Solution
PPTX Shredder intelligently extracts and restructures PowerPoint presentations into markdown format optimized for Large Language Model consumption, preserving the instructional design elements that make content teachable rather than just readable.

### Target Users
1. **Primary**: Technical trainers creating content for online learning platforms
2. **Secondary**: Instructional designers repurposing existing materials
3. **Tertiary**: Content creators building AI-assisted training materials

## Functional Requirements

### Core Functionality

#### 1. Content Extraction
The system must extract the following elements from PPTX files:

- **Text Content**: All visible text from shapes, text boxes, and placeholders
- **Speaker Notes**: Complete speaker notes with formatting preserved
- **Slide Titles**: Identified through shape type and position heuristics
- **Code Blocks**: Detected through formatting patterns and preserved with language hints
- **Lists and Hierarchies**: Maintained with proper nesting
- **Slide Relationships**: Previous/next indicators and section boundaries

#### 2. Intelligent Chunking
The chunking algorithm must recognize instructional patterns:

- **Module Detection**: Identify slides beginning with "Module", "Section", "Unit", "Chapter", or similar markers
- **Learning Objective Extraction**: Find and elevate stated objectives from slide content or speaker notes
- **Activity Recognition**: Detect labs, exercises, demos, and assessments
- **Narrative Flow Preservation**: Maintain the "story" across related slides
- **Context Window Optimization**: Target 1500-2000 tokens per chunk with overlap for continuity

#### 3. Metadata Preservation
Each chunk must include:

```yaml
---
module_id: "azure-storage-fundamentals"
module_title: "Azure Storage Fundamentals"
slide_range: [23, 29]
learning_objective: "Configure blob storage with appropriate security settings"
concepts:
  - "Storage account types"
  - "Blob tiers"
  - "Access patterns"
instructional_elements:
  - type: "theory"
    slides: [24, 25]
  - type: "demo"
    slides: [26, 28]
  - type: "assessment"
    slides: [29]
estimated_duration: "15 minutes"
prerequisites: ["azure-basics", "resource-groups"]
---
```

#### 4. Output Formatting
The markdown output must:

- Use consistent heading hierarchies
- Preserve code block formatting with language detection
- Maintain list structures
- Include speaker notes as contextual asides
- Reference visual elements descriptively: `[Diagram: Storage Architecture]`
- Preserve emphasis and formatting where pedagogically relevant

### Command Line Interface

The tool must support the following CLI operations:

```bash
# Basic usage
python shred.py presentation.pptx

# Advanced usage
python shred.py presentation.pptx --output-dir ./custom-output
python shred.py *.pptx --strategy instructional --chunk-size 1500
python shred.py deck.pptx --config my-config.yaml --verbose

# Help system
python shred.py --help
python shred.py --version
```

### Configuration System

Default configuration in `config.yaml`:

```yaml
# Chunking Strategy
chunking:
  strategy: "instructional"  # or "sequential", "module-based"
  max_tokens: 2000
  overlap_tokens: 100

# Module Detection
module_markers:
  - "Module"
  - "Section"
  - "Chapter"
  - "Unit"
  - "Lesson"

# Content Processing
content:
  include_speaker_notes: true
  preserve_code_blocks: true
  detect_language: true
  include_slide_numbers: true

# Output Format
output:
  format: "markdown"  # Future: "json", "yaml"
  include_metadata: true
  frontmatter_format: "yaml"
  filename_pattern: "{original_name}_{module_id}.md"

# Instructional Patterns
instructional:
  detect_objectives: true
  detect_assessments: true
  detect_activities: true
  activity_markers:
    - "Lab"
    - "Exercise"
    - "Practice"
    - "Demo"
    - "Try it"
```

## Technical Requirements

### Environment and Dependencies

#### Core Dependencies
```txt
# requirements.txt
python-pptx>=0.6.21      # PPTX file manipulation
pyyaml>=6.0             # Configuration and frontmatter
click>=8.1.0            # CLI framework
rich>=13.0              # Terminal output formatting
tiktoken>=0.5.0         # Token counting for LLMs
```

#### Development Dependencies
```txt
# requirements-dev.txt
pytest>=7.4.0           # Testing framework
pytest-cov>=4.1.0       # Coverage reporting
black>=23.0             # Code formatting
pylint>=2.17.0          # Linting
mypy>=1.5.0            # Type checking
pre-commit>=3.4.0       # Git hooks
```

### Platform Requirements

- **Primary Platform**: Windows 11 with PowerShell 7+
- **Python Version**: 3.9+ (for type hints and modern features)
- **Cross-Platform**: Must work on macOS and Linux
- **No External Services**: All processing must be local
- **Performance Target**: <60 seconds for 200-slide deck on modern hardware

### Code Architecture

The application follows a modular architecture with clear separation of concerns:

```python
# src/shred.py - Main entry point
import click
from extractor import PPTXExtractor
from chunker import InstructionalChunker
from formatter import MarkdownFormatter

@click.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output-dir', default='output', help='Output directory')
@click.option('--config', type=click.Path(), help='Configuration file')
def shred(input_file, output_dir, config):
    """Transform PowerPoint presentations into LLM-optimized markdown."""
    # Implementation details in actual code
    pass
```

## Privacy and Security Requirements

### Data Handling
1. **No Network Calls**: All processing must be completely offline
2. **No Telemetry**: No usage statistics or error reporting
3. **Local Storage Only**: All files remain on user's machine
4. **Explicit Output**: Users control where files are saved

### Repository Security
1. **Production Content**: Never committed to repository
2. **Sample Files**: Only generic, non-proprietary examples
3. **Secrets Management**: No API keys or credentials needed
4. **GHAS Integration**: Automated security scanning enabled

### Compliance Considerations
1. **NDA Friendly**: No employer names in documentation
2. **Generic Examples**: Focus on technical training patterns
3. **Open Source**: MIT license for maximum flexibility

## Output Specifications

### Markdown Schema

Each generated markdown file follows this structure:

```markdown
---
# YAML Frontmatter with metadata
module_id: "unique-identifier"
module_title: "Human Readable Title"
slide_range: [start, end]
learning_objective: "Primary learning outcome"
# ... additional metadata
---

# Module: [Module Title]

## Learning Objective
[Extracted or inferred objective]

## Overview
[Synthesized introduction from first slides]

## Concepts

### [Concept 1 Title]
[Content from relevant slides with speaker notes integrated naturally]

### [Concept 2 Title]
[Content continues...]

## Practical Application
[Labs, demos, exercises presented as actionable steps]

## Key Takeaways
[Synthesized from conclusion slides]

## Instructor Notes
[Important speaker notes that provide teaching context]
```

### Token Optimization

The chunking algorithm ensures:
- Each chunk remains under 2000 tokens (approximately 500-750 words)
- Natural break points at concept boundaries
- Overlap context from previous chunk when needed
- Metadata doesn't count against token limit

## Success Criteria and Metrics

### Functional Success
1. **Extraction Accuracy**: 100% of text content extracted from test presentations
2. **Module Detection**: 90%+ accuracy in identifying instructional boundaries
3. **Token Compliance**: No chunk exceeds configured token limit
4. **Processing Speed**: <60 seconds for 200-slide presentation

### Quality Metrics
1. **Narrative Preservation**: Output maintains logical flow when read sequentially
2. **Context Completeness**: LLM can answer questions about content without accessing original PPTX
3. **Instructional Integrity**: Learning objectives remain clear and achievable
4. **Code Preservation**: All code blocks maintain formatting and language hints

### User Experience
1. **Installation**: Single pip install command
2. **Basic Usage**: Works with just filename argument
3. **Error Handling**: Clear messages for common issues
4. **Progress Indication**: Visual feedback during processing

## Development Roadmap

### Phase 1: MVP (Week 1-2)
- Basic PPTX text extraction
- Simple sequential chunking
- Markdown output with frontmatter
- Command line interface
- Core documentation

### Phase 2: Intelligent Chunking (Week 3-4)
- Module detection algorithm
- Speaker notes integration
- Token counting and optimization
- Configuration system
- Comprehensive testing

### Phase 3: Instructional Enhancement (Week 5-6)
- Learning objective extraction
- Activity type detection
- Narrative flow preservation
- Advanced chunking strategies
- Performance optimization

### Future Enhancements (Post-MVP)
- Image OCR and description
- Animation sequence preservation
- Multiple output formats (JSON, YAML)
- GUI interface option
- Plugin system for custom processors

## Testing Strategy

### Test Coverage Requirements
- Unit tests for all core functions (90%+ coverage)
- Integration tests with sample PPTX files
- Performance benchmarks with large presentations
- Cross-platform validation (Windows, macOS, Linux)

### Sample Test Presentations
The repository includes diverse test cases:
1. `simple_technical.pptx` - Basic technical training slides
2. `complex_modules.pptx` - Multi-module course with labs
3. `code_heavy.pptx` - Programming course with lots of code
4. `mixed_content.pptx` - Combination of theory and practice

## Documentation Requirements

### User Documentation
1. **README.md**: Quick start and basic usage
2. **USAGE.md**: Comprehensive guide with examples
3. **INSTRUCTIONAL_DESIGN.md**: Explanation of ID preservation approach
4. **CONFIGURATION.md**: Detailed configuration options

### Developer Documentation
1. **ARCHITECTURE.md**: Technical design and flow
2. **CONTRIBUTING.md**: Guidelines for contributors
3. **API.md**: Module interfaces for extensions
4. **Code Comments**: Inline documentation for complex logic

## Support and Community

### GitHub Integration
- Issue templates for bugs and features
- Pull request template with checklist
- GitHub Actions for CI/CD
- Automated release process

### Community Engagement
- Clear contribution guidelines
- Code of conduct
- Response time expectations
- Feature request process

This comprehensive PRD provides everything needed to implement PPTX Shredder from scratch, including all architectural decisions, implementation details, and quality standards. The document serves as both a specification and a guide for creating a professional-grade tool that solves real problems for technical trainers and instructional designers.

**Next Best Steps:**
1) **Create the GitHub repository** with the structure defined in this PRD
2) **Implement the MVP** focusing on basic extraction and markdown output
3) **Iterate based on testing** with real training presentations to refine the chunking algorithm
