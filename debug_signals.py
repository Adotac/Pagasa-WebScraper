#!/usr/bin/env python
"""Debug Uwan format signal extraction"""
import pdfplumber
import json
import re

pdf_path = 'dataset/pdfs/pagasa-25-TC21/PAGASA_25-TC21_Uwan_TCB#03.pdf'

with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[0]
    text = page.extract_text()

# Find and extract the signal table section
lines = text.split('\n')

# Find TCWS header
tcws_idx = None
for i, line in enumerate(lines):
    if 'TCWS' in line and ('No.' in line or 'Luzon' in line):
        tcws_idx = i
        break

if tcws_idx is not None:
    print(f"TCWS header found at line {tcws_idx}")
    print("\n=== NEXT 50 LINES FROM TCWS ===\n")
    
    for j in range(tcws_idx, min(tcws_idx + 50, len(lines))):
        print(f"{j:3d}: {lines[j]}")
    
    # Now extract just this section
    print("\n=== SIGNAL SECTION TEXT ===\n")
    section_lines = lines[tcws_idx:min(tcws_idx+50, len(lines))]
    section_text = '\n'.join(section_lines)
    
    # Try to find signal numbers 1-5
    print("\n=== SEARCHING FOR SIGNALS ===\n")
    for sig_num in range(1, 6):
        matches = list(re.finditer(rf'\b{sig_num}\b', section_text))
        print(f"Signal {sig_num}: Found {len(matches)} matches")
        for idx, m in enumerate(matches[:3]):  # Show first 3
            start = max(0, m.start() - 30)
            end = min(len(section_text), m.end() + 50)
            context = section_text[start:end]
            print(f"  Match {idx+1}: ...{repr(context)}...")
