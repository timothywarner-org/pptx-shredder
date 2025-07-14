#!/bin/bash
# Local Content Quality Check Script
# Run this script locally to check markdown formatting and URLs before committing

set -e

echo "🔍 PPTX Shredder Content Quality Check"
echo "====================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if required tools are installed
check_dependencies() {
    echo -e "${BLUE}Checking dependencies...${NC}"
    
    if ! command -v node &> /dev/null; then
        echo -e "${RED}❌ Node.js is required but not installed${NC}"
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        echo -e "${RED}❌ npm is required but not installed${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Dependencies check passed${NC}"
}

# Install markdown linting tools
install_tools() {
    echo -e "${BLUE}Installing markdown tools...${NC}"
    
    if ! command -v markdownlint-cli2 &> /dev/null; then
        echo "Installing markdownlint-cli2..."
        npm install -g markdownlint-cli2
    fi
    
    if ! command -v markdown-link-check &> /dev/null; then
        echo "Installing markdown-link-check..."
        npm install -g markdown-link-check
    fi
    
    echo -e "${GREEN}✅ Tools installation completed${NC}"
}

# Run markdown linting
lint_markdown() {
    echo -e "${BLUE}🔍 Linting markdown files...${NC}"
    
    if markdownlint-cli2 "**/*.md" "!node_modules/**" "!.git/**"; then
        echo -e "${GREEN}✅ All markdown files pass linting checks!${NC}"
        return 0
    else
        echo -e "${RED}❌ Markdown linting failed${NC}"
        echo -e "${YELLOW}Common issues to fix:${NC}"
        echo "   • Missing blank lines around headings"
        echo "   • Missing blank lines around lists"
        echo "   • Inconsistent heading styles"
        echo "   • Long lines (>120 chars)"
        echo "   • Trailing whitespace"
        return 1
    fi
}

# Check URL validity
check_urls() {
    echo -e "${BLUE}🔗 Checking URLs in markdown files...${NC}"
    
    local failed_files=0
    local total_files=0
    
    echo "Creating URL validation report..."
    echo "# URL Validation Report" > url-report.md
    echo "Generated on: $(date)" >> url-report.md
    echo "" >> url-report.md
    
    # Check each markdown file
    for file in $(find . -name "*.md" -not -path "./node_modules/*" -not -path "./.git/*"); do
        echo "Checking: $file"
        total_files=$((total_files + 1))
        
        if markdown-link-check "$file" --config .markdown-link-check.json --quiet; then
            echo "✅ $file - All links valid" >> url-report.md
        else
            echo "❌ $file - Contains broken links" >> url-report.md
            failed_files=$((failed_files + 1))
        fi
    done
    
    echo "" >> url-report.md
    echo "## Summary" >> url-report.md
    echo "- Total files checked: $total_files" >> url-report.md
    echo "- Files with broken links: $failed_files" >> url-report.md
    
    if [ $total_files -gt 0 ]; then
        local success_rate=$(( (total_files - failed_files) * 100 / total_files ))
        echo "- Success rate: ${success_rate}%" >> url-report.md
    fi
    
    # Display results
    if [ $failed_files -eq 0 ]; then
        echo -e "${GREEN}✅ All URLs are valid!${NC}"
        echo -e "${GREEN}📊 Report saved to url-report.md${NC}"
        return 0
    else
        echo -e "${RED}❌ Found broken links in $failed_files file(s)${NC}"
        echo -e "${YELLOW}📊 Detailed report saved to url-report.md${NC}"
        return 1
    fi
}

