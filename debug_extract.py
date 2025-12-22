#!/usr/bin/env python
import json
from typhoon_extraction_ml import TyphoonBulletinExtractor

extractor = TyphoonBulletinExtractor()

# Extract from Uwan TCB#03
pdf_path = 'dataset/pdfs/pagasa-25-TC21/PAGASA_25-TC21_Uwan_TCB#03.pdf'
result = extractor.extract_from_pdf(pdf_path)

# Print signal tags
print("Extracted signal tags:")
for sig_num in [1, 2, 3, 4, 5]:
    key = f'signal_warning_tags{sig_num}'
    if key in result:
        print(f"\n{key}:")
        print(json.dumps(result[key], indent=2))

# Also print expected from annotation
print("\n" + "="*80)
print("Expected signal tags:")
annotation_path = 'dataset/pdfs_annotation/PAGASA_25-TC21_Uwan_TCB#03.json'
with open(annotation_path) as f:
    annotation = json.load(f)

for sig_num in [1, 2, 3, 4, 5]:
    key = f'signal_warning_tags{sig_num}'
    if key in annotation:
        print(f"\n{key}:")
        print(json.dumps(annotation[key], indent=2))
