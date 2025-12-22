#!/usr/bin/env python
import json
import re
from typhoon_extraction_ml import SignalWarningExtractor, LocationMatcher

matcher = LocationMatcher()
sig_extractor = SignalWarningExtractor(matcher)

# Extract from Uwan TCB#03
pdf_path = 'dataset/pdfs/pagasa-25-TC21/PAGASA_25-TC21_Uwan_TCB#03.pdf'

# Get the text and extract signal section
import pdfplumber
with pdfplumber.open(pdf_path) as pdf:
    text = pdf.pages[0].extract_text()

signal_section = sig_extractor._extract_signal_section(text)
if not signal_section:
    print("Signal section extraction failed, using raw text...")
    # Fall back to finding TCWS manually
    idx = text.find('TCWS')
    if idx >= 0:
        signal_section = text[idx:idx+8000]  # Take next 8000 chars
    else:
        print("No TCWS found!")
        exit(1)

lines = signal_section.split('\n')

# Just check what we're parsing
full_text = '\n'.join(lines)

# Find signal 1 block
pattern = rf'\n1\n'
match = re.search(pattern, full_text)
if match:
    sig_start = match.end()
    sig_end = len(full_text)
    
    # Find signal 2
    pattern2 = rf'\n2\n'
    match2 = re.search(pattern2, full_text[sig_start:])
    if match2:
        sig_end = sig_start + match2.start()
    
    signal_block = full_text[sig_start:sig_end].strip()
    print("Signal 1 raw block (first 500 chars):")
    print(signal_block[:500])
    print("\n" + "="*80 + "\n")
    
    # Clean it
    block_lines = signal_block.split('\n')
    clean_lines = []
    for line in block_lines:
        stripped = line.strip()
        if not stripped:
            continue
        if any(marker in stripped.lower() for marker in 
               ['wind threat:', 'gale-forc', 'strong winds', 'prevailing winds',
                'warning lead time:', 'range of wind speeds:', 'potential impacts',
                'minor to moderate', 'minor threat', 'moderate threat', 'property']):
            continue
        if stripped in ['-', '--', '- -']:
            continue
        clean_lines.append(stripped)
    
    location_block = ' '.join(clean_lines)
    location_block = location_block.replace(' and ', ', ')
    location_block = re.sub(r'\s+', ' ', location_block).strip()
    
    print("Signal 1 cleaned block (first 500 chars):")
    print(location_block[:500])
    print("\n" + "="*80 + "\n")
    
    # Split by commas and classify
    location_parts = re.split(r',\s*', location_block)
    print(f"Found {len(location_parts)} location parts:")
    
    for i, part in enumerate(location_parts[:10]):  # First 10
        part = part.strip()
        if not part or len(part) < 2:
            continue
        island = matcher.find_island_group(part)
        print(f"  {i}: '{part[:50]}...' -> {island}")
