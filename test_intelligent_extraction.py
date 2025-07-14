#!/usr/bin/env python3
"""
Test script for intelligent PPTX extraction using DeepSeek.
"""

import json
import sys
from pathlib import Path
from dataclasses import asdict

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from intelligent_extractor import IntelligentPPTXExtractor

def test_intelligent_extraction():
    """Test the intelligent extraction on the Pluralsight file."""
    
    pptx_file = "input/administer-ghas-enterprise-m1.pptx"
    
    if not Path(pptx_file).exists():
        print(f"❌ File not found: {pptx_file}")
        return
    
    print("🧠 Testing Intelligent PPTX Extraction with DeepSeek")
    print(f"📁 File: {pptx_file}")
    print()
    
    # Initialize extractor
    extractor = IntelligentPPTXExtractor(pptx_file, use_llm=True)
    
    # Extract first few slides for testing (start with just 2 slides)
    print("🔄 Extracting slides...")
    slides = []
    
    for slide_num, slide in enumerate(list(extractor.presentation.slides)[:5], 1):  # First 5 slides
        print(f"   Processing slide {slide_num}...")
        slide_content = extractor._extract_slide_content(slide, slide_num)
        
        print(f"   Getting LLM analysis for slide {slide_num}...")
        if extractor.use_llm and extractor.client:
            instructional_structure = extractor._infer_instructional_structure(slide_content)
        else:
            instructional_structure = extractor._fallback_structure_detection(slide_content)
        
        slide_data = {
            'content': asdict(slide_content),
            'structure': asdict(instructional_structure)
        }
        slides.append(slide_data)
    
    print(f"✅ Extracted {len(slides)} slides")
    print()
    
    # Show detailed results for first 3 slides
    for i, slide_data in enumerate(slides[:3]):
        content = slide_data['content']
        structure = slide_data['structure']
        
        print(f"🎯 SLIDE {i+1}")
        print(f"   Title: {content['title']}")
        print(f"   Layout: {content['layout_name']}")
        print(f"   Text Items: {len(content['text_content'])}")
        print(f"   Bullet Points: {len(content['bullet_points'])}")
        print(f"   Speaker Notes: {len(content['speaker_notes'])} chars")
        print(f"   Visual Elements: {len(content['images'])} images, {len(content['tables'])} tables, {len(content['charts'])} charts")
        print()
        print(f"🎓 INSTRUCTIONAL ANALYSIS:")
        print(f"   Module Start: {structure['is_module_start']}")
        print(f"   Module Title: {structure['module_title']}")
        print(f"   Activity Type: {structure['activity_type']}")
        print(f"   Difficulty: {structure['difficulty_level']}")
        print(f"   Time Estimate: {structure['estimated_time_minutes']} min")
        print(f"   Learning Objectives: {len(structure['learning_objectives'])} found")
        for obj in structure['learning_objectives']:
            print(f"      • {obj}")
        print(f"   Prerequisites: {len(structure['prerequisites'])} found")
        for prereq in structure['prerequisites']:
            print(f"      • {prereq}")
        print(f"   Summary: {structure['content_summary']}")
        print(f"   Notes: {structure['instructional_notes']}")
        print()
        print("-" * 80)
        print()
    
    # Show summary statistics
    module_starts = sum(1 for slide in slides if slide['structure']['is_module_start'])
    total_objectives = sum(len(slide['structure']['learning_objectives']) for slide in slides)
    total_prerequisites = sum(len(slide['structure']['prerequisites']) for slide in slides)
    activity_types = [slide['structure']['activity_type'] for slide in slides if slide['structure']['activity_type']]
    
    print("📊 EXTRACTION SUMMARY:")
    print(f"   Total Slides: {len(slides)}")
    print(f"   Module Boundaries: {module_starts}")
    print(f"   Learning Objectives Found: {total_objectives}")
    print(f"   Prerequisites Found: {total_prerequisites}")
    print(f"   Activity Types: {set(activity_types)}")
    
    # Save detailed results
    output_file = "intelligent_extraction_results.json"
    with open(output_file, 'w') as f:
        json.dump(slides, f, indent=2)
    print(f"   Detailed results saved to: {output_file}")

if __name__ == "__main__":
    test_intelligent_extraction()