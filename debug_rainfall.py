#!/usr/bin/env python
"""Debug rainfall extraction"""

import pdfplumber
import re

pdf_path = 'dataset/pdfs/pagasa-22-tc08/PAGASA_22-TC08_Henry_TCB#05.pdf'
with pdfplumber.open(pdf_path) as pdf:
    text = pdf.pages[0].extract_text()

# Extract rainfall section
pattern = r'(?:HAZARDS\s+AFFECTING\s+LAND\s+AREAS)(.*?)(?:HAZARDS AFFECTING COASTAL WATERS|Severe Winds)'
match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
if match:
    section = match.group(1)
    print('RAINFALL SECTION:')
    print(section[:1200])
    print()
    print('=' * 60)
    print()
    
    # Look for Light to moderate pattern
    level2_pattern = r'light\s+to\s+moderate\s+with\s+at\s+times\s+heavy'
    for match2 in re.finditer(level2_pattern, section, re.IGNORECASE):
        print(f'Found level 2 match at position {match2.start()}: {repr(section[match2.start():match2.end()])}')
        
        # Find 'over' keyword
        remaining = section[match2.end():]
        over_match = re.search(r'\s+(?:over|in|affecting)\s+', remaining, re.IGNORECASE)
        if over_match:
            location_start = match2.end() + over_match.end()
            location_text = section[location_start:location_start+300]
            print(f'Raw location text: {repr(location_text)}')
            print()
