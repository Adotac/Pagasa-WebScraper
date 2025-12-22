#!/usr/bin/env python
"""Extract TCWS table structure using pdfplumber's table detection"""
import pdfplumber
import json

pdf_path = 'dataset/pdfs/pagasa-25-TC21/PAGASA_25-TC21_Uwan_TCB#03.pdf'

with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[0]
    
    # Try to extract tables from the page
    tables = page.extract_tables()
    
    print(f"Found {len(tables)} tables on the page\n")
    
    # Show all tables
    for table_idx, table in enumerate(tables):
        print(f"\n{'='*100}")
        print(f"TABLE {table_idx}")
        print(f"{'='*100}\n")
        print(f"Dimensions: {len(table)} rows x {len(table[0]) if table else 0} cols\n")
        
        # Print table as-is
        for row_idx, row in enumerate(table):
            print(f"Row {row_idx}: ", end='')
            for col_idx, cell in enumerate(row):
                if cell:
                    # Truncate long cells for readability
                    cell_str = str(cell).replace('\n', '|')
                    if len(cell_str) > 80:
                        print(f"[{cell_str[:80]}...]", end=' ')
                    else:
                        print(f"[{cell_str}]", end=' ')
                else:
                    print("[None]", end=' ')
            print()