# Check formatting specifics
check_formatting() {
    echo -e "${BLUE}📝 Checking specific formatting rules...${NC}"
    
    local issues_found=0
    
    # Check for missing blank lines before headings
    echo "Checking blank lines before headings..."
    if grep -rn --include="*.md" -B1 "^##\|^###\|^####" . | grep -v "^--$" | grep -v "^$" | grep -A1 -B1 "^[^-].*:.*[^#]$" | head -5; then
        echo -e "${YELLOW}⚠️  Found headings that may need blank lines before them${NC}"
        issues_found=1
    fi
    
    # Check for missing blank lines around lists
    echo "Checking list formatting..."
    if grep -rn --include="*.md" -B1 -A1 "^[-*+] \|^[0-9]\+\. " . | grep -v "^--$" | grep -B1 -A1 "^[^-]*\.md-[0-9]*-[-*+0-9]" | grep -v "^$" | head -5; then
        echo -e "${YELLOW}⚠️  Found potential list formatting issues${NC}"
        issues_found=1
    fi
    
    if [ $issues_found -eq 0 ]; then
        echo -e "${GREEN}✅ Formatting checks passed${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Some formatting issues detected${NC}"
        return 0  # Don't fail on formatting warnings
    fi
}

# Create quality summary
create_summary() {
    local lint_result=$1
    local url_result=$2
    local format_result=$3
    
    echo -e "${BLUE}📊 Creating quality summary...${NC}"
    
    echo "# 📊 Content Quality Summary" > quality-summary.md
    echo "Generated on: $(date)" >> quality-summary.md
    echo "" >> quality-summary.md
    
    if [ $lint_result -eq 0 ]; then
        echo "✅ **Markdown Linting**: All files pass formatting checks" >> quality-summary.md
    else
        echo "❌ **Markdown Linting**: Issues found with formatting" >> quality-summary.md
    fi
    
    if [ $url_result -eq 0 ]; then
        echo "✅ **URL Validation**: All links are valid" >> quality-summary.md
    else
        echo "❌ **URL Validation**: Broken links detected" >> quality-summary.md
    fi
    
    if [ $format_result -eq 0 ]; then
        echo "✅ **Formatting Rules**: All specific formatting checks passed" >> quality-summary.md
    else
        echo "⚠️ **Formatting Rules**: Minor formatting issues detected" >> quality-summary.md
    fi
    
    echo "" >> quality-summary.md
    echo "## 🛠️ Quick Fixes" >> quality-summary.md
    echo "- Add blank lines before and after headings" >> quality-summary.md
    echo "- Add blank lines before and after lists" >> quality-summary.md
    echo "- Use consistent heading styles (ATX: #, ##, ###)" >> quality-summary.md
    echo "- Keep lines under 120 characters" >> quality-summary.md
    echo "- Update any 404 URLs found in url-report.md" >> quality-summary.md
    
    echo -e "${GREEN}📊 Summary saved to quality-summary.md${NC}"
}

# Main execution
main() {
    local check_type="${1:-all}"
    
    case $check_type in
        "markdown-only")
            echo -e "${BLUE}Running markdown checks only...${NC}"
            check_dependencies
            install_tools
            lint_markdown
            lint_result=$?
            check_formatting
            format_result=$?
            create_summary $lint_result 0 $format_result
            exit $lint_result
            ;;
        "urls-only")
            echo -e "${BLUE}Running URL checks only...${NC}"
            check_dependencies
            install_tools
            check_urls
            url_result=$?
            create_summary 0 $url_result 0
            exit $url_result
            ;;
        "all"|*)
            echo -e "${BLUE}Running all content quality checks...${NC}"
            check_dependencies
            install_tools
            
            lint_markdown
            lint_result=$?
            
            check_urls
            url_result=$?
            
            check_formatting
            format_result=$?
            
            create_summary $lint_result $url_result $format_result
            
            if [ $lint_result -eq 0 ] && [ $url_result -eq 0 ]; then
                echo -e "${GREEN}🎉 All content quality checks passed!${NC}"
                exit 0
            else
                echo -e "${RED}❌ Some content quality checks failed${NC}"
                exit 1
            fi
            ;;
    esac
}

# Help message
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "PPTX Shredder Content Quality Check"
    echo ""
    echo "Usage: $0 [check_type]"
    echo ""
    echo "Check types:"
    echo "  all            Run all checks (default)"
    echo "  markdown-only  Run only markdown linting"
    echo "  urls-only      Run only URL validation"
    echo ""
    echo "Examples:"
    echo "  $0                    # Run all checks"
    echo "  $0 markdown-only      # Check markdown formatting only"
    echo "  $0 urls-only          # Check URLs only"
    exit 0
fi

# Run main function
main "$@"