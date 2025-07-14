#!/bin/bash
# GitHub Labels Setup Script for PPTX Shredder
# Run this script to create all project labels using GitHub CLI

set -e

echo "🏷️  Creating GitHub labels for PPTX Shredder..."
echo "📁 Repository: timothywarner-org/pptx-shredder"
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed. Please install it first:"
    echo "   https://cli.github.com/"
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Please authenticate with GitHub CLI first:"
    echo "   gh auth login"
    exit 1
fi

echo "✅ GitHub CLI is ready"
echo ""

# Function to create a label
create_label() {
    local name="$1"
    local color="$2"
    local description="$3"
    
    echo "Creating label: $name"
    gh label create "$name" --color "$color" --description "$description" || echo "  ↳ Label already exists or failed to create"
}

# Community & Contributors
echo "🤝 Creating community labels..."
create_label "help wanted" "008672" "Looking for community help and contributions"
create_label "good first issue" "7057ff" "Perfect for newcomers to the project"
create_label "good first PR" "7057ff" "Ideal first pull request for new contributors"
create_label "hacktoberfest" "ff6b35" "Suitable for Hacktoberfest participation"
create_label "mentor available" "1d76db" "Maintainer available to guide contributors"

# Issue Types
echo ""
echo "🏷️  Creating issue type labels..."
create_label "bug" "d73a4a" "Something isn't working correctly"
create_label "enhancement" "a2eeef" "Improvement to existing functionality"
create_label "feature" "0075ca" "New functionality or capability"
create_label "documentation" "0052cc" "Documentation updates or improvements"
create_label "refactor" "fbca04" "Code cleanup and restructuring"
create_label "performance" "ff9500" "Performance optimization and improvements"
create_label "security" "b60205" "Security-related issues or improvements"
create_label "dependencies" "0366d6" "Updates to dependencies or package management"
create_label "testing" "1a7f37" "Test-related changes or improvements"

# Components
echo ""
echo "🧩 Creating component labels..."
create_label "component: extractor" "e1f5fe" "PPTX content extraction functionality"
create_label "component: formatter" "f3e5f5" "Markdown formatting and chunking"
create_label "component: mcp-server" "fff3e0" "Model Context Protocol server integration"
create_label "component: cli" "e8f5e8" "Command-line interface and Rich UI"
create_label "component: tests" "f0f4ff" "Test suite and quality assurance"
create_label "component: ci/cd" "fef7e0" "Continuous integration and deployment"
create_label "component: docs" "fdf4ff" "Documentation and README files"

# Priority
echo ""
echo "⚡ Creating priority labels..."
create_label "priority: critical" "b60205" "Urgent issue requiring immediate attention"
create_label "priority: high" "d93f0b" "High priority issue"
create_label "priority: medium" "fbca04" "Medium priority issue"
create_label "priority: low" "0e8a16" "Low priority issue"

# Size/Effort
echo ""
echo "📏 Creating size labels..."
create_label "size: xs" "c2e0c6" "Extra small change (< 1 hour)"
create_label "size: s" "7cfc00" "Small change (1-4 hours)"
create_label "size: m" "ffd700" "Medium change (4-8 hours)"
create_label "size: l" "ff8c00" "Large change (1-2 days)"
create_label "size: xl" "ff4500" "Extra large change (2+ days)"

# Status
echo ""
echo "📊 Creating status labels..."
create_label "status: blocked" "d4c5f9" "Blocked by another issue or dependency"
create_label "status: in-progress" "1f883d" "Currently being worked on"
create_label "status: needs-review" "fbca04" "Ready for review and feedback"
create_label "status: ready-to-merge" "0e8a16" "Approved and ready for merge"
create_label "status: on-hold" "d4c5f9" "Temporarily paused or postponed"

# PPTX Shredder Specific
echo ""
echo "🎯 Creating PPTX Shredder specific labels..."
create_label "instructional-design" "ff6b35" "Related to learning objectives and educational patterns"
create_label "llm-optimization" "f7931e" "LLM compatibility and token optimization"
create_label "markdown-output" "0969da" "Markdown generation and formatting"
create_label "pptx-processing" "d73527" "PowerPoint file handling and extraction"
create_label "chunking-strategy" "8b5cf6" "Content chunking and segmentation logic"
create_label "metadata-extraction" "06b6d4" "YAML frontmatter and metadata handling"

# General
echo ""
echo "📋 Creating general labels..."
create_label "question" "d876e3" "General questions about the project"
create_label "duplicate" "cfd3d7" "Duplicate issue or pull request"
create_label "invalid" "e4e669" "Invalid issue or pull request"
create_label "wontfix" "ffffff" "Issue will not be addressed"
create_label "breaking-change" "b60205" "Changes that break backward compatibility"
create_label "cross-platform" "0052cc" "Issues affecting Windows, macOS, or Linux compatibility"

echo ""
echo "✅ All labels created successfully!"
echo ""
echo "🎉 Your repository now has a comprehensive labeling system:"
echo "   • Community & contributor onboarding labels"
echo "   • Component-specific labels for PPTX Shredder architecture"
echo "   • Priority and effort estimation labels"
echo "   • Status tracking labels"
echo "   • Domain-specific labels for instructional design and LLM optimization"
echo ""
echo "💡 Pro tip: Use these labels consistently to help contributors find the right issues!"