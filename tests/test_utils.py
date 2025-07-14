"""
Tests for utility functions.
"""

import pytest
from src.utils import sanitize_filename, is_pptx_file, load_config


class TestFilenameSanitization:
    """Test filename sanitization functionality."""
    
    def test_sanitize_basic_filename(self):
        """Test basic filename sanitization."""
        result = sanitize_filename("normal_file.md")
        assert result == "normal_file.md"
    
    def test_sanitize_special_characters(self):
        """Test removal of special characters."""
        result = sanitize_filename("file<>:\"/\\|?*.md")
        assert result == "file__________.md"
    
    def test_sanitize_whitespace(self):
        """Test whitespace normalization."""
        result = sanitize_filename("file   with    spaces.md")
        assert result == "file_with_spaces.md"
    
    def test_sanitize_windows_reserved_names(self):
        """Test Windows reserved name handling."""
        result = sanitize_filename("CON.md")
        assert result == "file_CON.md"
        
        result = sanitize_filename("com1.md")
        assert result == "file_com1.md"
    
    def test_sanitize_long_filename(self):
        """Test long filename truncation."""
        long_name = "a" * 200 + ".md"
        result = sanitize_filename(long_name)
        assert len(result) <= 154  # 150 + ".md"
        assert result.endswith(".md")
    
    def test_sanitize_empty_filename(self):
        """Test empty filename handling."""
        result = sanitize_filename("")
        assert result == "untitled.md"
        
        result = sanitize_filename(None)
        assert result == "untitled.md"
    
    def test_sanitize_hidden_file(self):
        """Test hidden file handling."""
        result = sanitize_filename(".hidden.md")
        assert result == "file.hidden.md"
    
    def test_sanitize_no_extension(self):
        """Test filename without extension."""
        result = sanitize_filename("filename")
        assert result == "filename.md"
    
    def test_sanitize_unicode_control_chars(self):
        """Test Unicode control character removal."""
        result = sanitize_filename("file\x00\x01\x1f.md")
        assert result == "file___.md"
    
    def test_sanitize_enterprise_examples(self):
        """Test real-world enterprise filename examples."""
        test_cases = [
            ("Azure Training Module 1: Introduction.md", "Azure_Training_Module_1_Introduction.md"),
            ("AWS Solutions Architect (Advanced).md", "AWS_Solutions_Architect_(Advanced).md"),
            ("Data Science & ML Fundamentals.md", "Data_Science_&_ML_Fundamentals.md"),
            ("Microsoft 365 - Admin Guide.md", "Microsoft_365_-_Admin_Guide.md"),
        ]
        
        for input_name, expected in test_cases:
            result = sanitize_filename(input_name)
            # Should be safe for filesystem
            assert not any(char in result for char in '<>:"/\\|?*')
            assert len(result) <= 154


class TestFileValidation:
    """Test file validation functions."""
    
    def test_is_pptx_file(self):
        """Test PPTX file detection."""
        assert is_pptx_file("presentation.pptx") is True
        assert is_pptx_file("presentation.ppt") is True
        assert is_pptx_file("PRESENTATION.PPTX") is True
        assert is_pptx_file("document.docx") is False
        assert is_pptx_file("image.jpg") is False
        assert is_pptx_file("presentation") is False


class TestConfiguration:
    """Test configuration loading."""
    
    def test_get_default_config(self):
        """Test default configuration structure."""
        from src.utils import get_default_config
        config = get_default_config()
        
        assert 'chunking' in config
        assert 'content' in config
        assert 'output' in config
        
        # Check default values
        assert config['chunking']['strategy'] == 'instructional'
        assert config['chunking']['max_tokens'] == 2000
        assert config['content']['include_speaker_notes'] is True
        assert config['output']['format'] == 'markdown'