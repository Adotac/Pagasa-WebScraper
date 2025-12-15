#!/usr/bin/env python
"""Debug signal extraction logic"""

import pdfplumber
import re
from typhoon_extraction_ml import SignalWarningExtractor, LocationMatcher

pdf_path = 'dataset/pdfs/pagasa-20-19W/PAGASA_20-19W_Pepito_SWB#05.pdf'

with pdfplumber.open(pdf_path) as pdf:
    text = "\n".join([page.extract_text() for page in pdf.pages])

text_clean = re.sub(r'\s+', ' ', text.lower())

# Test the pattern
pattern = r'(?:signal|tcws|tropical\s+cyclone\s+wind\s+signal)[^0-9]*?#?(\d)'
matches = re.findall(pattern, text_clean, re.IGNORECASE)
print(f"Signal number matches: {matches}")

# Test the extractor
location_matcher = LocationMatcher()
extractor = SignalWarningExtractor(location_matcher)
signals = extractor.extract_signals(text)

print(f"\nExtracted signals: {signals}")

# Test location extraction
locations = location_matcher.extract_locations(text)
print(f"\nExtracted locations: {locations}")
