# GitHub Workflows

This directory contains GitHub Actions workflows for maintaining PPTX Shredder quality and automation.

## 📋 Workflows

### Content Quality Check (`content-quality.yml`)

**Purpose**: Automated markdown linting and URL validation to ensure enterprise-grade content quality.

**Triggers**:
- 🕘 **Scheduled**: Weekly on Mondays at 9 AM UTC
- 🔄 **Manual**: Workflow dispatch with options (all/markdown-only/urls-only)
- 📝 **Pull Requests**: When markdown files are modified
- 🚀 **Push to main**: When markdown files are changed

**What it checks**:
- ✅ Markdown formatting (spacing around headings, lists, line length)
- 🔗 URL validity (detects 404s, redirects, timeouts)
- 📊 Content structure and consistency
- 🛡️ Compliance with enterprise documentation standards

**Outputs**:
- Detailed markdown linting results
- URL validation report with success rates
- Content quality summary with fix recommendations
- PR comments with check results

### Jobs Breakdown

#### 1. Markdown Linting
- **Tool**: `markdownlint-cli2` with custom rules
- **Rules**: 50+ formatting rules optimized for technical documentation
- **Focus**: Spacing, heading consistency, line length, code blocks

#### 2. URL Validation  
- **Tool**: `markdown-link-check` with retry logic
- **Features**: Handles redirects, respects rate limits, custom headers
- **Ignores**: Local URLs, localhost, email links, placeholders

#### 3. Quality Summary
- **Aggregates**: Results from all checks
- **Provides**: Actionable fix recommendations
- **Creates**: Artifacts for 30-90 day retention

## 🛠️ Configuration Files

### `.markdownlint.json`
Comprehensive markdown linting configuration:
- **MD022/MD032**: Enforces blank lines around headings and lists
- **MD013**: Line length limits (120 chars, flexible for code/tables)
- **MD003**: Consistent ATX heading style (#, ##, ###)
- **MD030**: Proper spacing in lists
- **Enterprise-friendly**: Allows necessary HTML elements

### `.markdown-link-check.json`
URL validation configuration:
- **Timeout**: 10 seconds with 3 retries
- **Rate limiting**: Handles 429 responses gracefully
- **Custom headers**: GitHub API compatibility
- **Ignores**: Development URLs, placeholders, fragments

## 🎯 Benefits

### For Content Quality
- **Consistent formatting** across all documentation
- **No broken links** in published content
- **Enterprise standards** compliance
- **Automated enforcement** of style guides

### For Contributors
- **Clear feedback** on formatting issues
- **Automated fixes** suggestions
- **Quality gates** before merge
- **Learning** markdown best practices

### For Maintainers
- **Reduced manual review** time
- **Consistent quality** standards
- **Automated reporting** and tracking
- **Historical quality** metrics

## 🔧 Local Development

Run content checks locally before pushing:

```bash
# Full content quality check
./scripts/local-content-check.sh

# Markdown only
./scripts/local-content-check.sh markdown-only

# URLs only
./scripts/local-content-check.sh urls-only
```

## 📊 Quality Metrics

The workflow tracks:
- **Success rate** of URL validation
- **Number of formatting** issues over time
- **Most common** formatting problems
- **Content quality** trends

## 🚀 Future Enhancements

Planned improvements:
- **Spelling/grammar** checking
- **Technical terminology** validation
- **Accessibility** checks (alt text, headings)
- **SEO optimization** hints
- **Multi-language** support