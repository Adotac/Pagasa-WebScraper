#!/usr/bin/env python
"""Detailed accuracy analysis script"""

import json
from pathlib import Path
from typhoon_extraction_ml import TyphoonBulletinExtractor
from difflib import SequenceMatcher

ANNOTATIONS_PATH = Path("dataset/pdfs_annotation")
PDFS_PATH = Path("dataset/pdfs")

def get_pdf_path(annotation_filename: str):
    base_name = annotation_filename.replace(".json", "")
    parts = base_name.split("_")
    if len(parts) >= 2:
        year_storm = parts[0] + "_" + parts[1]
        storm_folder = "pagasa-" + year_storm.lower().replace("pagasa_", "")
        pdf_path = PDFS_PATH / storm_folder / (base_name + ".pdf")
        if pdf_path.exists():
            return pdf_path
    return Path()

def analyze_file(annotation_filename):
    pdf_path = get_pdf_path(annotation_filename)
    if not pdf_path.exists():
        return None
    
    # Load ground truth
    with open(ANNOTATIONS_PATH / annotation_filename) as f:
        ground_truth = json.load(f)
    
    # Extract
    extractor = TyphoonBulletinExtractor()
    extracted = extractor.extract_from_pdf(str(pdf_path))
    
    print(f"\n{'='*80}")
    print(f"Analysis: {annotation_filename}")
    print(f"{'='*80}")
    
    # Check simple fields
    simple_fields = ['typhoon_location_text', 'typhoon_movement', 'typhoon_windspeed', 'updated_datetime']
    for field in simple_fields:
        ext_val = str(extracted.get(field, '')).strip()
        gt_val = str(ground_truth.get(field, '')).strip()
        
        if ext_val == gt_val:
            print(f"✓ {field}")
        else:
            similarity = SequenceMatcher(None, ext_val.lower(), gt_val.lower()).ratio()
            print(f"✗ {field} (similarity: {similarity*100:.1f}%)")
            if len(ext_val) < 150 and len(gt_val) < 150:
                print(f"  Extracted: {ext_val}")
                print(f"  Expected : {gt_val}")
    
    # Check nested fields
    for i in range(1, 6):
        for tag_type in ['signal_warning_tags', 'rainfall_warning_tags']:
            if i > 3 and tag_type == 'rainfall_warning_tags':
                continue
            
            field = f"{tag_type}{i}"
            ext_val = extracted.get(field, {})
            gt_val = ground_truth.get(field, {})
            
            matches = 0
            total = 4
            for ig in ['Luzon', 'Visayas', 'Mindanao', 'Other']:
                if ext_val.get(ig) == gt_val.get(ig):
                    matches += 1
            
            ratio = matches / total
            if ratio == 1.0:
                print(f"✓ {field}")
            else:
                print(f"◐ {field} ({matches}/{total} subfields match)")
                for ig in ['Luzon', 'Visayas', 'Mindanao', 'Other']:
                    e = ext_val.get(ig)
                    g = gt_val.get(ig)
                    if e != g:
                        print(f"   {ig}:")
                        print(f"     Extracted: {str(e)[:80]}")
                        print(f"     Expected : {str(g)[:80]}")

if __name__ == "__main__":
    # Test first few files
    for annotation_file in sorted(list(ANNOTATIONS_PATH.glob("*.json")))[:5]:
        analyze_file(annotation_file.name)
