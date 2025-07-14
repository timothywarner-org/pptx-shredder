"""
Intelligent markdown formatter for LLM-optimized output.

This module takes the intelligent extraction results and formats them into
high-quality markdown optimized for LLM consumption.
"""

import yaml
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

@dataclass
class IntelligentChunk:
    """Container for an intelligently formatted markdown chunk."""
    module_id: str
    module_title: str
    slide_range: Tuple[int, int]
    content: str
    metadata: Dict[str, Any]

class IntelligentMarkdownFormatter:
    """Format intelligent extraction results into LLM-optimized markdown."""
    
    def __init__(self, chunk_size: int = 1500):
        """Initialize formatter with target chunk size."""
        self.chunk_size = chunk_size
    
    def format(self, slides_data: List[Dict[str, Any]], presentation_name: str) -> Dict[str, str]:
        """Format intelligent slides data into markdown files."""
        # Group slides into logical modules
        modules = self._group_slides_into_modules(slides_data)
        
        # Create chunks from modules
        chunks = []
        for module in modules:
            module_chunks = self._create_module_chunks(module)
            chunks.extend(module_chunks)
        
        # Generate markdown files
        markdown_files = {}
        for i, chunk in enumerate(chunks):
            chunk.metadata['chunk_index'] = i + 1
            chunk.metadata['total_chunks'] = len(chunks)
            
            filename = f"{presentation_name}_{chunk.module_id}.md"
            content = self._generate_markdown(chunk)
            markdown_files[filename] = content
        
        return markdown_files
    
    def _group_slides_into_modules(self, slides_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Group slides into logical learning modules."""
        modules = []
        current_module = {
            'module_id': '01-introduction',
            'module_title': 'Introduction',
            'slides': []
        }
        module_counter = 1
        
        for slide_data in slides_data:
            structure = slide_data['structure']
            
            # Check if this slide starts a new module
            if structure['is_module_start'] and current_module['slides']:
                # Finalize current module
                modules.append(current_module)
                
                # Start new module
                module_counter += 1
                current_module = {
                    'module_id': f"{module_counter:02d}-{self._create_module_id(structure['module_title'])}",
                    'module_title': structure['module_title'] or f"Module {module_counter}",
                    'slides': [slide_data]
                }
            else:
                current_module['slides'].append(slide_data)
        
        # Add final module
        if current_module['slides']:
            modules.append(current_module)
        
        return modules
    
    def _create_module_id(self, title: Optional[str]) -> str:
        """Create URL-friendly module ID from title."""
        if not title:
            return "untitled"
        
        # Clean and format title
        import re
        clean_title = re.sub(r'[^\w\s-]', '', title.lower())
        clean_title = re.sub(r'[-\s]+', '-', clean_title).strip('-')
        
        # Limit length
        if len(clean_title) > 30:
            clean_title = clean_title[:30].rstrip('-')
        
        return clean_title or "untitled"
    
    def _create_module_chunks(self, module: Dict[str, Any]) -> List[IntelligentChunk]:
        """Create chunks from a module, respecting token limits."""
        slides = module['slides']
        
        # For now, create one chunk per module (can enhance with token-based splitting later)
        if not slides:
            return []
        
        first_slide = slides[0]['content']['slide_number']
        last_slide = slides[-1]['content']['slide_number']
        
        # Aggregate module metadata
        all_objectives = []
        all_prerequisites = []
        activity_types = []
        difficulty_levels = []
        total_time = 0
        
        for slide_data in slides:
            structure = slide_data['structure']
            all_objectives.extend(structure.get('learning_objectives', []))
            all_prerequisites.extend(structure.get('prerequisites', []))
            if structure.get('activity_type'):
                activity_types.append(structure['activity_type'])
            if structure.get('difficulty_level'):
                difficulty_levels.append(structure['difficulty_level'])
            if structure.get('estimated_time_minutes'):
                total_time += structure['estimated_time_minutes']
        
        # Remove duplicates
        all_objectives = list(dict.fromkeys(all_objectives))
        all_prerequisites = list(dict.fromkeys(all_prerequisites))
        
        # Determine primary characteristics
        primary_activity = max(set(activity_types), key=activity_types.count) if activity_types else 'lecture'
        primary_difficulty = max(set(difficulty_levels), key=difficulty_levels.count) if difficulty_levels else 'intermediate'
        
        # Generate content
        content = self._generate_module_content(slides, module['module_title'])
        
        # Create metadata
        metadata = {
            'slide_range': [first_slide, last_slide],
            'learning_objectives': all_objectives,
            'prerequisites': all_prerequisites,
            'activity_type': primary_activity,
            'difficulty_level': primary_difficulty,
            'estimated_duration': f"{total_time} minutes" if total_time else "5 minutes",
            'total_slides': len(slides),
            'visual_elements': sum(len(s['content'].get('images', [])) + 
                                 len(s['content'].get('tables', [])) + 
                                 len(s['content'].get('charts', [])) for s in slides),
            'has_speaker_notes': any(s['content'].get('speaker_notes', '') for s in slides),
            'content_summary': self._create_module_summary(slides)
        }
        
        chunk = IntelligentChunk(
            module_id=module['module_id'],
            module_title=module['module_title'],
            slide_range=(first_slide, last_slide),
            content=content,
            metadata=metadata
        )
        
        return [chunk]
    
    def _generate_module_content(self, slides: List[Dict[str, Any]], module_title: str) -> str:
        """Generate high-quality markdown content for a module."""
        content_parts = []
        
        # Extract module-level information
        all_objectives = []
        all_prerequisites = []
        
        for slide_data in slides:
            structure = slide_data['structure']
            all_objectives.extend(structure.get('learning_objectives', []))
            all_prerequisites.extend(structure.get('prerequisites', []))
        
        # Remove duplicates while preserving order
        all_objectives = list(dict.fromkeys(all_objectives))
        all_prerequisites = list(dict.fromkeys(all_prerequisites))
        
        # Add prerequisites section if any exist
        if all_prerequisites:
            content_parts.extend([
                "## 📋 Prerequisites",
                "",
                "Before starting this module, you should have:",
            ])
            for prereq in all_prerequisites:
                content_parts.append(f"- {prereq}")
            content_parts.append("")
        
        # Add learning objectives
        if all_objectives:
            content_parts.extend([
                "## 🎯 Learning Objectives",
                "",
                "By the end of this module, you will be able to:",
            ])
            for obj in all_objectives:
                content_parts.append(f"- {obj}")
            content_parts.append("")
        
        # Add main content
        content_parts.extend([
            "## 📚 Content",
            ""
        ])
        
        for slide_data in slides:
            self._add_slide_content(content_parts, slide_data)
        
        return "\n".join(content_parts)
    
    def _add_slide_content(self, content_parts: List[str], slide_data: Dict[str, Any]):
        """Add content for a single slide."""
        content = slide_data['content']
        structure = slide_data['structure']
        
        # Add slide title/header
        title = content.get('title') or f"Slide {content['slide_number']}"
        
        # Add activity type icon
        activity_icon = self._get_activity_icon(structure.get('activity_type', 'lecture'))
        content_parts.append(f"### {activity_icon} {title}")
        content_parts.append("")
        
        # Add content summary if available
        if structure.get('content_summary'):
            content_parts.append(f"*{structure['content_summary']}*")
            content_parts.append("")
        
        # Add text content
        for text in content.get('text_content', []):
            content_parts.append(text)
            content_parts.append("")
        
        # Add bullet points
        bullet_points = content.get('bullet_points', [])
        if bullet_points:
            content_parts.append("**Key Points:**")
            for bp in bullet_points:
                indent = "  " * (bp.get('level', 1) - 1)
                content_parts.append(f"{indent}- {bp['text']}")
            content_parts.append("")
        
        # Add visual elements description
        images = content.get('images', [])
        tables = content.get('tables', [])
        charts = content.get('charts', [])
        
        if images or tables or charts:
            content_parts.append("**Visual Elements:**")
            for img in images:
                content_parts.append(f"- 📷 Image at position {img.get('position', 'unknown')}")
            for table in tables:
                dims = table.get('dimensions', 'unknown')
                content_parts.append(f"- 📊 Table ({dims})")
                if table.get('headers'):
                    headers = ', '.join(table['headers'][:3])
                    content_parts.append(f"  - Columns: {headers}...")
            for chart in charts:
                content_parts.append(f"- 📈 Chart at position {chart.get('position', 'unknown')}")
            content_parts.append("")
        
        # Add speaker notes if present
        speaker_notes = content.get('speaker_notes', '').strip()
        if speaker_notes:
            content_parts.append("**👨‍🏫 Instructor Notes:**")
            content_parts.append(f"> {speaker_notes[:500]}{'...' if len(speaker_notes) > 500 else ''}")
            content_parts.append("")
        
        content_parts.append("---")
        content_parts.append("")
    
    def _get_activity_icon(self, activity_type: str) -> str:
        """Get appropriate icon for activity type."""
        icons = {
            'lecture': '📚',
            'demo': '🎬',
            'lab': '🧪',
            'assessment': '📊',
            'exercise': '💪',
            'overview': '🎯',
            'conclusion': '✅'
        }
        return icons.get(activity_type, '📖')
    
    def _create_module_summary(self, slides: List[Dict[str, Any]]) -> str:
        """Create a concise summary of the module."""
        if not slides:
            return "Empty module"
        
        # Get key themes from slide summaries
        summaries = [s['structure'].get('content_summary', '') for s in slides if s['structure'].get('content_summary')]
        
        if summaries:
            # Take first summary as representative
            return summaries[0][:200] + "..." if len(summaries[0]) > 200 else summaries[0]
        else:
            return f"Module with {len(slides)} slides covering technical training content."
    
    def _generate_markdown(self, chunk: IntelligentChunk) -> str:
        """Generate the final markdown with YAML frontmatter."""
        # Create comprehensive YAML frontmatter
        frontmatter = {
            'module_id': chunk.module_id,
            'module_title': chunk.module_title,
            'slide_range': list(chunk.slide_range),
            'chunk_index': chunk.metadata.get('chunk_index', 1),
            'total_chunks': chunk.metadata.get('total_chunks', 1),
            'learning_objectives': chunk.metadata.get('learning_objectives', []),
            'prerequisites': chunk.metadata.get('prerequisites', []),
            'activity_type': chunk.metadata.get('activity_type'),
            'difficulty_level': chunk.metadata.get('difficulty_level'),
            'estimated_duration': chunk.metadata.get('estimated_duration'),
            'total_slides': chunk.metadata.get('total_slides'),
            'visual_elements_count': chunk.metadata.get('visual_elements'),
            'has_speaker_notes': chunk.metadata.get('has_speaker_notes'),
            'content_summary': chunk.metadata.get('content_summary'),
            'extraction_method': 'intelligent_llm_analysis',
            'llm_model': 'deepseek-chat'
        }
        
        # Remove empty fields
        frontmatter = {k: v for k, v in frontmatter.items() if v is not None and v != []}
        
        # Generate markdown
        markdown_parts = [
            "---",
            yaml.dump(frontmatter, default_flow_style=False, sort_keys=False).strip(),
            "---",
            "",
            f"# {chunk.module_title}",
            ""
        ]
        
        # Add chunk context if multiple chunks
        if chunk.metadata.get('total_chunks', 1) > 1:
            markdown_parts.extend([
                f"*This is part {chunk.metadata.get('chunk_index', 1)} of {chunk.metadata.get('total_chunks', 1)} in the {chunk.module_title} series.*",
                ""
            ])
        
        # Add the main content
        markdown_parts.append(chunk.content)
        
        return "\n".join(markdown_parts)