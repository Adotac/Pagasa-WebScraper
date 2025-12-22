#!/usr/bin/env python
"""Extract and display the TCWS signal section in detail"""
import pdfplumber

pdf_path = 'dataset/pdfs/pagasa-25-TC21/PAGASA_25-TC21_Uwan_TCB#03.pdf'

with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[0]
    text = page.extract_text()
    
    # Find the TCWS section
    lines = text.split('\n')
    
    # Find where TCWS starts
    tcws_start = None
    for i, line in enumerate(lines):
        if 'TCWS' in line and 'No' in line:
            tcws_start = i
            break
    
    if tcws_start is not None:
        # Find where TCWS ends (at RAINFALL or POTENTIAL IMPACTS)
        tcws_end = len(lines)
        for i in range(tcws_start + 1, len(lines)):
            if 'RAINFALL' in lines[i].upper() or 'POTENTIAL' in lines[i].upper():
                tcws_end = i
                break
        
        print("TCWS SIGNAL TABLE SECTION")
        print("=" * 120)
        print(f"Lines {tcws_start} to {tcws_end}\n")
        
        for i in range(tcws_start, min(tcws_end, tcws_start + 60)):
            print(f"{i-tcws_start:3d}: {repr(lines[i])}")
    else:
        print("TCWS section not found!")
        print("\nFirst 50 lines of text:")
        for i, line in enumerate(lines[:50]):
            print(f"{i:3d}: {repr(line)}")
