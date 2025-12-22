#!/usr/bin/env python
import json
import sys
from typhoon_extraction_ml import TyphoonBulletinExtractor

# Fix encoding on Windows
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

extractor = TyphoonBulletinExtractor()

# Extract from Uwan TCB#03
pdf_path = 'dataset/pdfs/pagasa-25-TC21/PAGASA_25-TC21_Uwan_TCB#03.pdf'
result = extractor.extract_from_pdf(pdf_path)

# Load expected from annotation
annotation_path = 'dataset/pdfs_annotation/PAGASA_25-TC21_Uwan_TCB#03.json'
with open(annotation_path, encoding='utf-8') as f:
    annotation = json.load(f)

# Compare all fields
print("FIELD-BY-FIELD COMPARISON")
print("=" * 100)

# Check basic fields
for field in ['typhoon_location_text', 'typhoon_movement', 'typhoon_windspeed', 'updated_datetime']:
    extracted = result.get(field)
    expected = annotation.get(field)
    match = "PASS" if extracted == expected else "FAIL"
    print(f"{match} {field}")
    if extracted != expected:
        print(f"  Expected: {repr(expected[:80] if isinstance(expected, str) else expected)}...")
        print(f"  Extracted: {repr(extracted[:80] if isinstance(extracted, str) else extracted)}...")

# Check signal warnings
print("\n" + "=" * 100)
print("SIGNAL WARNINGS")
for sig_num in range(1, 6):
    key = f'signal_warning_tags{sig_num}'
    extracted = result.get(key, {})
    expected = annotation.get(key, {})
    
    for col in ['Luzon', 'Visayas', 'Mindanao']:
        e_val = extracted.get(col)
        exp_val = expected.get(col)
        match = "PASS" if e_val == exp_val else "FAIL"
        
        if e_val != exp_val:
            print(f"{match} {key}[{col}]")
            if exp_val:
                print(f"  Expected (first 80): {repr(exp_val[:80])}...")
            if e_val:
                print(f"  Extracted (first 80): {repr(e_val[:80])}...")

