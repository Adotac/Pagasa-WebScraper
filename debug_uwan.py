#!/usr/bin/env python
"""Check Uwan TCB#04 extraction"""

import json
from pathlib import Path
from typhoon_extraction_ml import TyphoonBulletinExtractor

annotation_file = 'dataset/pdfs_annotation/PAGASA_25-TC21_Uwan_TCB#04.json'
with open(annotation_file) as f:
    expected = json.load(f)

# Map annotation to PDF correctly
base_name = Path(annotation_file).stem
parts = base_name.split('_')
year_storm = parts[0] + '_' + parts[1]
storm_folder = 'pagasa-' + year_storm.lower().replace('pagasa_', '')
pdf_path = Path('dataset/pdfs') / storm_folder / (base_name + '.pdf')

extractor = TyphoonBulletinExtractor()
got = extractor.extract_from_pdf(str(pdf_path))

print('Test: PAGASA_25-TC21_Uwan_TCB#04.json')

# Check signals
print('\nSignal Tags:')
for level in [1, 2]:
    exp = expected.get(f'signal_warning_tags{level}', {})
    g = got.get(f'signal_warning_tags{level}', {}) if got else {}
    
    if exp.get('Luzon'):
        match = exp.get('Luzon') == g.get('Luzon')
        print(f'  Tags{level} Luzon: match={match}')
        if not match:
            print(f'    Expected: {repr(exp.get("Luzon")[:50])}...')
            print(f'    Got:      {repr(g.get("Luzon", "None")[:50] if g.get("Luzon") else "None")}')
