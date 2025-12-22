#!/usr/bin/env python
"""Debug rainfall extraction with the actual extractor"""

from typhoon_extraction_ml import TyphoonBulletinExtractor, RainfallWarningExtractor, LocationMatcher
import pdfplumber

pdf_path = 'dataset/pdfs/pagasa-22-tc08/PAGASA_22-TC08_Henry_TCB#05.pdf'
with pdfplumber.open(pdf_path) as pdf:
    full_text = "\n".join([page.extract_text() or "" for page in pdf.pages])

# Extract rainfall
matcher = LocationMatcher()
extractor = RainfallWarningExtractor(matcher)

section = extractor._extract_rainfall_section(full_text)
if section:
    print('RAINFALL SECTION found, length:', len(section))
    print('First 800 chars:')
    print(repr(section[:800]))
    print()
    
    # Now parse it
    result = extractor._parse_rainfall_section(section)
    print('Parsed result:')
    for level in [1, 2, 3]:
        print(f'  Level {level}: {result[level]}')
else:
    print('No rainfall section found')
