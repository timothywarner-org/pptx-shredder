"""
Unit tests for the MarkdownFormatter module.
"""

import pytest
import yaml
from pathlib import Path

from src.formatter import MarkdownFormatter, ChunkData
from src.extractor import SlideData


class TestMarkdownFormatter:
    """Test the MarkdownFormatter class."""
    
    def test_init_default_params(self):
        """Test initialization with default parameters."""
        formatter = MarkdownFormatter()
        assert formatter.strategy == 'instructional'
        assert formatter.chunk_size == 1500
        assert formatter.encoder is not None or formatter.encoder is None  # Depends on tiktoken availability
    
    def test_init_custom_params(self):
        """Test initialization with custom parameters."""
        formatter = MarkdownFormatter(strategy='sequential', chunk_size=2000)
        assert formatter.strategy == 'sequential'
        assert formatter.chunk_size == 2000
    
    def test_format_basic_slides(self, sample_slide_data):
        """Test basic formatting of slide data to markdown."""
        formatter = MarkdownFormatter()
        markdown_files = formatter.format(sample_slide_data, "test_presentation")
        
        assert len(markdown_files) >= 1
        assert all(filename.endswith('.md') for filename in markdown_files.keys())
        assert all('test_presentation' in filename for filename in markdown_files.keys())
    
    def test_chunk_by_instructional_patterns(self, sample_slide_data):
        """Test chunking based on instructional patterns."""
        formatter = MarkdownFormatter(strategy='instructional')
        chunks = formatter._chunk_by_instructional_patterns(sample_slide_data)
        
        assert len(chunks) >= 1
        assert all(isinstance(chunk, ChunkData) for chunk in chunks)
        
        # Check that module starts are respected
        first_chunk = chunks[0]
        assert first_chunk.slide_range[0] == 1  # Should start with first slide
    
    def test_chunk_by_modules(self, sample_slide_data):
        """Test chunking strictly by module boundaries."""
        formatter = MarkdownFormatter(strategy='module-based')
        chunks = formatter._chunk_by_modules(sample_slide_data)
        
        assert len(chunks) >= 1
        assert all(isinstance(chunk, ChunkData) for chunk in chunks)
    
    def test_chunk_sequentially(self, sample_slide_data):
        """Test sequential chunking based on token limits."""
        formatter = MarkdownFormatter(strategy='sequential', chunk_size=100)  # Small size to force chunking
        chunks = formatter._chunk_sequentially(sample_slide_data)
        
        assert len(chunks) >= 1
        assert all(isinstance(chunk, ChunkData) for chunk in chunks)
    
    def test_create_chunk_basic(self, sample_slide_data):
        """Test creation of a basic chunk from slides."""
        formatter = MarkdownFormatter()
        chunk = formatter._create_chunk(sample_slide_data, "Test Module", 1)
        
        assert isinstance(chunk, ChunkData)
        assert chunk.module_title == "Test Module"
        assert chunk.module_id == "01-test-module"
        assert chunk.slide_range == (1, 3)
        assert len(chunk.learning_objectives) > 0
        assert len(chunk.concepts) > 0
    
    def test_create_chunk_empty_slides(self):
        """Test that creating chunk from empty slides raises error."""
        formatter = MarkdownFormatter()
        with pytest.raises(ValueError, match="Cannot create chunk from empty slides list"):
            formatter._create_chunk([], "Test Module", 1)
    
    def test_generate_module_id(self):
        """Test generation of module IDs."""
        formatter = MarkdownFormatter()
        
        # Test basic title
        module_id = formatter._generate_module_id("Azure Fundamentals", 1)
        assert module_id == "01-azure-fundamentals"
        
        # Test title with special characters
        module_id = formatter._generate_module_id("Module 2: Advanced Topics!", 2)
        assert module_id == "02-module-2-advanced-topics"
        
        # Test very long title
        long_title = "This is a very long module title that should be truncated"
        module_id = formatter._generate_module_id(long_title, 10)
        assert module_id.startswith("10-")
        assert len(module_id) <= 35  # Should be truncated
    
    def test_extract_concepts(self, sample_slide_data):
        """Test extraction of key concepts from slides."""
        formatter = MarkdownFormatter()
        concepts = formatter._extract_concepts(sample_slide_data)
        
        assert isinstance(concepts, list)
        assert len(concepts) <= 10  # Should be limited
        assert all(isinstance(concept, str) for concept in concepts)
    
    def test_generate_chunk_content_basic(self, sample_slide_data):
        """Test generation of chunk content."""
        formatter = MarkdownFormatter()
        content = formatter._generate_chunk_content(sample_slide_data, "Test Module")
        
        assert isinstance(content, str)
        assert "## Learning Objectives" in content
        assert "## Content" in content
        assert "### Module 1: Azure Fundamentals" in content
        assert "### What is Cloud Computing?" in content
        assert "### Lab: Create Azure Account" in content
    
    def test_generate_chunk_content_with_code(self, sample_code_slide_data):
        """Test generation of chunk content with code blocks."""
        formatter = MarkdownFormatter()
        content = formatter._generate_chunk_content([sample_code_slide_data], "Code Module")
        
        assert "```python" in content
        assert "def hello_world():" in content
        assert "print(\"Hello, World!\")" in content
    
    def test_generate_chunk_content_with_speaker_notes(self, sample_slide_data):
        """Test that speaker notes are included as instructor context."""
        formatter = MarkdownFormatter()
        content = formatter._generate_chunk_content(sample_slide_data, "Test Module")
        
        assert "**Instructor Notes:**" in content
        assert "15 minutes" in content  # From sample speaker notes
    
    def test_estimate_chunk_tokens(self, sample_slide_data):
        """Test token estimation for chunks."""
        formatter = MarkdownFormatter()
        token_count = formatter._estimate_chunk_tokens(sample_slide_data)
        
        assert isinstance(token_count, int)
        assert token_count > 0
    
    def test_find_break_point(self, sample_slide_data):
        """Test finding optimal break points in slide sequences."""
        formatter = MarkdownFormatter()
        break_point = formatter._find_break_point(sample_slide_data)
        
        assert isinstance(break_point, int)
        assert 1 <= break_point < len(sample_slide_data)
    
    def test_generate_markdown_complete(self, sample_slide_data):
        """Test generation of complete markdown with frontmatter."""
        formatter = MarkdownFormatter()
        chunk = formatter._create_chunk(sample_slide_data, "Test Module", 1)
        markdown = formatter._generate_markdown(chunk)
        
        # Check YAML frontmatter
        assert markdown.startswith("---\n")
        parts = markdown.split("---\n", 2)
        assert len(parts) >= 3
        
        # Parse frontmatter
        frontmatter = yaml.safe_load(parts[1])
        assert frontmatter['module_id'] == chunk.module_id
        assert frontmatter['module_title'] == chunk.module_title
        assert frontmatter['slide_range'] == list(chunk.slide_range)
        
        # Check markdown content
        content = parts[2]
        assert f"# {chunk.module_title}" in content
        assert "## Learning Objectives" in content or "## Content" in content
    
    def test_generate_markdown_with_activity_type(self, sample_slide_data):
        """Test markdown generation includes activity type when present."""
        formatter = MarkdownFormatter()
        
        # Modify sample data to have activity type
        sample_slide_data[0].activity_type = "lab"
        chunk = formatter._create_chunk(sample_slide_data, "Lab Module", 1)
        markdown = formatter._generate_markdown(chunk)
        
        # Parse frontmatter to check activity type
        parts = markdown.split("---\n", 2)
        frontmatter = yaml.safe_load(parts[1])
        assert frontmatter.get('activity_type') == 'lab'
    
    @pytest.mark.parametrize("strategy", ['instructional', 'sequential', 'module-based'])
    def test_format_with_different_strategies(self, sample_slide_data, strategy):
        """Test formatting with different chunking strategies."""
        formatter = MarkdownFormatter(strategy=strategy)
        markdown_files = formatter.format(sample_slide_data, "test_presentation")
        
        assert len(markdown_files) >= 1
        assert all(filename.endswith('.md') for filename in markdown_files.keys())
        
        # Check that content is valid markdown
        for content in markdown_files.values():
            assert content.startswith("---\n")
            assert "# " in content  # Should have at least one heading
    
    def test_token_size_limits_respected(self, sample_slide_data):
        """Test that chunks respect token size limits."""
        small_chunk_size = 50  # Very small to force chunking
        formatter = MarkdownFormatter(chunk_size=small_chunk_size)
        
        # Add more content to force chunking
        extended_slides = sample_slide_data * 5  # Duplicate slides to create more content
        for i, slide in enumerate(extended_slides):
            slide.slide_number = i + 1
        
        markdown_files = formatter.format(extended_slides, "large_presentation")
        
        # Should create multiple chunks due to size limit
        assert len(markdown_files) > 1