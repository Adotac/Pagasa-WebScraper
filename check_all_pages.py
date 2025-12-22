#!/usr/bin/env python
import pdfplumber

pdf_path = 'dataset/pdfs/pagasa-25-TC21/PAGASA_25-TC21_Uwan_TCB#03.pdf'
with pdfplumber.open(pdf_path) as pdf:
    print(f"Total pages: {len(pdf.pages)}")
    
    for page_idx in range(len(pdf.pages)):
        page = pdf.pages[page_idx]
        text = page.extract_text()
        
        # Check if this page has signal info
        if any(kw in text for kw in ['TCWS', 'TROPICAL CYCLONE WIND', 'Signal', 'Catanduanes', 'Cagayan']):
            print(f"\nPage {page_idx}: Has signal info, length={len(text)}")
            if 'TCWS' in text:
                idx = text.find('TCWS')
                print(f"  TCWS found at {idx}")
            if 'Catanduanes' in text:
                idx = text.find('Catanduanes')
                print(f"  Catanduanes found at {idx}")
            
            # Show first 1000 chars
            print(f"  First 1000 chars:\n{text[:1000]}")
        else:
            print(f"\nPage {page_idx}: No signal info, length={len(text)}")
