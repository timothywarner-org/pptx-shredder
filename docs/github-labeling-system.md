# .github Directory

This directory contains GitHub-specific configuration and documentation for PPTX Shredder.

## 📁 Contents

### 🏷️ Labels System
- **`labels.json`** - Complete label definitions for import
- **`create-labels.sh`** - Automated script to create all labels via GitHub CLI
- **`LABEL_GUIDE.md`** - Comprehensive guide to using our labeling system

### 🚀 Quick Setup
```bash
# Create all labels automatically
./.github/create-labels.sh

# Or import manually via GitHub web interface using labels.json
```

## 🎯 Label Categories

Our comprehensive labeling system includes:

- **🤝 Community**: `help wanted`, `good first issue`, `mentor available`
- **🏷️ Types**: `bug`, `feature`, `enhancement`, `documentation`
- **🧩 Components**: `component: extractor`, `component: formatter`, `component: mcp-server`
- **⚡ Priority**: `priority: critical/high/medium/low`
- **📏 Effort**: `size: xs/s/m/l/xl`
- **📊 Status**: `status: blocked/in-progress/needs-review`
- **🎯 Domain**: `instructional-design`, `llm-optimization`, `pptx-processing`

## 📚 Documentation

See **`LABEL_GUIDE.md`** for:
- Complete labeling strategy
- Best practices for issues and PRs
- Examples of well-labeled contributions
- Setup and verification instructions

## 🎉 Benefits

This system provides:
- **Clear contributor onboarding** with `good first issue` labels
- **Efficient project management** with priority and component labels
- **Transparent development** with status tracking
- **Domain expertise** routing with component-specific labels

---

**Goal**: Make PPTX Shredder welcoming to contributors and easy to maintain! 🚀