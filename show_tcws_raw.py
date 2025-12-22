#!/usr/bin/env python
import pdfplumber
import re

pdf_path = 'dataset/pdfs/pagasa-25-TC21/PAGASA_25-TC21_Uwan_TCB#03.pdf'
with pdfplumber.open(pdf_path) as pdf:
    full_text = "\n".join([page.extract_text() or "" for page in pdf.pages])

# Find the TCWS section
idx = full_text.find('TROPICAL CYCLONE WIND SIGNALS')
if idx >= 0:
    # Extract from TCWS until next major section
    end_idx = full_text.find('HAZARDS AFFECTING', idx)
    if end_idx < 0:
        end_idx = full_text.find('Heavy Rainfall', idx)
    if end_idx < 0:
        end_idx = idx + 3000
    
    tcws_section = full_text[idx:end_idx]
    print("TCWS SECTION (raw):")
    print("="*100)
    print(tcws_section)
    print("\n" + "="*100)
    
    # Now find signals
    # Look for lines that contain just a number 1-5
    lines = tcws_section.split('\n')
    print(f"\nTotal lines: {len(lines)}")
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped in ['1', '2', '3', '4', '5']:
            print(f"Found signal {stripped} at line {i}")
            # Show context
            start = max(0, i - 2)
            end = min(len(lines), i + 8)
            for j in range(start, end):
                prefix = ">>> " if j == i else "    "
                print(f"{prefix}{j}: {lines[j][:100]}")
