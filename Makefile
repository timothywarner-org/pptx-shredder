# PPTX Shredder - Development Makefile
# Lightning-fast development commands

.PHONY: help install test test-fast test-cov lint format clean run run-dry dev build all

# Default target
help: ## Show this help message
	@echo "🎯 PPTX Shredder Development Commands"
	@echo "=================================="
	@awk 'BEGIN {FS = ":.*##"; printf "\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ 🚀 Quick Start
install: ## Install all dependencies
	@echo "📦 Installing dependencies..."
	@pip install -r requirements.txt -r requirements-dev.txt

run: ## Run PPTX Shredder (scans input/ folder)
	@echo "🎯 Running PPTX Shredder..."
	@PYTHONPATH=src python shred.py

run-dry: ## Run in dry-run mode (preview only)
	@echo "🔍 Running dry-run preview..."
	@PYTHONPATH=src python shred.py --dry-run --verbose

##@ 🧪 Testing
test: ## Run all tests
	@echo "🧪 Running all tests..."
	@PYTHONPATH=src python -m pytest tests/ -v

test-fast: ## Run tests (stop on first failure)
	@echo "🏃‍♂️ Running fast tests..."
	@PYTHONPATH=src python -m pytest tests/ -x --tb=line

test-cov: ## Run tests with coverage report
	@echo "📊 Running tests with coverage..."
	@PYTHONPATH=src python -m pytest tests/ --cov=src --cov-report=html --cov-report=term-missing
	@echo "📊 Coverage report: htmlcov/index.html"

##@ 🎨 Code Quality
format: ## Format code with black
	@echo "🎨 Formatting code..."
	@black src/ tests/ --line-length=88

lint: ## Lint code with pylint
	@echo "🔍 Linting code..."
	@pylint src/

type-check: ## Type check with mypy
	@echo "🔬 Type checking..."
	@mypy src/

##@ 🧹 Maintenance
clean: ## Clean cache and temporary files
	@echo "🧹 Cleaning cache..."
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@rm -rf .pytest_cache htmlcov .coverage 2>/dev/null || true
	@echo "✨ Cleaned!"

##@ 🏗️ Build
build: format lint test ## Full build pipeline (format + lint + test)
	@echo "✅ Build complete!"

all: clean install build ## Complete setup from scratch
	@echo "🎉 All done! Ready to shred some PPTXs!"

##@ 🔧 Development
dev: install ## Set up development environment
	@echo "🔧 Setting up development environment..."
	@echo "export PYTHONPATH=$(pwd)/src" >> ~/.bashrc || true
	@echo "✅ Development environment ready!"

demo: ## Create and process demo presentation
	@echo "🎬 Creating demo presentation..."
	@PYTHONPATH=src python -c "
import sys; sys.path.insert(0, 'src')
from pptx import Presentation
prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[0])
slide.shapes.title.text = 'Demo: PPTX Shredder'
slide.placeholders[1].text = 'Transform presentations into LLM-ready markdown!'
import os; os.makedirs('input', exist_ok=True)
prs.save('input/demo.pptx')
print('📁 Created input/demo.pptx')
"
	@$(MAKE) run
	@echo "🎉 Demo complete! Check output/ folder"

##@ 📊 Info
info: ## Show project info
	@echo "📊 PPTX Shredder Project Info"
	@echo "============================"
	@echo "Python version: $$(python --version)"
	@echo "Pip version: $$(pip --version)"
	@echo "Project files:"
	@find . -name "*.py" -not -path "./.venv/*" -not -path "./venv/*" | wc -l | xargs echo "  Python files:"
	@find tests/ -name "test_*.py" | wc -l | xargs echo "  Test files:"
	@echo "  Total LOC: $$(find . -name '*.py' -not -path './.venv/*' -not -path './venv/*' -exec wc -l {} + | tail -1 | awk '{print $$1}')"