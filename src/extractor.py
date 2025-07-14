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
    """Container for extracted slide data with comprehensive pedagogical metadata."""
    slide_number: int
    title: Optional[str]
    content: List[str]
    speaker_notes: str
    code_blocks: List[Dict[str, str]]
    is_module_start: bool
    learning_objectives: List[str]
    activity_type: Optional[str]
    # Enhanced pedagogical metadata
    instructor_notes: Dict[str, List[str]]  # categorized by type
    prerequisites: List[str]
    difficulty_level: str
    estimated_time: int  # minutes
    visual_elements: List[Dict[str, str]]
    structured_content: Dict[str, Any]  # preserved formatting
    assessment_items: List[Dict[str, str]]
    compliance_markers: List[str]
    slide_layout_type: str


class PPTXExtractor:
    """Extracts content from PowerPoint presentations with instructional design awareness."""
    
    # Keywords that indicate the start of a new module/section
    MODULE_MARKERS = [
        'module', 'section', 'chapter', 'unit', 'lesson', 
        'part', 'topic', 'agenda', 'overview'
    ]
    
    # Keywords that indicate learning activities (enterprise training focused)
    ACTIVITY_MARKERS = {
        'lab': 'hands-on-lab',
        'exercise': 'guided-exercise', 
        'practice': 'practice-session',
        'demo': 'demonstration',
        'demonstration': 'demonstration',
        'try it': 'hands-on-activity',
        'hands-on': 'hands-on-activity',
        'activity': 'learning-activity',
        'assignment': 'assignment',
        'quiz': 'knowledge-check',
        'test': 'assessment',
        'assessment': 'formal-assessment',
        'review': 'knowledge-review',
        'troubleshooting': 'troubleshooting-scenario',
        'case study': 'case-study',
        'scenario': 'scenario-based-learning',
        'best practice': 'best-practices',
        'real world': 'real-world-application',
        'certification': 'certification-prep'
    }
    
    # Instructor note categorization patterns
    INSTRUCTOR_NOTE_PATTERNS = {
        'timing': [r'(?:time|duration|minutes?):', r'(?:spend|allow|take)\s+\d+\s*(?:min|minutes?)'],
        'emphasis': [r'(?:important|key|critical|note|remember):', r'(?:emphasize|highlight|stress)'],
        'examples': [r'(?:example|instance|case|scenario):', r'for example', r'such as'],
        'tips': [r'(?:tip|hint|suggestion):', r'pro tip', r'best practice'],
        'warnings': [r'(?:warning|caution|avoid|don\'t):', r'be careful', r'watch out'],
        'context': [r'(?:context|background|why):', r'the reason', r'this is because'],
        'delivery': [r'(?:say|tell|explain|mention):', r'make sure to', r'don\'t forget']
    }
    
    # Difficulty indicators
    DIFFICULTY_MARKERS = {
        'beginner': ['basic', 'introduction', 'fundamentals', 'getting started', 'overview'],
        'intermediate': ['intermediate', 'advanced concepts', 'diving deeper', 'detailed'],
        'advanced': ['advanced', 'expert', 'deep dive', 'complex', 'enterprise', 'production']
    }
    
    # Compliance and certification markers
    COMPLIANCE_MARKERS = [
        'certification', 'certified', 'compliance', 'audit', 'security', 
        'gdpr', 'hipaa', 'sox', 'iso', 'nist', 'pci', 'regulation'
    ]
    
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
        """Extract content from a single slide with comprehensive pedagogical analysis."""
        title = self._extract_title(slide)
        content = self._extract_content(slide)
        speaker_notes = self._extract_speaker_notes(slide)
        code_blocks = self._extract_code_blocks(slide)
        
        # Analyze slide for instructional patterns
        is_module_start = self._is_module_start(title, content)
        learning_objectives = self._extract_learning_objectives(content, speaker_notes)
        activity_type = self._detect_activity_type(title, content)
        
        # Enhanced pedagogical extraction
        instructor_notes = self._categorize_instructor_notes(speaker_notes)
        prerequisites = self._extract_prerequisites(content, speaker_notes)
        difficulty_level = self._assess_difficulty_level(title, content, speaker_notes)
        estimated_time = self._estimate_slide_time(content, speaker_notes, activity_type)
        visual_elements = self._extract_visual_elements(slide)
        structured_content = self._extract_structured_content(slide)
        assessment_items = self._extract_assessment_items(content, speaker_notes)
        compliance_markers = self._extract_compliance_markers(content, speaker_notes)
        slide_layout_type = self._detect_slide_layout(slide)
        
        return SlideData(
            slide_number=slide_number,
            title=title,
            content=content,
            speaker_notes=speaker_notes,
            code_blocks=code_blocks,
            is_module_start=is_module_start,
            learning_objectives=learning_objectives,
            activity_type=activity_type,
            instructor_notes=instructor_notes,
            prerequisites=prerequisites,
            difficulty_level=difficulty_level,
            estimated_time=estimated_time,
            visual_elements=visual_elements,
            structured_content=structured_content,
            assessment_items=assessment_items,
            compliance_markers=compliance_markers,
            slide_layout_type=slide_layout_type
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
                if hasattr(shape, 'top') and shape.top < self.presentation.slide_height * 0.25:
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
    
    def _categorize_instructor_notes(self, speaker_notes: str) -> Dict[str, List[str]]:
        """Categorize speaker notes by pedagogical intent."""
        categories = {
            'timing': [],
            'emphasis': [],
            'examples': [],
            'tips': [],
            'warnings': [],
            'context': [],
            'delivery': []
        }
        
        if not speaker_notes:
            return categories
            
        # Split notes into sentences for analysis
        sentences = re.split(r'[.!?]+', speaker_notes)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 5:  # Skip very short fragments
                continue
                
            # Check each category pattern
            for category, patterns in self.INSTRUCTOR_NOTE_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, sentence, re.IGNORECASE):
                        categories[category].append(sentence)
                        break
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}
    
    def _extract_prerequisites(self, content: List[str], speaker_notes: str) -> List[str]:
        """Extract prerequisite knowledge from content and notes."""
        prerequisites = []
        all_text = ' '.join(content) + ' ' + speaker_notes
        
        # Patterns for prerequisite detection
        prereq_patterns = [
            r'(?:prerequisite|requirement|need to know|should know|familiar with)[s]?[:\-]?\s*(.+)',
            r'(?:before|prior to|first)[^.]*(?:understand|know|learn)[^.]*(.+)',
            r'(?:assumes?|assuming)[^.]*(?:knowledge|experience)[^.]*(.+)'
        ]
        
        for pattern in prereq_patterns:
            matches = re.finditer(pattern, all_text, re.IGNORECASE)
            for match in matches:
                prereq = match.group(1).strip()
                if len(prereq) > 5 and len(prereq) < 100:  # Reasonable length
                    prerequisites.append(prereq)
        
        return prerequisites[:3]  # Limit to top 3
    
    def _assess_difficulty_level(self, title: Optional[str], content: List[str], speaker_notes: str) -> str:
        """Assess the difficulty level of the slide content."""
        all_text = ' '.join([title or ''] + content + [speaker_notes]).lower()
        
        # Score each difficulty level
        scores = {'beginner': 0, 'intermediate': 0, 'advanced': 0}
        
        for level, markers in self.DIFFICULTY_MARKERS.items():
            for marker in markers:
                scores[level] += all_text.count(marker)
        
        # Determine difficulty based on scores and content complexity
        max_score = max(scores.values())
        if max_score == 0:
            # Use heuristics: code blocks and technical terms suggest higher difficulty
            code_indicators = len(re.findall(r'[{}();]', all_text))
            if code_indicators > 5:
                return 'advanced'
            elif code_indicators > 2:
                return 'intermediate'
            else:
                return 'beginner'
        
        return max(scores, key=scores.get)
    
    def _estimate_slide_time(self, content: List[str], speaker_notes: str, activity_type: Optional[str]) -> int:
        """Estimate time needed for slide in minutes."""
        # Base time calculation
        content_length = sum(len(text) for text in content)
        notes_length = len(speaker_notes)
        
        # Base time: ~150 words per minute reading speed
        base_time = (content_length + notes_length) / (150 * 5)  # Rough chars per word
        
        # Activity type multipliers
        activity_multipliers = {
            'hands-on-lab': 10,
            'guided-exercise': 5,
            'practice-session': 3,
            'demonstration': 2,
            'hands-on-activity': 4,
            'troubleshooting-scenario': 8,
            'case-study': 6
        }
        
        multiplier = activity_multipliers.get(activity_type, 1)
        estimated_minutes = max(1, int(base_time * multiplier))
        
        return min(estimated_minutes, 45)  # Cap at 45 minutes
    
    def _extract_visual_elements(self, slide) -> List[Dict[str, str]]:
        """Extract information about visual elements on the slide."""
        visual_elements = []
        
        for shape in slide.shapes:
            element = {}
            
            if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                element = {
                    'type': 'image',
                    'description': 'Image content (extraction not yet implemented)',
                    'position': f'top={getattr(shape, "top", 0)}, left={getattr(shape, "left", 0)}'
                }
            elif shape.shape_type == MSO_SHAPE_TYPE.TABLE:
                element = {
                    'type': 'table',
                    'description': f'Table with {getattr(shape.table, "rows", "unknown")} rows' if hasattr(shape, 'table') else 'Table structure',
                    'data': 'Table data extraction pending'
                }
            elif shape.shape_type == MSO_SHAPE_TYPE.CHART:
                element = {
                    'type': 'chart',
                    'description': 'Chart or graph',
                    'chart_type': 'Chart type detection pending'
                }
            elif shape.shape_type == MSO_SHAPE_TYPE.DIAGRAM:
                element = {
                    'type': 'diagram',
                    'description': 'Diagram or SmartArt',
                    'content': 'Diagram content extraction pending'
                }
            
            if element:
                visual_elements.append(element)
        
        return visual_elements
    
    def _extract_structured_content(self, slide) -> Dict[str, Any]:
        """Extract content with preserved structure and formatting."""
        structured = {
            'lists': [],
            'emphasized_text': [],
            'headings': [],
            'layout_sections': []
        }
        
        for shape in slide.shapes:
            if hasattr(shape, 'text_frame') and shape.text_frame:
                # Extract list structures
                if hasattr(shape.text_frame, 'paragraphs'):
                    list_items = []
                    for para in shape.text_frame.paragraphs:
                        if para.level > 0:  # Indented = list item
                            list_items.append({
                                'text': para.text.strip(),
                                'level': para.level,
                                'bullet_style': 'bullet'  # Could be enhanced to detect actual style
                            })
                    if list_items:
                        structured['lists'].append(list_items)
                
                # Extract emphasized text (would need run-level analysis for bold/italic)
                text = shape.text.strip()
                if text and len(text) < 100:  # Likely emphasized if short
                    # Simple heuristic: ALL CAPS suggests emphasis
                    if text.isupper() and len(text) > 3:
                        structured['emphasized_text'].append(text)
        
        return structured
    
    def _extract_assessment_items(self, content: List[str], speaker_notes: str) -> List[Dict[str, str]]:
        """Extract quiz questions, assessments, and knowledge checks."""
        assessment_items = []
        all_text = ' '.join(content) + ' ' + speaker_notes
        
        # Question patterns
        question_patterns = [
            r'(What (?:is|are|do|does)[^?]*\\?)',
            r'(How (?:do|does|can|will)[^?]*\\?)',
            r'(Why (?:is|are|do|does)[^?]*\\?)',
            r'(Which (?:of|one)[^?]*\\?)',
            r'(True or False[^?]*\\?)'
        ]
        
        for pattern in question_patterns:
            matches = re.finditer(pattern, all_text, re.IGNORECASE)
            for match in matches:
                question = match.group(1).strip()
                assessment_items.append({
                    'type': 'question',
                    'content': question,
                    'format': 'multiple_choice' if 'which' in question.lower() else 'open_ended'
                })
        
        return assessment_items
    
    def _extract_compliance_markers(self, content: List[str], speaker_notes: str) -> List[str]:
        """Extract compliance and certification related markers."""
        compliance_items = []
        all_text = ' '.join(content + [speaker_notes]).lower()
        
        for marker in self.COMPLIANCE_MARKERS:
            if marker in all_text:
                compliance_items.append(marker.upper())
        
        return list(set(compliance_items))  # Remove duplicates
    
    def _detect_slide_layout(self, slide) -> str:
        """Detect the semantic layout type of the slide."""
        shape_types = [shape.shape_type for shape in slide.shapes]
        
        # Simple layout detection based on content
        if MSO_SHAPE_TYPE.TABLE in shape_types:
            return 'data-table'
        elif MSO_SHAPE_TYPE.CHART in shape_types:
            return 'data-visualization'
        elif MSO_SHAPE_TYPE.PICTURE in shape_types:
            return 'image-focused'
        elif len([s for s in slide.shapes if hasattr(s, 'text') and len(s.text) > 100]) > 2:
            return 'content-heavy'
        elif slide.shapes.title and len(slide.shapes) <= 3:
            return 'title-slide'
        else:
            return 'standard-content'