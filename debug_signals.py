#!/usr/bin/env python
"""Debug signal extraction"""

import pdfplumber
import re

pdf_path = 'dataset/pdfs/pagasa-20-19W/PAGASA_20-19W_Pepito_SWB#05.pdf'

with pdfplumber.open(pdf_path) as pdf:
    text = "\n".join([page.extract_text() for page in pdf.pages])

# Check for signal mentions
text_clean = re.sub(r'\s+', ' ', text.lower())

print("Looking for TCWS patterns...")
tcws_matches = re.findall(r'tcws\s+\d', text_clean, re.IGNORECASE)
print(f"Found TCWS matches: {tcws_matches}")

signal_matches = re.findall(r'signal\s+(?:no\.)?\s*(\d)', text_clean, re.IGNORECASE)
print(f"Found Signal matches: {signal_matches}")

# Extract signal section
signal_section = re.search(r'(?:wind|signal|tcws).*?over(.*?)(?:hazard|rainfall|$)', text_clean, re.IGNORECASE | re.DOTALL)
if signal_section:
    print("\nSignal section found:")
    print(signal_section.group(0)[:500])
else:
    print("\nNo signal section found")

# Check locations mentioned
locations = ['batanes', 'babuyan', 'ilocos', 'cagayan', 'quezon', 'albay']
print("\nLocations mentioned:")
for loc in locations:
    if loc in text_clean:
        print(f"  {loc}: YES")
