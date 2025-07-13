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


@dataclass
class ChunkData:
    """Container for a markdown chunk with metadata."""
    module_id: str
    module_title: str
    slide_range: Tuple[int, int]
    content: str
    learning_objectives: List[str]
    concepts: List[str]
    activity_type: Optional[str]
    estimated_duration: str
    prerequisites: List[str]


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
        
        # Generate markdown files
        markdown_files = {}
        for i, chunk in enumerate(chunks):
            filename = f"{presentation_name}_{chunk.module_id}.md"
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
                chunk = self._create_chunk(current_chunk_slides, current_module_title, module_counter)
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
                    chunk = self._create_chunk(chunk_slides, current_module_title, module_counter)
                    chunks.append(chunk)
                    
                    # Continue with remaining slides
                    current_chunk_slides = current_chunk_slides[break_point:]
                    current_module_title = f"Module {module_counter + 1} (Continued)"
                    module_counter += 1
        
        # Handle final chunk
        if current_chunk_slides:
            chunk = self._create_chunk(current_chunk_slides, current_module_title, module_counter)
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
                chunk = self._create_chunk(current_chunk_slides, current_module_title, module_counter)
                chunks.append(chunk)
                
                # Start new chunk
                current_chunk_slides = [slide]
                current_module_title = slide.title or f"Module {module_counter + 1}"
                module_counter += 1
            else:
                current_chunk_slides.append(slide)
        
        # Handle final chunk
        if current_chunk_slides:
            chunk = self._create_chunk(current_chunk_slides, current_module_title, module_counter)
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
                    chunk = self._create_chunk(chunk_slides, f"Section {chunk_counter}", chunk_counter)
                    chunks.append(chunk)
                    chunk_counter += 1
                
                # Start new chunk with the slide that exceeded limit
                current_chunk_slides = [slide]
        
        # Handle final chunk
        if current_chunk_slides:
            chunk = self._create_chunk(current_chunk_slides, f"Section {chunk_counter}", chunk_counter)
            chunks.append(chunk)
        
        return chunks
    
    def _create_chunk(self, slides: List[SlideData], module_title: str, module_number: int) -> ChunkData:
        """Create a chunk from a list of slides."""
        if not slides:
            raise ValueError("Cannot create chunk from empty slides list")
        
        slide_range = (slides[0].slide_number, slides[-1].slide_number)
        module_id = self._generate_module_id(module_title, module_number)
        
        # Aggregate learning objectives
        learning_objectives = []
        for slide in slides:
            learning_objectives.extend(slide.learning_objectives)
        learning_objectives = list(set(learning_objectives))  # Remove duplicates
        
        # Extract concepts (simplified - just unique title words)
        concepts = self._extract_concepts(slides)
        
        # Determine primary activity type
        activity_types = [slide.activity_type for slide in slides if slide.activity_type]
        activity_type = activity_types[0] if activity_types else None
        
        # Estimate duration (rough heuristic: 1-2 minutes per slide)
        duration_minutes = len(slides) * 1.5
        estimated_duration = f"{int(duration_minutes)} minutes"
        
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
            prerequisites=[]  # TODO: Implement prerequisite detection
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
        """Generate the main content for a chunk."""
        content_parts = []
        
        # Add overview if we have learning objectives
        all_objectives = []
        for slide in slides:
            all_objectives.extend(slide.learning_objectives)
        
        if all_objectives:
            content_parts.append("## Learning Objectives")
            for obj in all_objectives[:3]:  # Limit to top 3
                content_parts.append(f"- {obj}")
            content_parts.append("")
        
        # Add slide content
        content_parts.append("## Content")
        content_parts.append("")
        
        for slide in slides:
            # Add slide title as subsection
            if slide.title:
                content_parts.append(f"### {slide.title}")
                content_parts.append("")
            
            # Add slide content
            for content_item in slide.content:
                content_parts.append(content_item)
                content_parts.append("")
            
            # Add code blocks
            for code_block in slide.code_blocks:
                content_parts.append(f"```{code_block['language']}")
                content_parts.append(code_block['code'])
                content_parts.append("```")
                content_parts.append("")
            
            # Add speaker notes as instructor context
            if slide.speaker_notes:
                content_parts.append("> **Instructor Notes:** " + slide.speaker_notes)
                content_parts.append("")
        
        return "\n".join(content_parts)
    
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
        """Generate complete markdown file with frontmatter."""
        # Create YAML frontmatter
        frontmatter = {
            'module_id': chunk.module_id,
            'module_title': chunk.module_title,
            'slide_range': list(chunk.slide_range),
            'learning_objectives': chunk.learning_objectives,
            'concepts': chunk.concepts,
            'estimated_duration': chunk.estimated_duration
        }
        
        if chunk.activity_type:
            frontmatter['activity_type'] = chunk.activity_type
        
        if chunk.prerequisites:
            frontmatter['prerequisites'] = chunk.prerequisites
        
        # Generate markdown
        markdown_parts = [
            "---",
            yaml.dump(frontmatter, default_flow_style=False).strip(),
            "---",
            "",
            f"# {chunk.module_title}",
            "",
            chunk.content
        ]
        
        return "\n".join(markdown_parts)