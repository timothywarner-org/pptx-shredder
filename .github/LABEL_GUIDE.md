# GitHub Labels Guide for PPTX Shredder

This document explains our comprehensive labeling system designed to improve project organization, contributor experience, and issue management.

## 🎯 Label Categories

### 🤝 Community & Contributors
Perfect for building an open-source community around PPTX Shredder:

| Label | Purpose | When to Use |
|-------|---------|-------------|
| `help wanted` | Seeking community contributions | Issues where maintainer input isn't required |
| `good first issue` | Perfect for newcomers | Simple, well-defined issues with clear scope |
| `good first PR` | Ideal first contribution | Documentation fixes, small enhancements |
| `hacktoberfest` | Hacktoberfest participation | October contributions, beginner-friendly |
| `mentor available` | Maintainer guidance offered | Complex issues where you'll provide support |

**💡 Pro Tip**: Combine `good first issue` + `component: docs` for documentation improvements that welcome new contributors.

### 🏷️ Issue Types
Standard categorization for all issues and PRs:

| Label | Purpose | Examples |
|-------|---------|----------|
| `bug` | Something broken | Extraction fails, CLI crashes, incorrect output |
| `enhancement` | Improve existing feature | Better error messages, performance tuning |
| `feature` | New functionality | Image extraction, new chunking strategies |
| `documentation` | Docs and guides | README updates, API documentation |
| `refactor` | Code cleanup | Restructure modules, improve maintainability |
| `performance` | Speed/efficiency | Faster PPTX parsing, memory optimization |
| `security` | Security-related | Dependency vulnerabilities, input validation |
| `dependencies` | Package management | Dependency updates, version compatibility |
| `testing` | Test improvements | New test cases, CI/CD improvements |

### 🧩 Component Labels
Architecture-specific labels for PPTX Shredder:

| Label | Component | Scope |
|-------|-----------|-------|
| `component: extractor` | `src/extractor.py` | PPTX content extraction, slide parsing |
| `component: formatter` | `src/formatter.py` | Markdown generation, chunking logic |
| `component: mcp-server` | `mcp_server.py`, `bin/` | MCP integration, Claude Desktop |
| `component: cli` | `src/shred.py` | Command-line interface, Rich UI |
| `component: tests` | `tests/` | Test suite, coverage, quality |
| `component: ci/cd` | `.github/workflows/` | GitHub Actions, automation |
| `component: docs` | `README.md`, `docs/` | Documentation, guides |

**🎯 Usage**: Always add a component label to help contributors find relevant issues in their area of expertise.

### ⚡ Priority System
Clear priority hierarchy for issue management:

| Label | Timeline | Criteria |
|-------|----------|----------|
| `priority: critical` | Immediate | Blocks releases, security issues, data loss |
| `priority: high` | This sprint | User-facing bugs, important features |
| `priority: medium` | Next sprint | Enhancements, non-critical bugs |
| `priority: low` | Future | Nice-to-have improvements, minor issues |

### 📏 Effort Estimation
Help contributors choose appropriate issues:

| Label | Time Estimate | Examples |
|-------|---------------|----------|
| `size: xs` | < 1 hour | Typo fixes, small doc updates |
| `size: s` | 1-4 hours | Simple bug fixes, minor enhancements |
| `size: m` | 4-8 hours | Medium features, refactoring |
| `size: l` | 1-2 days | Complex features, major changes |
| `size: xl` | 2+ days | Architecture changes, large features |

### 📊 Status Tracking
Workflow management for issues and PRs:

| Label | Meaning | Action Required |
|-------|---------|-----------------|
| `status: blocked` | Cannot proceed | Identify and resolve blocker |
| `status: in-progress` | Being worked on | Regular updates expected |
| `status: needs-review` | Ready for feedback | Review and provide feedback |
| `status: ready-to-merge` | Approved | Merge when ready |
| `status: on-hold` | Temporarily paused | Revisit when circumstances change |

### 🎯 PPTX Shredder Specific
Domain-specific labels for our unique functionality:

| Label | Focus Area | Examples |
|-------|------------|----------|
| `instructional-design` | Learning patterns | Module detection, learning objectives |
| `llm-optimization` | AI compatibility | Token counting, chunk optimization |
| `markdown-output` | Output format | YAML frontmatter, formatting |
| `pptx-processing` | Input handling | Slide extraction, content parsing |
| `chunking-strategy` | Content segmentation | Overlap logic, size optimization |
| `metadata-extraction` | Structured data | Speaker notes, slide metadata |

## 📝 Labeling Best Practices

### For Issue Creation
1. **Always include**: Type label (`bug`, `feature`, etc.)
2. **Add component**: Which part of the system is affected
3. **Set priority**: How urgent is this issue
4. **Estimate size**: Help contributors choose appropriate work
5. **Consider community**: Is this suitable for `help wanted` or `good first issue`?

### Example Well-Labeled Issue
```
Title: "Extractor fails on PPTX files with embedded videos"
Labels: bug, component: extractor, priority: high, size: m, help wanted
```

### For Pull Requests
1. **Match issue labels**: Inherit relevant labels from the issue
2. **Add status**: Track the PR's progress
3. **Component focus**: Which components are modified
4. **Breaking changes**: Mark with `breaking-change` if applicable

### Example Well-Labeled PR
```
Title: "Fix video content extraction in PPTX files"
Labels: bug, component: extractor, status: needs-review, size: m
```

## 🚀 Setup Instructions

### Quick Setup (Recommended)
```bash
# Make sure you're authenticated with GitHub CLI
gh auth login

# Run the automated script
./.github/create-labels.sh
```

### Manual Setup
1. Import the JSON file via GitHub web interface
2. Navigate to your repository → Issues → Labels → Import labels
3. Upload `.github/labels.json`

### Verification
Check that all labels were created:
```bash
gh label list
```

## 🎉 Benefits of This System

### For Contributors
- **Easy navigation**: Find issues in your area of expertise
- **Clear expectations**: Understand effort and complexity
- **Guided contribution**: `good first issue` and `mentor available` labels

### For Maintainers
- **Efficient triage**: Quick categorization and prioritization
- **Community building**: Clear paths for new contributors
- **Project tracking**: Status and progress visibility

### For Users
- **Transparent development**: See what's being worked on
- **Feature requests**: Understand priority and status
- **Bug reporting**: Use correct labels for faster response

## 🔄 Label Evolution

This labeling system will evolve with the project. Consider:

- **Quarterly review**: Are labels being used effectively?
- **Community feedback**: What labels would help contributors?
- **Project growth**: New components may need new labels
- **Usage analytics**: GitHub Insights show label usage patterns

---

**Remember**: Good labeling is like good documentation - it saves time for everyone and makes the project more welcoming to contributors! 🎯