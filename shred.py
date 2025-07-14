#!/usr/bin/env python3
"""
PPTX Shredder entry point script.
This wrapper handles module imports and runs the main CLI.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

# Now import and run the main CLI
from src.shred import shred

if __name__ == '__main__':
    shred()