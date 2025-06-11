"""
Demonstration of Text Extraction Agent Integration.

Shows how the TextExtractionAgent can be integrated with the existing 
paper processing system following the project's OOP patterns.
"""

import json
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from text_agent import TextExtractionAgent, TextSection


def demonstrate_integration():
    """
    Demonstrate how to integrate the TextExtractionAgent with the main system.
    
    This shows the clean interface and how it follows project patterns.
    """
    print("🔧 Text Extraction Agent Integration Demo")
    print("=" * 50)
    
    # Initialize the agent (follows dependency injection pattern)
    agent = TextExtractionAgent()
    
    # Sample paper path
    sample_paper = Path(__file__).parent.parent / "docs" / "zanella_2025-with-images.md"
    
    if not sample_paper.exists():
        print(f"✗ Sample paper not found: {sample_paper}")
        return False
    
    try:
        # Load paper content
        with open(sample_paper, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📄 Processing: {sample_paper.name}")
        
        # Extract sections (main method)
        sections = agent.extract_text_sections(content, str(sample_paper))
        
        if not sections:
            print("✗ No sections extracted")
            return False
        
        # Display summary
        print(f"\n📊 Extraction Summary:")
        print(f"   Total sections: {len(sections)}")
        print(f"   Total words: {sum(s.word_count for s in sections):,}")
        
        # Show section breakdown by level
        level_counts = {}
        for section in sections:
            level_counts[section.level] = level_counts.get(section.level, 0) + 1
        
        print(f"   Section levels:")
        for level, count in sorted(level_counts.items()):
            print(f"     Level {level}: {count} sections")
        
        # Show first few sections with their enhanced fields
        print(f"\n📋 Sample Enhanced Sections:")
        for section in sections[:2]:
            print(f"\n   🔹 {section.title}")
            print(f"      ID: {section.id}")
            print(f"      Level: {section.level}")
            print(f"      Words: {section.word_count}")
            print(f"      Summary: {section.summary}")
            print(f"      Keywords: {', '.join(section.keywords[:6])}...")
            print(f"      Preview: {section.content[:60]}...")
        
        # Show keyword analysis
        all_keywords = set()
        statistical_found = set()
        study_types_found = set()
        
        # Create agent instance to access keyword lists
        temp_agent = TextExtractionAgent()
        for section in sections:
            all_keywords.update(section.keywords)
            for keyword in section.keywords:
                if keyword in temp_agent.statistical_methods:
                    statistical_found.add(keyword)
                if keyword in temp_agent.study_types:
                    study_types_found.add(keyword)
        
        print(f"\n🔍 Enhanced Analysis:")
        print(f"   Total unique keywords: {len(all_keywords)}")
        
        # Substantial sections (>50 words)
        substantial = [s for s in sections if s.word_count > 50]
        print(f"   Substantial sections (>50 words): {len(substantial)}")
        
        # Statistical analysis detection
        if statistical_found:
            print(f"   Statistical methods detected: {', '.join(list(statistical_found)[:5])}")
        
        # Study type detection  
        if study_types_found:
            print(f"   Study types identified: {', '.join(list(study_types_found))}")
        
        # Show sections with the most keywords
        keyword_rich = sorted(sections, key=lambda s: len(s.keywords), reverse=True)[:3]
        print(f"   Most keyword-rich sections:")
        for i, section in enumerate(keyword_rich, 1):
            print(f"     {i}. {section.title} ({len(section.keywords)} keywords)")
        
        # Show JSON export capability
        output_file = Path(__file__).parent / "demo_sections.json"
        success = agent.extract_and_save_json(content, str(output_file), str(sample_paper))
        
        if success:
            print(f"\n💾 Saved to: {output_file}")
        
        print(f"\n✅ Integration demo completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Error in demo: {e}")
        return False


def show_json_structure():
    """Show the enhanced JSON structure that gets produced."""
    print("\n📋 Enhanced JSON Output Structure:")
    print("""
    Each section is now a comprehensive JSON object with:
    {
        "id": 64-bit unique identifier,
        "paper_id": null (set when integrated with main system),
        "title": "Section title/heading",
        "content": "Full verbatim text content",
        "summary": "AI-generated comprehensive summary",
        "keywords": ["keyword1", "keyword2", "statistical_method", ...],
        "section_number": Sequential order (1, 2, 3...),
        "level": Heading level (1, 2, 3...),
        "word_count": Number of words,
        "extracted_at": ISO timestamp
    }
    
    Keywords include:
    - Title and content terms
    - Statistical methods (t-test, regression, chi-square, etc.)
    - Study types (RCT, cohort, meta-analysis, etc.)
    - Academic terms (hypothesis, intervention, outcome, etc.)
    - Numerical findings (p-values, odds ratios, etc.)
    """)


if __name__ == "__main__":
    success = demonstrate_integration()
    
    if success:
        show_json_structure()
        
        print(f"\n🎯 Enhanced Integration Points:")
        print(f"   • Can be added to PaperProcessor.process_paper()")
        print(f"   • Sections can be stored using the experimental enhanced schema")
        print(f"   • IDs are compatible with existing 64-bit ID system")
        print(f"   • Follows same OOP patterns as existing codebase")
        print(f"   • Enhanced with AI-powered summaries and keyword extraction")
        print(f"   • Automatically detects statistical methods and study types")
        print(f"   • Excludes tables, figures, images, and references")
        print(f"   • Ready for migration from experimental/ to src/ when needed")
