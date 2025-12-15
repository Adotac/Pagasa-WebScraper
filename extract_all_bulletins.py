#!/usr/bin/env python
"""
Comprehensive extraction and validation script for PAGASA typhoon bulletins.
Processes all PDFs and validates the extraction quality.
"""

from typhoon_extraction_ml import TyphoonBulletinExtractor
import json
from pathlib import Path
import time

def extract_all_pdfs():
    """Extract data from all PDFs in the dataset"""
    extractor = TyphoonBulletinExtractor()
    results = []
    errors = []
    
    pdfs_path = Path("dataset/pdfs")
    pdf_files = sorted(list(pdfs_path.rglob("*.pdf")))
    
    print(f"Found {len(pdf_files)} PDF files")
    print("=" * 80)
    
    start_time = time.time()
    
    for i, pdf_file in enumerate(pdf_files, 1):
        try:
            if i % 50 == 0 or i == 1:
                elapsed = time.time() - start_time
                print(f"[{i:4d}/{len(pdf_files)}] Processing... ({elapsed:.1f}s elapsed)")
            
            data = extractor.extract_from_pdf(str(pdf_file))
            if data:
                data['source_file'] = str(pdf_file)
                results.append(data)
        except Exception as e:
            errors.append({'file': str(pdf_file), 'error': str(e)})
            if i % 50 == 0:
                print(f"  ⚠ Error: {str(e)[:60]}")
    
    elapsed = time.time() - start_time
    print(f"\n{'=' * 80}")
    print(f"Extraction Complete!")
    print(f"{'=' * 80}")
    print(f"Total PDFs processed: {len(pdf_files)}")
    print(f"Successfully extracted: {len(results)}")
    print(f"Errors: {len(errors)}")
    print(f"Time elapsed: {elapsed:.1f}s")
    print(f"Average time per PDF: {elapsed/len(pdf_files):.2f}s")
    
    return results, errors


def analyze_extraction_quality(results):
    """Analyze the quality of extraction"""
    stats = {
        'total': len(results),
        'with_datetime': 0,
        'with_location': 0,
        'with_movement': 0,
        'with_windspeed': 0,
        'with_signals': 0,
        'with_rainfall': 0,
        'signal_coverage': {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0},
        'rainfall_coverage': {'1': 0, '2': 0, '3': 0},
    }
    
    for result in results:
        # Check for extracted fields
        if result.get('updated_datetime'):
            stats['with_datetime'] += 1
        
        if result.get('typhoon_location_text') and result['typhoon_location_text'] != "Location not found":
            stats['with_location'] += 1
        
        if result.get('typhoon_movement') and result['typhoon_movement'] != "Movement information not found":
            stats['with_movement'] += 1
        
        if result.get('typhoon_windspeed') and result['typhoon_windspeed'] != "Wind speed not found":
            stats['with_windspeed'] += 1
        
        # Check for signals
        for signal_num in range(1, 6):
            tag_key = f'signal_warning_tags{signal_num}'
            tag = result.get(tag_key, {})
            has_signal = any(tag.get(ig) for ig in ['Luzon', 'Visayas', 'Mindanao', 'Other'])
            if has_signal:
                stats['with_signals'] += 1
                stats['signal_coverage'][str(signal_num)] += 1
        
        # Check for rainfall
        for level in range(1, 4):
            tag_key = f'rainfall_warning_tags{level}'
            tag = result.get(tag_key, {})
            has_rainfall = any(tag.get(ig) for ig in ['Luzon', 'Visayas', 'Mindanao', 'Other'])
            if has_rainfall:
                stats['with_rainfall'] += 1
                stats['rainfall_coverage'][str(level)] += 1
    
    return stats


def main():
    print("PAGASA Typhoon Bulletin Extraction System")
    print("=" * 80)
    
    # Extract all PDFs
    results, errors = extract_all_pdfs()
    
    # Analyze quality
    print("\nAnalyzing extraction quality...")
    stats = analyze_extraction_quality(results)
    
    print(f"\n{'=' * 80}")
    print("EXTRACTION QUALITY REPORT")
    print(f"{'=' * 80}")
    print(f"Total bulletins: {stats['total']}")
    print(f"\nField Extraction Coverage:")
    print(f"  - Datetime:       {stats['with_datetime']:5d} ({stats['with_datetime']*100//stats['total']:3d}%)")
    print(f"  - Location:       {stats['with_location']:5d} ({stats['with_location']*100//stats['total']:3d}%)")
    print(f"  - Movement:       {stats['with_movement']:5d} ({stats['with_movement']*100//stats['total']:3d}%)")
    print(f"  - Wind Speed:     {stats['with_windspeed']:5d} ({stats['with_windspeed']*100//stats['total']:3d}%)")
    print(f"\nWarning Extraction:")
    print(f"  - With Signals:   {stats['with_signals']:5d} ({stats['with_signals']*100//stats['total']:3d}%)")
    print(f"    - Signal 1:     {stats['signal_coverage']['1']:5d}")
    print(f"    - Signal 2:     {stats['signal_coverage']['2']:5d}")
    print(f"    - Signal 3:     {stats['signal_coverage']['3']:5d}")
    print(f"    - Signal 4:     {stats['signal_coverage']['4']:5d}")
    print(f"    - Signal 5:     {stats['signal_coverage']['5']:5d}")
    print(f"  - With Rainfall:  {stats['with_rainfall']:5d} ({stats['with_rainfall']*100//stats['total']:3d}%)")
    print(f"    - Level 1:      {stats['rainfall_coverage']['1']:5d}")
    print(f"    - Level 2:      {stats['rainfall_coverage']['2']:5d}")
    print(f"    - Level 3:      {stats['rainfall_coverage']['3']:5d}")
    
    # Save results
    output_file = "bin/extracted_typhoon_data_final.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n✓ Results saved to: {output_file}")
    
    # Save stats
    stats_file = "bin/extraction_stats.json"
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"✓ Statistics saved to: {stats_file}")
    
    if errors:
        errors_file = "bin/extraction_errors.json"
        with open(errors_file, 'w') as f:
            json.dump(errors, f, indent=2)
        print(f"⚠ Errors saved to: {errors_file}")


if __name__ == "__main__":
    main()
