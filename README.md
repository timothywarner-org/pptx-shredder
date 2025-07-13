# PPTX Shredder

Transform PowerPoint presentations into LLM-optimized markdown while preserving instructional design narrative. Built for technical trainers.

## 🎯 Production Ready

**Super Simple Workflow:**
1. Drop PPTX files in `input/` folder
2. Run `python shred.py`
3. Pick up LLM-ready markdown from `output/`

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Production workflow:**
   ```bash
   # Drop files in input/ and run
   python shred.py
   
   # Or process specific files
   python shred.py presentation.pptx
   
   # Preview what would happen
   python shred.py --dry-run
   ```

3. **Your markdown files are ready in `output/`**

## Usage Options

```bash
# Production mode - scan input/ folder
python shred.py

# Process specific files  
python shred.py presentation.pptx another.pptx

# Advanced options
python shred.py --strategy sequential --chunk-size 2000 --verbose

# See what would be processed
python shred.py --dry-run
```

## What It Does

PPTX Shredder intelligently:
- Extracts text content, speaker notes, and slide structure
- Detects instructional patterns (modules, labs, objectives)
- Chunks content optimally for LLM consumption (1500-2000 tokens)
- Preserves teaching narrative and context
- Generates markdown with YAML frontmatter metadata

## Output Example

```markdown
---
module_id: "01-azure-storage-fundamentals"
module_title: "Azure Storage Fundamentals"
slide_range: [1, 5]
learning_objectives:
  - "Configure blob storage with appropriate security settings"
concepts: ["Storage", "Azure", "Security"]
activity_type: "lab"
estimated_duration: "8 minutes"
---

# Azure Storage Fundamentals

## Learning Objectives
- Configure blob storage with appropriate security settings

## Content

### Storage Account Types
• Standard general-purpose v2
• Premium block blobs
...
```

## ✨ Features

- **🎯 Production Ready**: Simple input/output folder workflow
- **📊 Rich Console**: Beautiful progress bars, tables, and feedback
- **🧠 Instructional Design Aware**: Recognizes modules, labs, objectives
- **🤖 LLM Optimized**: Token-counted chunks with proper overlap
- **📋 Rich Metadata**: YAML frontmatter with learning context
- **🔒 Privacy First**: All processing local, no network calls
- **🧪 Test Driven**: 64 tests with 95%+ coverage
- **⚡ Cross Platform**: Works on Windows, macOS, Linux

## 🎬 Demo

Try it with the included demo:
```bash
python demo.py
```

## 🧪 Testing

```bash
# Run all tests
PYTHONPATH=src python -m pytest tests/ -v

# Run with coverage
PYTHONPATH=src python -m pytest tests/ --cov=src --cov-report=html

# Format code
black src/ tests/

# Type checking
mypy src/
```

## Perfect For

- **Technical trainers** creating LLM-assisted content
- **Instructional designers** repurposing materials  
- **Content creators** building AI training materials

Built by technical trainers, for technical trainers. 🎓