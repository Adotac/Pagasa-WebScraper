#!/usr/bin/env python
"""Debug specific test cases to understand what's missing"""

import json
from pathlib import Path
from typhoon_extraction_ml import TyphoonBulletinExtractor
import difflib

DATASET_PATH = Path("dataset")
ANNOTATIONS_PATH = DATASET_PATH / "pdfs_annotation"
PDFS_PATH = DATASET_PATH / "pdfs"

extractor = TyphoonBulletinExtractor()

# Test a TCB case that's not 100%
annotation_file = ANNOTATIONS_PATH / "PAGASA_22-TC08_Henry_TCB#05.json"

with open(annotation_file) as f:
    expected = json.load(f)

# Map annotation to PDF
base_name = str(annotation_file.stem)
year_storm = "_".join(base_name.split("_")[:2])
storm_folder = "pagasa-" + year_storm.lower().replace("pagasa_", "")
pdf_path = PDFS_PATH / storm_folder / (base_name + ".pdf")

got = extractor.extract_from_pdf(str(pdf_path))

print(f"Test: {annotation_file.name}")
print(f"PDF: {pdf_path}")
print(f"Accuracy: {expected.get('accuracy_info', {})}")
print()

# Find mismatches
print("=" * 60)
print("CHECKING FIELDS")
print("=" * 60)

all_fields = set(expected.keys()) | set(got.keys() if got else {})

for field in sorted(all_fields):
    exp_val = expected.get(field, 'MISSING')
    got_val = got.get(field, 'MISSING') if got else 'PDF_ERROR'
    
    # Skip metadata fields
    if field in ['accuracy_info', 'metadata']:
        continue
    
    match = exp_val == got_val
    
    if not match:
        print()
        print(f"Field: {field}")
        print(f"  Expected: {repr(exp_val)[:150]}")
        print(f"  Got:      {repr(got_val)[:150]}")
        
        # Show detailed comparison for signal/rainfall tags
        if 'tags' in field:
            print("  Details:")
            if isinstance(exp_val, dict) and isinstance(got_val, dict):
                for region in ['Luzon', 'Visayas', 'Mindanao', 'Other']:
                    exp_region = exp_val.get(region)
                    got_region = got_val.get(region) if got_val else None
                    if exp_region != got_region:
                        print(f"    {region}:")
                        print(f"      Expected: {repr(exp_region)[:100]}")
                        print(f"      Got:      {repr(got_region)[:100]}")
