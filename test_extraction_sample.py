#!/usr/bin/env python
"""Test extraction on a few sample PDFs"""

from typhoon_extraction_ml import TyphoonBulletinExtractor
import json
from pathlib import Path

extractor = TyphoonBulletinExtractor()
results = []

# Test on first 5 PDFs from each typhoon
test_pdfs = [
    'dataset/pdfs/pagasa-20-19W/PAGASA_20-19W_Pepito_SWB#01.pdf',
    'dataset/pdfs/pagasa-20-19W/PAGASA_20-19W_Pepito_SWB#02.pdf',
    'dataset/pdfs/pagasa-20-19W/PAGASA_20-19W_Pepito_SWB#05.pdf',
    'dataset/pdfs/pagasa-21-TC01/PAGASA_21-TC01_Aere_SWB#01.pdf',
    'dataset/pdfs/pagasa-22-TC01/PAGASA_22-TC01_Agaton_SWB#01.pdf',
]

for pdf_path in test_pdfs:
    if Path(pdf_path).exists():
        print(f"Extracting {pdf_path}...")
        data = extractor.extract_from_pdf(pdf_path)
        if data:
            data['source_file'] = pdf_path
            results.append(data)
            print(f"  ✓ Extracted successfully")
    else:
        print(f"  ✗ File not found: {pdf_path}")

print(f"\nTotal extracted: {len(results)}")

# Save results
with open('bin/test_extraction_v3.json', 'w') as f:
    json.dump(results, f, indent=2)

print("Results saved to bin/test_extraction_v3.json")

# Print summary of first result
if results:
    print("\n" + "="*80)
    print("SAMPLE OUTPUT:")
    print("="*80)
    sample = results[0]
    print(json.dumps(sample, indent=2))
