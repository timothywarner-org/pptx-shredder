# PPTX Shredder 🎯

**Production-Ready PowerPoint → LLM Markdown Converter**

Transform PowerPoint presentations into LLM-optimized markdown while preserving instructional design narrative. Built for technical trainers who need a dead-simple workflow.

## 🚀 Status: Production Ready

✅ **Fully Implemented** - All core features working  
✅ **Comprehensively Tested** - 64 tests, 95%+ coverage  
✅ **Enterprise CI/CD** - GitHub Actions, Dependabot, auto-review  
✅ **Rich Console UI** - Beautiful progress bars and tables  
✅ **Public Repository** - [timothywarner-org/pptx-shredder](https://github.com/timothywarner-org/pptx-shredder)

## 💡 Super Simple Workflow

1. **Drop** PPTX files in `input/` folder
2. **Run** `python shred.py`
3. **Collect** LLM-ready markdown from `output/`

That's it! No configuration needed for basic use.

## 🏃 Quick Start

### Option 1: Production Use
```bash
# Clone the repository
git clone https://github.com/timothywarner-org/pptx-shredder.git
cd pptx-shredder

# Install dependencies
pip install -r requirements.txt

# Drop PPTX files in input/ folder, then:
python shred.py

# Find your markdown in output/
```

### Option 2: Development Container (Recommended)
```bash
# Open in VS Code with Dev Containers extension
code pptx-shredder

# Click "Reopen in Container" when prompted
# Everything is pre-configured and ready!
```

### Option 3: Direct Processing
```bash
# Process specific files
python shred.py presentation.pptx another.pptx

# Preview what would happen
python shred.py --dry-run
```

## 📖 Usage Guide

### Basic Commands
```bash
# Production mode - scan input/ folder
python shred.py

# Process specific files  
python shred.py presentation.pptx course.pptx

# Preview mode (no files created)
python shred.py --dry-run

# Show help
python shred.py --help
```

### Advanced Options
```bash
# Custom chunking strategy
python shred.py --strategy sequential --chunk-size 2000

# Verbose output with detailed logging
python shred.py --verbose

# Custom output directory
python shred.py --output-dir ./my-markdown

# Force overwrite existing files
python shred.py --force
```

### Processing Strategies
- **`instructional`** (default): Smart chunking that preserves learning modules
- **`sequential`**: Simple slide-by-slide processing
- **`single`**: One file per presentation

## 🎯 What It Does

### Core Features
PPTX Shredder intelligently:
- **Extracts Everything**: Text, speaker notes, slide structure, code blocks
- **Recognizes Patterns**: Modules, labs, exercises, learning objectives
- **Optimizes for LLMs**: Token-counted chunks (1500-2000 tokens) with overlap
- **Preserves Context**: Instructional narrative and relationships
- **Rich Metadata**: YAML frontmatter with learning context
- **Code Detection**: Identifies and formats code in 15+ languages
- **Beautiful UI**: Progress bars, tables, and colored output

### Instructional Design Awareness
- Detects module boundaries and learning objectives
- Preserves lab instructions and exercise context  
- Maintains teaching flow and narrative structure
- Groups related content intelligently

## 📄 Output Example

```markdown
---
module_id: "01-azure-storage-fundamentals"
module_title: "Azure Storage Fundamentals"
slide_range: [1, 5]
learning_objectives:
  - "Configure blob storage with appropriate security settings"
  - "Implement lifecycle management policies"
concepts: ["Storage", "Azure", "Security", "Lifecycle"]
activity_type: "lab"
estimated_duration: "15 minutes"
chunk_index: 1
total_chunks: 3
---

# Module 1: Azure Storage Fundamentals

## 🎯 Learning Objectives

By the end of this module, you will be able to:
- Configure blob storage with appropriate security settings
- Implement lifecycle management policies
- Monitor storage metrics and set up alerts

## 📚 Content

### Storage Account Types

Azure offers several storage account types optimized for different scenarios:

• **Standard general-purpose v2** - Balanced performance and cost
• **Premium block blobs** - SSD-backed for low latency
• **Premium file shares** - High-performance file storage

### 🧪 Lab: Configure Secure Storage

**Objective**: Deploy a storage account with private endpoint

```powershell
# Create storage account with private endpoint
$storageAccount = New-AzStorageAccount -ResourceGroupName "rg-lab" `
  -Name "stlab$((Get-Random))" `
  -Location "eastus" `
  -SkuName "Standard_LRS" `
  -Kind "StorageV2" `
  -AllowBlobPublicAccess $false
```

**Next Steps**: Continue to implement lifecycle policies...
```

## ✨ Key Features

### Production Ready
- **🎯 Simple Workflow**: Just drop files and run
- **📊 Rich Console**: Beautiful progress bars, tables, and colored output
- **⚡ Fast Processing**: Handles large presentations efficiently
- **🔒 Privacy First**: All processing local, no external API calls

### Instructional Design Focused
- **🧠 Pattern Recognition**: Detects modules, labs, demos, exercises
- **📚 Learning Context**: Preserves objectives and teaching narrative  
- **🎓 Trainer-Friendly**: Built by trainers, for trainers

### LLM Optimization
- **🤖 Token Counting**: Precise chunking for GPT-4, Claude, etc.
- **📋 Rich Metadata**: YAML frontmatter with semantic context
- **🔗 Smart Overlap**: Maintains context across chunks
- **💬 Conversation Ready**: Output designed for chat interfaces

### Enterprise Grade
- **🧪 Comprehensive Testing**: 64 tests, 95%+ coverage
- **🚀 CI/CD Pipeline**: GitHub Actions for all platforms
- **🤝 Auto-Review**: Dependabot + GitHub Copilot integration
- **⚡ Cross Platform**: Windows, macOS, Linux support
- **🐳 Dev Container**: Pre-configured development environment

## 🎬 Try It Now

### Quick Demo
```bash
# Run the interactive demo
python demo.py

# Or try with sample presentations
cp samples/*.pptx input/
python shred.py
```

### Real-World Example
```bash
# Process a technical training deck
python shred.py "Azure Fundamentals Course.pptx"

# Output includes:
# - Module detection and grouping
# - Lab instructions preserved
# - Code blocks properly formatted
# - Learning objectives extracted
# - Smart chunking for LLM context windows
```

## 🧪 Development

### Testing
```bash
# Run all tests with verbose output
PYTHONPATH=src python -m pytest tests/ -v

# Run with coverage report
PYTHONPATH=src python -m pytest tests/ --cov=src --cov-report=html

# Run specific test category
PYTHONPATH=src python -m pytest tests/test_extractor.py -v

# Quick test run
make test
```

### Code Quality
```bash
# Format code
black src/ tests/

# Type checking
mypy src/

# Lint code
ruff check src/

# Run all checks
make check
```

### Development Workflow
```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run in watch mode
make watch

# Build and test
make all
```

## 👥 Perfect For

### Technical Trainers
- Convert course materials for AI-assisted delivery
- Create searchable knowledge bases from presentations
- Generate practice questions and assessments

### Instructional Designers  
- Repurpose existing content for new formats
- Extract learning objectives and outcomes
- Analyze course structure and flow

### Content Teams
- Build AI training datasets from presentations
- Create documentation from training materials
- Generate summaries and abstracts

### Developers
- Process technical presentations for RAG systems
- Extract code examples and documentation
- Build knowledge bases for AI assistants

## 🏗️ Architecture

```
pptx-shredder/
├── src/                    # Core application code
│   ├── extractor.py       # PPTX content extraction
│   ├── formatter.py       # Markdown generation & chunking
│   ├── shred.py          # CLI interface with Rich UI
│   └── utils.py          # Token counting & helpers
├── tests/                 # Comprehensive test suite
├── input/                 # Drop PPTX files here
├── output/                # Markdown files appear here
├── .github/               # CI/CD and automation
│   ├── workflows/        # GitHub Actions
│   └── dependabot.yml    # Dependency management
└── .devcontainer/        # VS Code dev environment
```

## 🔧 Configuration

Default settings in `config.yaml`:
```yaml
extraction:
  extract_text: true
  extract_notes: true
  extract_images: false  # Coming soon
  
formatting:
  default_chunk_size: 1500
  chunk_overlap: 200
  include_metadata: true
  
output:
  overwrite_existing: false
  create_summary: true
```

## 🚀 Roadmap

- [x] Core PPTX text extraction
- [x] Instructional design patterns
- [x] LLM-optimized chunking
- [x] Rich console interface
- [x] Comprehensive testing
- [x] CI/CD pipeline
- [ ] Image extraction and description
- [ ] Table preservation
- [ ] Multi-language support
- [ ] Web interface
- [ ] API endpoint

## 📚 Documentation

- [CLAUDE.md](CLAUDE.md) - AI assistant context
- [docs/PRD.md](docs/PRD.md) - Product requirements
- [GitHub Wiki](https://github.com/timothywarner-org/pptx-shredder/wiki) - Extended docs

## 🤝 Contributing

Contributions welcome! This project uses:
- Automated PR review assignment
- GitHub Copilot code review
- Comprehensive test requirements
- Pre-commit hooks for quality

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

**Built by technical trainers, for technical trainers.** 🎓

Need help? Found a bug? [Open an issue](https://github.com/timothywarner-org/pptx-shredder/issues)!