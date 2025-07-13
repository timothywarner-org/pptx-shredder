"""
PPTX content extraction module.

Extracts text content, speaker notes, slide titles, and structural information
from PowerPoint presentations while preserving instructional design elements.
"""

import re
from typing import List, Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass

from pptx import Presentation
from pptx.shapes.base import BaseShape
from pptx.enum.shapes import MSO_SHAPE_TYPE


@dataclass
class SlideData:
    """Container for extracted slide data."""
    slide_number: int
    title: Optional[str]
    content: List[str]
    speaker_notes: str
    code_blocks: List[Dict[str, str]]
    is_module_start: bool
    learning_objectives: List[str]
    activity_type: Optional[str]


class PPTXExtractor:
    """Extracts content from PowerPoint presentations with instructional design awareness."""
    
    # Keywords that indicate the start of a new module/section
    MODULE_MARKERS = [
        'module', 'section', 'chapter', 'unit', 'lesson', 
        'part', 'topic', 'agenda', 'overview'
    ]
    
    # Keywords that indicate learning activities
    ACTIVITY_MARKERS = {
        'lab': 'lab',
        'exercise': 'exercise', 
        'practice': 'practice',
        'demo': 'demo',
        'demonstration': 'demo',
        'try it': 'hands-on',
        'hands-on': 'hands-on',
        'activity': 'activity',
        'assignment': 'assignment',
        'quiz': 'assessment',
        'test': 'assessment',
        'assessment': 'assessment',
        'review': 'review'
    }
    
    def __init__(self, pptx_path: str):
        """Initialize extractor with PowerPoint file path."""
        self.pptx_path = Path(pptx_path)
        self.presentation = Presentation(str(self.pptx_path))
        
    def extract(self) -> List[SlideData]:
        """Extract all content from the presentation."""
        slides_data = []
        
        for slide_num, slide in enumerate(self.presentation.slides, 1):
            slide_data = self._extract_slide(slide, slide_num)
            slides_data.append(slide_data)
            
        return slides_data
    
    def _extract_slide(self, slide, slide_number: int) -> SlideData:
        """Extract content from a single slide."""
        title = self._extract_title(slide)
        content = self._extract_content(slide)
        speaker_notes = self._extract_speaker_notes(slide)
        code_blocks = self._extract_code_blocks(slide)
        
        # Analyze slide for instructional patterns
        is_module_start = self._is_module_start(title, content)
        learning_objectives = self._extract_learning_objectives(content, speaker_notes)
        activity_type = self._detect_activity_type(title, content)
        
        return SlideData(
            slide_number=slide_number,
            title=title,
            content=content,
            speaker_notes=speaker_notes,
            code_blocks=code_blocks,
            is_module_start=is_module_start,
            learning_objectives=learning_objectives,
            activity_type=activity_type
        )
    
    def _extract_title(self, slide) -> Optional[str]:
        """Extract slide title using shape type and position heuristics."""
        # Try to get title from slide layout first
        if slide.shapes.title:
            return slide.shapes.title.text.strip()
        
        # Fallback: look for text at the top of the slide
        title_candidates = []
        for shape in slide.shapes:
            if hasattr(shape, 'text') and shape.text.strip():
                # Check if shape is positioned like a title (top 25% of slide)
                if hasattr(shape, 'top') and shape.top < slide.slide_height * 0.25:
                    title_candidates.append((shape.text.strip(), shape.top))
        
        if title_candidates:
            # Return the topmost text as title
            title_candidates.sort(key=lambda x: x[1])
            return title_candidates[0][0]
        
        return None
    
    def _extract_content(self, slide) -> List[str]:
        """Extract all text content from slide shapes."""
        content = []
        
        for shape in slide.shapes:
            if shape == slide.shapes.title:
                continue  # Skip title, handled separately
                
            if hasattr(shape, 'text') and shape.text.strip():
                content.append(shape.text.strip())
            elif shape.shape_type == MSO_SHAPE_TYPE.GROUP:
                # Handle grouped shapes
                content.extend(self._extract_from_group(shape))
            elif hasattr(shape, 'text_frame'):
                # Handle text frames
                text = self._extract_from_text_frame(shape.text_frame)
                if text:
                    content.append(text)
        
        return content
    
    def _extract_from_group(self, group_shape) -> List[str]:
        """Extract text from grouped shapes."""
        content = []
        for shape in group_shape.shapes:
            if hasattr(shape, 'text') and shape.text.strip():
                content.append(shape.text.strip())
        return content
    
    def _extract_from_text_frame(self, text_frame) -> str:
        """Extract formatted text from text frame."""
        if not text_frame.text.strip():
            return ""
        
        # For now, just return plain text
        # TODO: Preserve formatting for lists, emphasis, etc.
        return text_frame.text.strip()
    
    def _extract_speaker_notes(self, slide) -> str:
        """Extract speaker notes from slide."""
        if slide.has_notes_slide:
            notes_slide = slide.notes_slide
            if notes_slide.notes_text_frame:
                return notes_slide.notes_text_frame.text.strip()
        return ""
    
    def _extract_code_blocks(self, slide) -> List[Dict[str, str]]:
        """Identify and extract code blocks from slide content."""
        code_blocks = []
        
        for shape in slide.shapes:
            if hasattr(shape, 'text') and shape.text.strip():
                text = shape.text.strip()
                
                # Heuristics for identifying code:
                # 1. Monospace font indicators
                # 2. Common code patterns
                # 3. Indentation patterns
                if self._looks_like_code(text, shape):
                    language = self._detect_language(text)
                    code_blocks.append({
                        'code': text,
                        'language': language
                    })
        
        return code_blocks
    
    def _looks_like_code(self, text: str, shape) -> bool:
        """Determine if text looks like code using various heuristics."""
        # Check for common code indicators
        code_indicators = [
            '{', '}', '()', '[]', ';', '->', '=>', 
            'function', 'def ', 'class ', 'import ', 'from ',
            'SELECT', 'INSERT', 'UPDATE', 'DELETE',
            '$', '#', '//', '/*', '*/', '<!--', '-->'
        ]
        
        text_lower = text.lower()
        indicator_count = sum(1 for indicator in code_indicators if indicator in text_lower)
        
        # If multiple indicators present, likely code
        if indicator_count >= 2:
            return True
        
        # Check for indentation patterns (common in code)
        lines = text.split('\n')
        indented_lines = sum(1 for line in lines if line.startswith(('  ', '\t')))
        if len(lines) > 1 and indented_lines / len(lines) > 0.3:
            return True
        
        return False
    
    def _detect_language(self, code: str) -> str:
        """Attempt to detect programming language from code content."""
        code_lower = code.lower()
        
        # Simple language detection based on keywords (order matters - more specific first)
        if any(keyword in code_lower for keyword in ['select ', 'insert ', 'update ', 'delete ', 'where ']):
            return 'sql'
        elif any(keyword in code_lower for keyword in ['def ', 'import ', 'from ', 'print(']):
            return 'python'
        elif any(keyword in code_lower for keyword in ['function', 'var ', 'let ', 'const ', 'console.log']):
            return 'javascript'
        elif any(keyword in code_lower for keyword in ['<div', '<span', '<html', '<body']):
            return 'html'
        elif any(keyword in code_lower for keyword in ['public class', 'private ', 'public static']):
            return 'java'
        elif any(keyword in code_lower for keyword in ['using ', 'namespace', 'public class']):
            return 'csharp'
        
        return 'text'  # Default fallback
    
    def _is_module_start(self, title: Optional[str], content: List[str]) -> bool:
        """Determine if slide marks the start of a new module/section."""
        if not title:
            return False
        
        title_lower = title.lower()
        return any(marker in title_lower for marker in self.MODULE_MARKERS)
    
    def _extract_learning_objectives(self, content: List[str], speaker_notes: str) -> List[str]:
        """Extract learning objectives from slide content and speaker notes."""
        objectives = []
        all_text = ' '.join(content) + ' ' + speaker_notes
        
        # Look for common objective patterns
        objective_patterns = [
            r'(?:objective|goal|aim|learn|understand|be able to)[s]?[:\-]?\s*(.+)',
            r'(?:by the end|after this|upon completion)[^.]*you (?:will|should)[^.]*(.+)',
            r'(?:students will|learners will|you will)[^.]*(.+)'
        ]
        
        for pattern in objective_patterns:
            matches = re.finditer(pattern, all_text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                objective = match.group(1).strip()
                if len(objective) > 10:  # Filter out very short matches
                    objectives.append(objective)
        
        return objectives
    
    def _detect_activity_type(self, title: Optional[str], content: List[str]) -> Optional[str]:
        """Detect the type of learning activity represented by the slide."""
        if not title:
            return None
        
        title_lower = title.lower()
        all_content = ' '.join(content).lower()
        
        # Check title and content for activity markers
        for marker, activity_type in self.ACTIVITY_MARKERS.items():
            if marker in title_lower or marker in all_content:
                return activity_type
        
        return None