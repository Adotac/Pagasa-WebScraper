#!/usr/bin/env python
import pdfplumber

pdf_path = 'dataset/pdfs/pagasa-25-TC21/PAGASA_25-TC21_Uwan_TCB#03.pdf'
with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[0]
    text = page.extract_text()

lines = text.split('\n')
for i, line in enumerate(lines):
    if 'TCWS' in line:
        print(f'TCWS at line {i}')
        for j in range(i, min(i+50, len(lines))):
            print(f'{j:3d}: {lines[j][:120]}')  # First 120 chars
        break

