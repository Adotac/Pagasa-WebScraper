#!/usr/bin/env python
import pdfplumber

pdf_path = 'dataset/pdfs/pagasa-25-TC21/PAGASA_25-TC21_Uwan_TCB#03.pdf'
with pdfplumber.open(pdf_path) as pdf:
    text = pdf.pages[0].extract_text()

# Find what keywords are actually in the text
keywords = ['TCWS', 'Wind', 'Signal', 'Luzon', 'Visayas', 'Mindanao', 'Catanduanes', 'Cagayan']

for kw in keywords:
    if kw in text:
        idx = text.find(kw)
        print(f"{kw}: Found at position {idx}")
        # Show context
        start = max(0, idx - 50)
        end = min(len(text), idx + 100)
        print(f"  Context: ...{repr(text[start:end])}...")
    else:
        print(f"{kw}: NOT FOUND")

print(f"\nTotal text length: {len(text)}")
print(f"\nFirst 500 chars:\n{text[:500]}")
