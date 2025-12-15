#!/usr/bin/env python
"""
Analyze a single PAGASA PDF bulletin and display extracted data in a readable format.
Usage: python analyze_pdf.py "<path_to_pdf>"
"""

from typhoon_extraction_ml import TyphoonBulletinExtractor
import json
import sys
from pathlib import Path

def display_results(data):
    """Display extraction results in a readable format"""
    print("\n" + "=" * 80)
    print("PAGASA BULLETIN EXTRACTION RESULTS")
    print("=" * 80)
    
    # Basic Info
    print("\n[BASIC INFORMATION]")
    print(f"  Issued:       {data.get('updated_datetime', 'N/A')}")
    print(f"  Location:     {data.get('typhoon_location_text', 'N/A')}")
    print(f"  Wind Speed:   {data.get('typhoon_windspeed', 'N/A')}")
    print(f"  Movement:     {data.get('typhoon_movement', 'N/A')}")
    
    # Signal Warnings
    print("\n[SIGNAL WARNINGS (TCWS)]")
    signal_found = False
    for level in range(1, 6):
        tag_key = f'signal_warning_tags{level}'
        tag = data.get(tag_key, {})
        
        # Check if any island group has locations
        has_locations = any(tag.get(ig) for ig in ['Luzon', 'Visayas', 'Mindanao', 'Other'])
        
        if has_locations:
            signal_found = True
            print(f"\n  Signal {level}:")
            for island_group in ['Luzon', 'Visayas', 'Mindanao', 'Other']:
                locations = tag.get(island_group)
                if locations:
                    print(f"    {island_group:12} → {locations}")
        else:
            print(f"\n  Signal {level}: No warnings")
    
    if not signal_found:
        print("  ✓ No tropical cyclone wind signals in effect")
    
    # Rainfall Warnings
    print("\n[RAINFALL WARNINGS]")
    rainfall_found = False
    
    rainfall_levels = {
        1: "Level 1 - Intense Rainfall (>30mm/hr, RED)",
        2: "Level 2 - Heavy Rainfall (15-30mm/hr, ORANGE)",
        3: "Level 3 - Heavy Rainfall Advisory (7.5-15mm/hr, YELLOW)"
    }
    
    for level in range(1, 4):
        tag_key = f'rainfall_warning_tags{level}'
        tag = data.get(tag_key, {})
        
        # Check if any island group has locations
        has_locations = any(tag.get(ig) for ig in ['Luzon', 'Visayas', 'Mindanao', 'Other'])
        
        if has_locations:
            rainfall_found = True
            print(f"\n  {rainfall_levels[level]}:")
            for island_group in ['Luzon', 'Visayas', 'Mindanao', 'Other']:
                locations = tag.get(island_group)
                if locations:
                    print(f"    {island_group:12} → {locations}")
        else:
            print(f"\n  {rainfall_levels[level]}: No warnings")
    
    if not rainfall_found:
        print("  ✓ No rainfall warnings issued")
    
    print("\n" + "=" * 80 + "\n")

def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_pdf.py \"<path_to_pdf>\"")
        print("\nExample:")
        print('  python analyze_pdf.py "dataset/pdfs/pagasa-20-19W/PAGASA_20-19W_Pepito_SWB#02.pdf"')
        print("\nOr for random selection:")
        print("  python analyze_pdf.py --random")
        sys.exit(1)
    
    # Handle random selection
    if sys.argv[1] == "--random":
        from pathlib import Path
        import random
        pdfs = list(Path("dataset/pdfs").rglob("*.pdf"))
        if not pdfs:
            print("Error: No PDFs found in dataset/pdfs/")
            sys.exit(1)
        pdf_path = str(random.choice(pdfs))
        print(f"Selected random PDF: {pdf_path}\n")
    else:
        pdf_path = sys.argv[1]
    
    # Verify file exists
    if not Path(pdf_path).exists():
        print(f"Error: File not found: {pdf_path}")
        sys.exit(1)
    
    print(f"Analyzing: {pdf_path}")
    print("Processing...\n")
    
    # Extract data
    extractor = TyphoonBulletinExtractor()
    data = extractor.extract_from_pdf(pdf_path)
    
    if not data:
        print("Error: Failed to extract data from PDF")
        sys.exit(1)
    
    # Display in readable format
    display_results(data)
    
    # Option to show raw JSON
    if len(sys.argv) > 2 and sys.argv[2] == "--json":
        print("RAW JSON OUTPUT:")
        print("=" * 80)
        print(json.dumps(data, indent=2))

if __name__ == "__main__":
    main()
