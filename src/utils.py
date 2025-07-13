"""
Utility functions for PPTX Shredder.

Includes configuration loading, file handling, and helper functions.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from YAML file."""
    if config_path:
        config_file = Path(config_path)
    else:
        # Look for config.yaml in current directory or parent
        config_file = Path('config.yaml')
        if not config_file.exists():
            config_file = Path(__file__).parent.parent / 'config.yaml'
    
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    else:
        # Return default configuration
        return get_default_config()


def get_default_config() -> Dict[str, Any]:
    """Return default configuration values."""
    return {
        'chunking': {
            'strategy': 'instructional',
            'max_tokens': 2000,
            'overlap_tokens': 100
        },
        'content': {
            'include_speaker_notes': True,
            'preserve_code_blocks': True,
            'detect_language': True,
            'include_slide_numbers': True
        },
        'output': {
            'format': 'markdown',
            'include_metadata': True,
            'frontmatter_format': 'yaml',
            'filename_pattern': '{original_name}_{module_id}.md'
        }
    }


def ensure_output_directory(output_dir: str) -> Path:
    """Ensure output directory exists and return Path object."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def is_pptx_file(file_path: str) -> bool:
    """Check if file is a PowerPoint presentation."""
    return Path(file_path).suffix.lower() in ['.pptx', '.ppt']


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for cross-platform compatibility."""
    # Remove or replace problematic characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove extra whitespace and normalize
    filename = ' '.join(filename.split())
    
    # Limit length
    if len(filename) > 100:
        filename = filename[:100]
    
    return filename


def count_tokens_rough(text: str) -> int:
    """Rough token count estimation (4 characters per token average)."""
    return len(text) // 4


def format_duration(minutes: float) -> str:
    """Format duration in a human-readable way."""
    if minutes < 1:
        return "< 1 minute"
    elif minutes < 60:
        return f"{int(minutes)} minutes"
    else:
        hours = int(minutes // 60)
        remaining_minutes = int(minutes % 60)
        if remaining_minutes > 0:
            return f"{hours}h {remaining_minutes}m"
        else:
            return f"{hours}h"