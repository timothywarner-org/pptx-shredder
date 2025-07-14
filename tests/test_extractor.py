"""
Unit tests for the PPTXExtractor module.
"""

import pytest
from pathlib import Path

from src.extractor import PPTXExtractor, SlideData


class TestPPTXExtractor:
    """Test the PPTXExtractor class."""
    
    def test_init_with_valid_file(self, sample_pptx):
        """Test initialization with a valid PPTX file."""
        extractor = PPTXExtractor(str(sample_pptx))
        assert extractor.pptx_path == sample_pptx
        assert extractor.presentation is not None
    
    def test_init_with_invalid_file(self, temp_dir):
        """Test initialization with invalid file raises error."""
        invalid_path = temp_dir / "nonexistent.pptx"
        with pytest.raises(Exception):
            PPTXExtractor(str(invalid_path))
    
    def test_extract_basic_content(self, sample_pptx):
        """Test basic content extraction from PPTX."""
        extractor = PPTXExtractor(str(sample_pptx))
        slides_data = extractor.extract()
        
        assert len(slides_data) == 3
        assert all(isinstance(slide, SlideData) for slide in slides_data)
        
        # Check first slide
        first_slide = slides_data[0]
        assert first_slide.slide_number == 1
        assert "Module 1: Azure Fundamentals" in first_slide.title
        assert first_slide.is_module_start is True
        assert len(first_slide.learning_objectives) > 0
    
    def test_extract_slide_titles(self, sample_pptx):
        """Test extraction of slide titles."""
        extractor = PPTXExtractor(str(sample_pptx))
        slides_data = extractor.extract()
        
        titles = [slide.title for slide in slides_data]
        assert "Module 1: Azure Fundamentals" in titles[0]
        assert "What is Cloud Computing?" in titles[1]
        assert "Lab: Create Azure Account" in titles[2]
    
    def test_extract_speaker_notes(self, sample_pptx):
        """Test extraction of speaker notes."""
        extractor = PPTXExtractor(str(sample_pptx))
        slides_data = extractor.extract()
        
        # Check that speaker notes are extracted
        notes = [slide.speaker_notes for slide in slides_data]
        assert any("Learning objective" in note for note in notes)
        assert any("15 minutes" in note for note in notes)
    
    def test_module_detection(self, sample_pptx):
        """Test detection of module start slides."""
        extractor = PPTXExtractor(str(sample_pptx))
        slides_data = extractor.extract()
        
        # First slide should be detected as module start
        assert slides_data[0].is_module_start is True
        assert slides_data[1].is_module_start is False
        assert slides_data[2].is_module_start is False
    
    def test_activity_detection(self, sample_pptx):
        """Test detection of activity types."""
        extractor = PPTXExtractor(str(sample_pptx))
        slides_data = extractor.extract()
        
        # Lab slide should be detected
        lab_slide = slides_data[2]
        assert lab_slide.activity_type == "lab"
        
        # Other slides should not be activities
        assert slides_data[0].activity_type is None
        assert slides_data[1].activity_type is None
    
    @pytest.mark.parametrize("title,expected", [
        ("Module 1: Introduction", True),
        ("Section 2: Advanced Topics", True), 
        ("Chapter 3: Best Practices", True),
        ("Unit 4: Assessment", True),
        ("Lesson 5: Summary", True),
        ("Regular Slide Title", False),
        ("Lab: Hands-on Exercise", False),  # Lab is activity, not module
    ])
    def test_is_module_start_detection(self, sample_pptx, title, expected):
        """Test module start detection with various titles."""
        extractor = PPTXExtractor(str(sample_pptx))
        result = extractor._is_module_start(title, [])
        assert result == expected
    
    @pytest.mark.parametrize("title,expected_activity", [
        ("Lab: Create Account", "lab"),
        ("Exercise 1: Practice", "exercise"),
        ("Demo: How to Configure", "demo"),
        ("Assessment: Quiz", "assessment"),
        ("Try it: Hands-on", "hands-on"),
        ("Review Questions", "review"),
        ("Regular Content Slide", None),
    ])
    def test_activity_type_detection(self, sample_pptx, title, expected_activity):
        """Test activity type detection with various titles."""
        extractor = PPTXExtractor(str(sample_pptx))
        result = extractor._detect_activity_type(title, [])
        assert result == expected_activity
    
    def test_learning_objectives_extraction(self, sample_pptx):
        """Test extraction of learning objectives from text."""
        extractor = PPTXExtractor(str(sample_pptx))
        
        content = ["By the end of this module, you will understand cloud basics"]
        notes = "Objective: Students will be able to explain cloud computing."
        
        objectives = extractor._extract_learning_objectives(content, notes)
        assert len(objectives) > 0
        assert any("cloud" in obj.lower() for obj in objectives)
    
    def test_code_detection(self, sample_pptx):
        """Test detection of code blocks in content."""
        extractor = PPTXExtractor(str(sample_pptx))
        
        # Mock shape for testing
        class MockShape:
            def __init__(self, text):
                self.text = text
        
        # Test code-like content
        code_text = "def hello():\n    print('Hello World')\n    return True"
        assert extractor._looks_like_code(code_text, MockShape(code_text)) is True
        
        # Test regular text
        regular_text = "This is just regular presentation text"
        assert extractor._looks_like_code(regular_text, MockShape(regular_text)) is False
    
    @pytest.mark.parametrize("code,expected_language", [
        ("def hello():\n    print('world')", "python"),
        ("function test() {\n    console.log('hello');\n}", "javascript"),
        ("SELECT * FROM users WHERE id = 1", "sql"),
        ("public class Test {\n    public static void main() {}\n}", "java"),
        ("<div>Hello World</div>", "html"),
        ("using System;\nnamespace Test {}", "csharp"),
        ("Some regular text", "text"),
    ])
    def test_language_detection(self, sample_pptx, code, expected_language):
        """Test programming language detection."""
        extractor = PPTXExtractor(str(sample_pptx))
        result = extractor._detect_language(code)
        assert result == expected_language