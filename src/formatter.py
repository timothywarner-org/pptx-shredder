"""
Markdown formatting module.

Converts extracted PPTX data into LLM-optimized markdown with intelligent chunking
that preserves instructional design patterns and maintains narrative flow.
"""

import re
import yaml
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False

from extractor import SlideData
from utils import sanitize_filename


@dataclass
class ChunkData:
    """Container for a markdown chunk with comprehensive pedagogical metadata."""
    module_id: str
    module_title: str
    slide_range: Tuple[int, int]
    content: str
    learning_objectives: List[str]
    concepts: List[str]
    activity_type: Optional[str]
    estimated_duration: str
    prerequisites: List[str]
    # Enhanced enterprise training metadata
    difficulty_level: str
    instructor_guidance: Dict[str, List[str]]
    assessment_items: List[Dict[str, str]]
    compliance_markers: List[str]
    visual_elements_summary: List[str]
    slide_layout_types: List[str]
    chunk_index: int
    total_chunks: int
    learning_context: Dict[str, Any]


class MarkdownFormatter:
    """Formats extracted slide data into LLM-optimized markdown chunks."""
    
    def __init__(self, strategy: str = 'instructional', chunk_size: int = 1500):
        """Initialize formatter with chunking strategy and size limits."""
        self.strategy = strategy
        self.chunk_size = chunk_size
        
        # Initialize token encoder if available
        if TIKTOKEN_AVAILABLE:
            try:
                self.encoder = tiktoken.get_encoding("cl100k_base")  # GPT-4 encoding
            except:
                self.encoder = None
        else:
            self.encoder = None
    
    def format(self, slides_data: List[SlideData], presentation_name: str) -> Dict[str, str]:
        """Format slides data into markdown files."""
        if self.strategy == 'instructional':
            chunks = self._chunk_by_instructional_patterns(slides_data)
        elif self.strategy == 'module-based':
            chunks = self._chunk_by_modules(slides_data)
        else:  # sequential
            chunks = self._chunk_sequentially(slides_data)
        
        # Generate markdown files with chunk indexing
        markdown_files = {}
        total_chunks = len(chunks)
        for i, chunk in enumerate(chunks):
            # Update chunk with total count information
            chunk.chunk_index = i + 1
            chunk.total_chunks = total_chunks
            
            # Create filename with proper sanitization
            raw_filename = f"{presentation_name}_{chunk.module_id}.md"
            filename = sanitize_filename(raw_filename)
            content = self._generate_markdown(chunk)
            markdown_files[filename] = content
        
        return markdown_files
    
    def _chunk_by_instructional_patterns(self, slides_data: List[SlideData]) -> List[ChunkData]:
        """Chunk slides based on instructional design patterns."""
        chunks = []
        current_chunk_slides = []
        current_module_title = "Introduction"
        module_counter = 1
        
        for slide in slides_data:
            # Check if this slide starts a new module
            if slide.is_module_start and current_chunk_slides:
                # Finalize current chunk  
                chunk = self._create_chunk(current_chunk_slides, current_module_title, module_counter, len(chunks) + 1, 0)  # Will update total later
                chunks.append(chunk)
                
                # Start new chunk
                current_chunk_slides = [slide]
                current_module_title = slide.title or f"Module {module_counter + 1}"
                module_counter += 1
            else:
                current_chunk_slides.append(slide)
                
                # Check if chunk is getting too large
                if self._estimate_chunk_tokens(current_chunk_slides) > self.chunk_size:
                    # Find a good break point
                    break_point = self._find_break_point(current_chunk_slides)
                    
                    # Create chunk up to break point
                    chunk_slides = current_chunk_slides[:break_point]
                    chunk = self._create_chunk(chunk_slides, current_module_title, module_counter, len(chunks) + 1, 0)  # Will update total later
                    chunks.append(chunk)
                    
                    # Continue with remaining slides
                    current_chunk_slides = current_chunk_slides[break_point:]
                    current_module_title = f"Module {module_counter + 1} (Continued)"
                    module_counter += 1
        
        # Handle final chunk
        if current_chunk_slides:
            chunk = self._create_chunk(current_chunk_slides, current_module_title, module_counter, len(chunks) + 1, 0)  # Will update total later
            chunks.append(chunk)
        
        return chunks
    
    def _chunk_by_modules(self, slides_data: List[SlideData]) -> List[ChunkData]:
        """Chunk slides strictly by module boundaries."""
        chunks = []
        current_chunk_slides = []
        current_module_title = "Introduction"
        module_counter = 1
        
        for slide in slides_data:
            if slide.is_module_start and current_chunk_slides:
                # Finalize current chunk  
                chunk = self._create_chunk(current_chunk_slides, current_module_title, module_counter, len(chunks) + 1, 0)  # Will update total later
                chunks.append(chunk)
                
                # Start new chunk
                current_chunk_slides = [slide]
                current_module_title = slide.title or f"Module {module_counter + 1}"
                module_counter += 1
            else:
                current_chunk_slides.append(slide)
        
        # Handle final chunk
        if current_chunk_slides:
            chunk = self._create_chunk(current_chunk_slides, current_module_title, module_counter, len(chunks) + 1, 0)  # Will update total later
            chunks.append(chunk)
        
        return chunks
    
    def _chunk_sequentially(self, slides_data: List[SlideData]) -> List[ChunkData]:
        """Chunk slides sequentially based on token limits."""
        chunks = []
        current_chunk_slides = []
        chunk_counter = 1
        
        for slide in slides_data:
            current_chunk_slides.append(slide)
            
            if self._estimate_chunk_tokens(current_chunk_slides) > self.chunk_size:
                # Remove last slide and create chunk
                chunk_slides = current_chunk_slides[:-1]
                if chunk_slides:  # Ensure we have content
                    chunk = self._create_chunk(chunk_slides, f"Section {chunk_counter}", chunk_counter, len(chunks) + 1, 0)  # Will update total later
                    chunks.append(chunk)
                    chunk_counter += 1
                
                # Start new chunk with the slide that exceeded limit
                current_chunk_slides = [slide]
        
        # Handle final chunk
        if current_chunk_slides:
            chunk = self._create_chunk(current_chunk_slides, f"Section {chunk_counter}", chunk_counter, len(chunks) + 1, 0)  # Will update total later
            chunks.append(chunk)
        
        return chunks
    
    def _create_chunk(self, slides: List[SlideData], module_title: str, module_number: int, chunk_index: int = 1, total_chunks: int = 1) -> ChunkData:
        """Create an enterprise-grade chunk with comprehensive pedagogical metadata."""
        if not slides:
            raise ValueError("Cannot create chunk from empty slides list")
        
        slide_range = (slides[0].slide_number, slides[-1].slide_number)
        module_id = self._generate_module_id(module_title, module_number)
        
        # Aggregate all pedagogical data
        learning_objectives = []
        prerequisites = []
        instructor_guidance = {'timing': [], 'emphasis': [], 'examples': [], 'tips': [], 'warnings': [], 'context': [], 'delivery': []}
        assessment_items = []
        compliance_markers = []
        visual_elements_summary = []
        slide_layout_types = []
        difficulty_levels = []
        total_estimated_time = 0
        
        for slide in slides:
            learning_objectives.extend(slide.learning_objectives)
            prerequisites.extend(slide.prerequisites)
            assessment_items.extend(slide.assessment_items)
            compliance_markers.extend(slide.compliance_markers)
            
            # Aggregate instructor guidance
            for category, notes in slide.instructor_notes.items():
                instructor_guidance[category].extend(notes)
            
            # Visual elements summary
            for element in slide.visual_elements:
                visual_elements_summary.append(f"{element['type']}: {element['description']}")
            
            # Layout types
            slide_layout_types.append(slide.slide_layout_type)
            difficulty_levels.append(slide.difficulty_level)
            total_estimated_time += slide.estimated_time
        
        # Remove duplicates while preserving order
        learning_objectives = list(dict.fromkeys(learning_objectives))
        prerequisites = list(dict.fromkeys(prerequisites))
        compliance_markers = list(set(compliance_markers))
        visual_elements_summary = list(dict.fromkeys(visual_elements_summary))
        
        # Extract concepts with enhanced extraction
        concepts = self._extract_enhanced_concepts(slides)
        
        # Determine primary activity type with fallback
        activity_types = [slide.activity_type for slide in slides if slide.activity_type]
        activity_type = activity_types[0] if activity_types else None
        
        # Determine overall difficulty level
        difficulty_counts = {level: difficulty_levels.count(level) for level in set(difficulty_levels)}
        difficulty_level = max(difficulty_counts, key=difficulty_counts.get) if difficulty_counts else 'beginner'
        
        # Enhanced duration estimation
        estimated_duration = self._format_duration(total_estimated_time)
        
        # Create learning context for LLM understanding
        learning_context = {
            'module_sequence_position': f"{chunk_index} of {total_chunks}",
            'primary_learning_mode': self._determine_learning_mode(slides),
            'cognitive_load': self._assess_cognitive_load(slides),
            'interaction_level': self._assess_interaction_level(slides),
            'assessment_density': len(assessment_items) / len(slides) if slides else 0
        }
        
        # Generate content
        content = self._generate_chunk_content(slides, module_title)
        
        return ChunkData(
            module_id=module_id,
            module_title=module_title,
            slide_range=slide_range,
            content=content,
            learning_objectives=learning_objectives,
            concepts=concepts,
            activity_type=activity_type,
            estimated_duration=estimated_duration,
            prerequisites=prerequisites,
            difficulty_level=difficulty_level,
            instructor_guidance=instructor_guidance,
            assessment_items=assessment_items,
            compliance_markers=compliance_markers,
            visual_elements_summary=visual_elements_summary,
            slide_layout_types=list(set(slide_layout_types)),
            chunk_index=chunk_index,
            total_chunks=total_chunks,
            learning_context=learning_context
        )
    
    def _generate_module_id(self, title: str, number: int) -> str:
        """Generate a URL-friendly module ID."""
        # Clean title and make lowercase
        clean_title = re.sub(r'[^\w\s-]', '', title.lower())
        clean_title = re.sub(r'[-\s]+', '-', clean_title).strip('-')
        
        # Limit length and add number
        if len(clean_title) > 30:
            clean_title = clean_title[:30].rstrip('-')
        
        return f"{number:02d}-{clean_title}"
    
    def _extract_concepts(self, slides: List[SlideData]) -> List[str]:
        """Extract key concepts from slides (simplified implementation)."""
        concepts = set()
        
        for slide in slides:
            if slide.title:
                # Extract meaningful words from titles
                words = re.findall(r'\b[A-Z][a-z]+\b', slide.title)
                concepts.update(words)
        
        # Return top concepts (limit to prevent frontmatter bloat)
        return sorted(list(concepts))[:10]
    
    def _generate_chunk_content(self, slides: List[SlideData], module_title: str) -> str:
        """Generate enterprise-grade content optimized for LLM comprehension."""
        content_parts = []
        
        # Extract all pedagogical metadata
        all_objectives = []
        all_prerequisites = []
        instructor_guidance = {'timing': [], 'emphasis': [], 'examples': [], 'tips': [], 'warnings': [], 'context': [], 'delivery': []}
        assessment_items = []
        
        for slide in slides:
            all_objectives.extend(slide.learning_objectives)
            all_prerequisites.extend(slide.prerequisites)
            assessment_items.extend(slide.assessment_items)
            
            # Aggregate instructor guidance
            for category, notes in slide.instructor_notes.items():
                instructor_guidance[category].extend(notes)
        
        # Remove duplicates while preserving order
        all_objectives = list(dict.fromkeys(all_objectives))
        all_prerequisites = list(dict.fromkeys(all_prerequisites))
        
        # Add prerequisites section if any exist
        if all_prerequisites:
            content_parts.append("## 📋 Prerequisites")
            content_parts.append("")
            content_parts.append("Before starting this module, you should have:")
            for prereq in all_prerequisites[:3]:  # Limit to top 3
                content_parts.append(f"- {prereq}")
            content_parts.append("")
        
        # Add learning objectives with action verbs
        if all_objectives:
            content_parts.append("## 🎯 Learning Objectives")
            content_parts.append("")
            content_parts.append("By the end of this module, you will be able to:")
            for obj in all_objectives[:5]:  # Top 5 objectives
                # Ensure objective starts with action verb
                if not any(obj.lower().startswith(verb) for verb in ['understand', 'explain', 'demonstrate', 'configure', 'implement', 'analyze']):
                    obj = f"Understand {obj.lower()}"
                content_parts.append(f"- {obj}")
            content_parts.append("")
        
        # Add main content with enhanced structure
        content_parts.append("## 📚 Content")
        content_parts.append("")
        
        for slide in slides:
            # Add slide context with layout information
            if slide.slide_layout_type in ['data-table', 'data-visualization']:
                content_parts.append(f"### 📊 {slide.title or 'Data Presentation'}")
            elif slide.slide_layout_type == 'image-focused':
                content_parts.append(f"### 🖼️ {slide.title or 'Visual Content'}")
            elif slide.activity_type:
                activity_icon = self._get_activity_icon(slide.activity_type)
                content_parts.append(f"### {activity_icon} {slide.title or slide.activity_type.title()}")
            elif slide.title:
                content_parts.append(f"### {slide.title}")
            
            content_parts.append("")
            
            # Add structured content with preserved formatting
            if slide.structured_content.get('lists'):
                for list_group in slide.structured_content['lists']:
                    for item in list_group:
                        indent = "  " * (item['level'] - 1)
                        content_parts.append(f"{indent}- {item['text']}")
                content_parts.append("")
            
            # Add regular content
            for content_item in slide.content:
                # Check if content is emphasized
                if content_item in slide.structured_content.get('emphasized_text', []):
                    content_parts.append(f"**{content_item}**")
                else:
                    content_parts.append(content_item)
                content_parts.append("")
            
            # Add visual elements description
            if slide.visual_elements:
                content_parts.append("#### Visual Elements:")
                for element in slide.visual_elements:
                    content_parts.append(f"- **{element['type'].title()}**: {element['description']}")
                content_parts.append("")
            
            # Add code blocks with enhanced context
            for code_block in slide.code_blocks:
                if slide.activity_type == 'hands-on-lab':
                    content_parts.append("#### 💻 Lab Code:")
                elif slide.activity_type == 'demonstration':
                    content_parts.append("#### 🎬 Demo Code:")
                else:
                    content_parts.append("#### Code Example:")
                
                content_parts.append(f"```{code_block['language']}")
                content_parts.append(code_block['code'])
                content_parts.append("```")
                content_parts.append("")
            
            # Add assessment items if present
            if slide.assessment_items:
                content_parts.append("#### 🧠 Knowledge Check:")
                for item in slide.assessment_items:
                    content_parts.append(f"**Q**: {item['content']}")
                content_parts.append("")
            
            # Add categorized instructor guidance
            if slide.instructor_notes:
                content_parts.append("#### 👨‍🏫 Instructor Guidance:")
                content_parts.append("")
                
                for category, notes in slide.instructor_notes.items():
                    if notes:
                        icon = self._get_guidance_icon(category)
                        content_parts.append(f"**{icon} {category.title()}:**")
                        for note in notes:
                            content_parts.append(f"- {note}")
                        content_parts.append("")
            
            # Add basic speaker notes as fallback
            elif slide.speaker_notes:
                content_parts.append(f"> **📝 Instructor Notes:** {slide.speaker_notes}")
                content_parts.append("")
        
        return "\n".join(content_parts)
    
    def _get_activity_icon(self, activity_type: str) -> str:
        """Get appropriate icon for activity type."""
        icons = {
            'hands-on-lab': '🧪',
            'guided-exercise': '📝',
            'practice-session': '💪',
            'demonstration': '🎬',
            'hands-on-activity': '🔧',
            'troubleshooting-scenario': '🔍',
            'case-study': '📋',
            'knowledge-check': '🧠',
            'formal-assessment': '📊',
            'best-practices': '⭐',
            'real-world-application': '🌍'
        }
        return icons.get(activity_type, '📚')
    
    def _get_guidance_icon(self, category: str) -> str:
        """Get appropriate icon for instructor guidance category."""
        icons = {
            'timing': '⏱️',
            'emphasis': '⚠️',
            'examples': '💡',
            'tips': '🔧',
            'warnings': '🚨',
            'context': '📖',
            'delivery': '🎯'
        }
        return icons.get(category, '📌')
    
    def _estimate_chunk_tokens(self, slides: List[SlideData]) -> int:
        """Estimate token count for a chunk."""
        if self.encoder:
            # Use tiktoken for accurate counting
            text = ""
            for slide in slides:
                if slide.title:
                    text += slide.title + " "
                text += " ".join(slide.content) + " "
                text += slide.speaker_notes + " "
            return len(self.encoder.encode(text))
        else:
            # Fallback: rough estimation (4 chars per token)
            total_chars = 0
            for slide in slides:
                if slide.title:
                    total_chars += len(slide.title)
                total_chars += sum(len(content) for content in slide.content)
                total_chars += len(slide.speaker_notes)
            return total_chars // 4
    
    def _find_break_point(self, slides: List[SlideData]) -> int:
        """Find optimal break point in slides list."""
        # Simple heuristic: break at activity transitions
        for i in range(len(slides) - 1, 0, -1):
            if slides[i].activity_type and slides[i].activity_type != slides[i-1].activity_type:
                return i
        
        # Fallback: break at 75% of chunk to leave room for overlap
        return max(1, int(len(slides) * 0.75))
    
    def _generate_markdown(self, chunk: ChunkData) -> str:
        """Generate enterprise-grade markdown optimized for LLM comprehension."""
        # Create comprehensive YAML frontmatter for LLM context
        frontmatter = {
            # Core identification
            'module_id': chunk.module_id,
            'module_title': chunk.module_title,
            'slide_range': list(chunk.slide_range),
            'chunk_index': chunk.chunk_index,
            'total_chunks': chunk.total_chunks,
            
            # Learning objectives and prerequisites
            'learning_objectives': chunk.learning_objectives,
            'prerequisites': chunk.prerequisites,
            
            # Content categorization
            'concepts': chunk.concepts,
            'difficulty_level': chunk.difficulty_level,
            'estimated_duration': chunk.estimated_duration,
            
            # Pedagogical metadata
            'learning_context': chunk.learning_context,
            'slide_layout_types': chunk.slide_layout_types,
            
            # Activity and assessment information
            'activity_type': chunk.activity_type,
            'assessment_items_count': len(chunk.assessment_items),
            
            # Enterprise metadata
            'compliance_markers': chunk.compliance_markers,
            'visual_elements_count': len(chunk.visual_elements_summary),
            
            # Instructor guidance summary
            'instructor_guidance_categories': list(chunk.instructor_guidance.keys()) if chunk.instructor_guidance else [],
            
            # LLM optimization metadata
            'token_optimization': {
                'chunk_size_target': self.chunk_size,
                'actual_token_estimate': self._estimate_chunk_tokens([]),  # Would need slide data
                'content_density': chunk.learning_context.get('cognitive_load', 'unknown'),
                'interaction_level': chunk.learning_context.get('interaction_level', 'unknown')
            }
        }
        
        # Remove empty fields to keep frontmatter clean
        frontmatter = {k: v for k, v in frontmatter.items() if v}
        
        # Generate markdown with enhanced structure
        markdown_parts = [
            "---",
            yaml.dump(frontmatter, default_flow_style=False, sort_keys=False).strip(),
            "---",
            "",
            f"# {chunk.module_title}",
            "",
        ]
        
        # Add module context for LLM
        if chunk.total_chunks > 1:
            markdown_parts.extend([
                f"*This is part {chunk.chunk_index} of {chunk.total_chunks} in the {chunk.module_title} module series.*",
                ""
            ])
        
        # Add compliance notice if applicable
        if chunk.compliance_markers:
            compliance_text = ", ".join(chunk.compliance_markers)
            markdown_parts.extend([
                f"**🔒 Compliance Notice:** This content relates to {compliance_text} requirements.",
                ""
            ])
        
        # Add the main content
        markdown_parts.append(chunk.content)
        
        # Add instructor guidance summary for LLM context
        if chunk.instructor_guidance and any(chunk.instructor_guidance.values()):
            markdown_parts.extend([
                "",
                "---",
                "",
                "## 📋 Instructor Guidance Summary",
                "",
                "*This section provides context for AI assistants about the instructional intent:*",
                ""
            ])
            
            for category, notes in chunk.instructor_guidance.items():
                if notes:
                    icon = self._get_guidance_icon(category)
                    markdown_parts.extend([
                        f"**{icon} {category.title()} ({len(notes)} items):**",
                        f"- {' '.join(notes[:2])}{'...' if len(notes) > 2 else ''}",  # Summary
                        ""
                    ])
        
        return "\n".join(markdown_parts)
    
    def _extract_enhanced_concepts(self, slides: List[SlideData]) -> List[str]:
        """Extract key concepts with enhanced semantic analysis."""
        concepts = set()
        
        for slide in slides:
            # Extract from titles with better filtering
            if slide.title:
                # Extract capitalized words and technical terms
                title_concepts = re.findall(r'\b[A-Z][a-z]+(?:[A-Z][a-z]*)*\b', slide.title)
                concepts.update(title_concepts)
            
            # Extract from emphasized content
            if slide.structured_content.get('emphasized_text'):
                for text in slide.structured_content['emphasized_text']:
                    # Technical terms often in ALL CAPS
                    if text.isupper() and 2 < len(text) < 20:
                        concepts.add(text.title())
            
            # Extract from code language indicators
            for code_block in slide.code_blocks:
                if code_block['language'] != 'text':
                    concepts.add(code_block['language'].title())
        
        # Filter and sort concepts
        filtered_concepts = [c for c in concepts if len(c) > 2 and len(c) < 30]
        return sorted(filtered_concepts)[:15]  # Top 15 concepts
    
    def _format_duration(self, minutes: int) -> str:
        """Format duration in a human-readable way."""
        if minutes < 60:
            return f"{minutes} minutes"
        else:
            hours = minutes // 60
            remaining_minutes = minutes % 60
            if remaining_minutes == 0:
                return f"{hours} hour{'s' if hours > 1 else ''}"
            else:
                return f"{hours} hour{'s' if hours > 1 else ''} {remaining_minutes} minutes"
    
    def _determine_learning_mode(self, slides: List[SlideData]) -> str:
        """Determine the primary learning mode for the chunk."""
        activity_counts = {}
        for slide in slides:
            if slide.activity_type:
                activity_counts[slide.activity_type] = activity_counts.get(slide.activity_type, 0) + 1
        
        if not activity_counts:
            return 'lecture'
        
        primary_activity = max(activity_counts, key=activity_counts.get)
        
        if 'hands-on' in primary_activity or 'lab' in primary_activity:
            return 'experiential'
        elif 'demo' in primary_activity:
            return 'observational'
        elif 'assessment' in primary_activity or 'quiz' in primary_activity:
            return 'evaluative'
        else:
            return 'instructional'
    
    def _assess_cognitive_load(self, slides: List[SlideData]) -> str:
        """Assess the cognitive load of the content."""
        load_score = 0
        
        for slide in slides:
            # Add points for complexity indicators
            load_score += len(slide.code_blocks) * 2  # Code increases load
            load_score += len(slide.content) * 0.5    # More content = more load
            load_score += len(slide.visual_elements)  # Visual processing
            
            if slide.difficulty_level == 'advanced':
                load_score += 3
            elif slide.difficulty_level == 'intermediate':
                load_score += 1
        
        avg_load = load_score / len(slides) if slides else 0
        
        if avg_load > 6:
            return 'high'
        elif avg_load > 3:
            return 'medium'
        else:
            return 'low'
    
    def _assess_interaction_level(self, slides: List[SlideData]) -> str:
        """Assess the level of learner interaction required."""
        interaction_score = 0
        
        for slide in slides:
            if slide.activity_type:
                if 'hands-on' in slide.activity_type or 'lab' in slide.activity_type:
                    interaction_score += 3
                elif 'exercise' in slide.activity_type or 'practice' in slide.activity_type:
                    interaction_score += 2
                elif 'demo' in slide.activity_type:
                    interaction_score += 1
            
            # Assessment items require interaction
            interaction_score += len(slide.assessment_items) * 2
        
        avg_interaction = interaction_score / len(slides) if slides else 0
        
        if avg_interaction > 2:
            return 'high'
        elif avg_interaction > 0.5:
            return 'medium'
        else:
            return 'low'