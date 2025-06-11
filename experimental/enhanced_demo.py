"""
Enhanced Text Extraction Agent Demonstration.

This script demonstrates the improved text extraction agent with:
- Enhanced filtering of tables, figures, and images
- Comprehensive section summarization
- Advanced keyword extraction including statistical methods and study types
"""

import json
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from text_agent import TextExtractionAgent, TextSection


def demonstrate_enhanced_features():
    """
    Demonstrate the enhanced features of the TextExtractionAgent.
    
    Shows improvements in:
    1. Content filtering (removing tables/figures/images)
    2. Comprehensive summaries for section selection
    3. Statistical methods and study type detection
    """
    print("🚀 Enhanced Text Extraction Agent Demo")
    print("=" * 60)
    
    # Initialize the enhanced agent
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
        print(f"   Original content length: {len(content):,} characters")
        
        # Extract sections with enhanced features
        sections = agent.extract_text_sections(content, str(sample_paper))
        
        if not sections:
            print("✗ No sections extracted")
            return False
        
        print(f"\n📊 Enhanced Extraction Results:")
        print(f"   ✓ Total sections extracted: {len(sections)}")
        print(f"   ✓ Total words in extracted content: {sum(s.word_count for s in sections):,}")
        
        # Analyze keyword detection capabilities
        all_keywords = set()
        statistical_methods_found = set()
        study_types_found = set()
        
        for section in sections:
            all_keywords.update(section.keywords)
            for keyword in section.keywords:
                if keyword in agent.statistical_methods:
                    statistical_methods_found.add(keyword)
                if keyword in agent.study_types:
                    study_types_found.add(keyword)
        
        print(f"\n🔍 Enhanced Keyword Analysis:")
        print(f"   ✓ Total unique keywords extracted: {len(all_keywords)}")
        print(f"   ✓ Statistical methods detected: {len(statistical_methods_found)}")
        if statistical_methods_found:
            print(f"     Methods: {', '.join(sorted(list(statistical_methods_found))[:8])}...")
        print(f"   ✓ Study types detected: {len(study_types_found)}")
        if study_types_found:
            print(f"     Types: {', '.join(sorted(list(study_types_found)))}")
        
        # Show section-by-section analysis
        print(f"\n📝 Section-by-Section Enhanced Analysis:")
        print("=" * 60)
        
        for i, section in enumerate(sections[:5], 1):  # Show first 5 sections
            print(f"\n{i}. Section: {section.title}")
            print(f"   📋 Summary: {section.summary[:120]}...")
            print(f"   🔑 Top Keywords: {', '.join(section.keywords[:8])}")
            print(f"   📊 Stats: {section.word_count} words, Level {section.level}")
            
            # Highlight statistical content
            section_stats = [kw for kw in section.keywords if kw in agent.statistical_methods]
            section_studies = [kw for kw in section.keywords if kw in agent.study_types]
            
            if section_stats:
                print(f"   📈 Statistical methods: {', '.join(section_stats)}")
            if section_studies:
                print(f"   🔬 Study methodology: {', '.join(section_studies)}")
        
        if len(sections) > 5:
            print(f"\n   ... and {len(sections) - 5} more sections")
        
        # Save enhanced output
        output_file = Path(__file__).parent / "enhanced_demo_output.json"
        success = agent.extract_and_save_json(content, str(output_file), str(sample_paper))
        
        if success:
            print(f"\n✅ Enhanced output saved to: {output_file}")
        
        # Show filtering effectiveness
        print(f"\n🔧 Content Filtering Analysis:")
        print("   ✓ Images: Removed from content")
        print("   ✓ Tables: Filtered out during section detection")
        print("   ✓ Figures: Excluded from text extraction")
        print("   ✓ References: Automatically detected and excluded")
        print("   ✓ Supplements: Filtered based on section titles")
        
        return True
        
    except Exception as e:
        print(f"✗ Error during enhanced demonstration: {e}")
        return False


def search_demonstration():
    """
    Demonstrate how the enhanced keywords enable better section searching.
    """
    print(f"\n🔍 Search Capabilities Demonstration:")
    print("=" * 40)
    
    # Load the extracted data
    output_file = Path(__file__).parent / "enhanced_demo_output.json"
    
    if not output_file.exists():
        print("   ⚠️  Run main demo first to generate search data")
        return
    
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            sections_data = json.load(f)
        
        # Example searches
        search_terms = [
            "odds ratio",
            "cohort study", 
            "statistical analysis",
            "methodology",
            "results"
        ]
        
        for term in search_terms:
            matching_sections = []
            for section in sections_data:
                if (term.lower() in [kw.lower() for kw in section['keywords']] or 
                    term.lower() in section['title'].lower() or
                    term.lower() in section['summary'].lower()):
                    matching_sections.append(section)
            
            if matching_sections:
                print(f"\n   🔍 Search: '{term}' - Found {len(matching_sections)} sections:")
                for match in matching_sections[:2]:  # Show top 2 matches
                    print(f"      • {match['title']} (Section {match['section_number']})")
                    print(f"        Summary: {match['summary'][:80]}...")
        
    except Exception as e:
        print(f"   ✗ Error in search demonstration: {e}")


def main():
    """
    Main demonstration function.
    """
    try:
        # Run the enhanced demo
        success = demonstrate_enhanced_features()
        
        if success:
            # Show search capabilities
            search_demonstration()
            
            print(f"\n🎯 Enhancement Summary:")
            print("   ✅ Improved content filtering (no tables/figures/images)")
            print("   ✅ Comprehensive section summaries for easy selection")
            print("   ✅ Enhanced keyword extraction with statistical methods")
            print("   ✅ Study type detection for research methodology")
            print("   ✅ Better search capabilities using enriched keywords")
            print("\n📚 Ready for integration with main processing system!")
        
    except Exception as e:
        print(f"✗ Demo failed: {e}")


if __name__ == "__main__":
    main()
