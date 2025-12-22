#!/usr/bin/env python
import pdfplumber
import json

pdf_path = 'dataset/pdfs/pagasa-25-TC21/PAGASA_25-TC21_Uwan_TCB#03.pdf'
with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[0]
    text = page.extract_text()

# Find and print just the TCWS section
lines = text.split('\n')
start_idx = None
end_idx = None

for i, line in enumerate(lines):
    if 'TCWS' in line and ('No.' in line or 'Luzon' in line):
        start_idx = i
    if start_idx is not None and ('RAINFALL' in line.upper() or 'POTENTIAL' in line.upper()):
        end_idx = i
        break

if start_idx is not None:
    if end_idx is None:
        end_idx = min(start_idx + 80, len(lines))
    
    print("RAW TCWS SECTION:")
    print("=" * 100)
    for i in range(start_idx, end_idx):
        print(f"{i:3d}: {repr(lines[i])}")
    
    print("\n\nFORMATTED FOR READING:")
    print("=" * 100)
    for i in range(start_idx, end_idx):
        print(f"{i:3d}: {lines[i]}")
