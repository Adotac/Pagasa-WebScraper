#!/usr/bin/env python
import pdfplumber

pdf_path = 'dataset/pdfs/pagasa-25-TC21/PAGASA_25-TC21_Uwan_TCB#03.pdf'
with pdfplumber.open(pdf_path) as pdf:
    full_text = "\n".join([page.extract_text() or "" for page in pdf.pages])

print(f"Full text length: {len(full_text)}")

# Check if TCWS is in full text
if 'TROPICAL CYCLONE WIND SIGNALS' in full_text:
    idx = full_text.find('TROPICAL CYCLONE WIND SIGNALS')
    print(f"TCWS found at position {idx}")
    print(f"Context:\n{full_text[idx:idx+500]}")
else:
    print("TCWS NOT FOUND")

# Check if Catanduanes is in full text
if 'Catanduanes' in full_text:
    print(f"Catanduanes found {full_text.count('Catanduanes')} times")
else:
    print("Catanduanes NOT FOUND")
