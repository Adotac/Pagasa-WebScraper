#!/usr/bin/env python
"""
Integration test demonstrating the complete typhoon image extraction workflow.

This example shows:
1. Extracting data from PDF
2. Extracting image in both modes
3. Using the extracted data and image together
"""

import json
import base64
from pathlib import Path
from typhoon_extraction import TyphoonBulletinExtractor
from typhoon_image_extractor import TyphoonImageExtractor


def example_1_extract_and_save():
    """Example 1: Extract data and image, save image to file"""
    print("=" * 80)
    print("EXAMPLE 1: Extract data and save image to file")
    print("=" * 80)
    
    # Sample PDF path
    pdf_path = "dataset/pdfs/pagasa-22-TC18/PAGASA_22-TC18_Rosal_TCB#01.pdf"
    
    if not Path(pdf_path).exists():
        print(f"Error: PDF not found: {pdf_path}")
        return
    
    # Step 1: Extract typhoon data
    print("\nStep 1: Extracting typhoon data...")
    extractor = TyphoonBulletinExtractor()
    data = extractor.extract_from_pdf(pdf_path)
    
    if data:
        print(f"✓ Typhoon: {data.get('typhoon_name')}")
        print(f"  Location: {data.get('typhoon_location_text', 'N/A')[:50]}...")
        print(f"  Wind Speed: {data.get('typhoon_windspeed', 'N/A')[:50]}...")
    else:
        print("✗ Failed to extract data")
        return
    
    # Step 2: Extract and save image
    print("\nStep 2: Extracting typhoon track image...")
    img_extractor = TyphoonImageExtractor()
    
    # Generate filename
    typhoon_name = data.get('typhoon_name', 'unknown').replace(' ', '_')
    img_filename = f"example_{typhoon_name}_track.png"
    
    result = img_extractor.extract_image(pdf_path, save_path=img_filename)
    
    if result:
        img_stream, img_path = result
        print(f"✓ Image saved to: {img_path}")
        print(f"  Image size: {len(img_stream.getvalue())} bytes")
        
        # Step 3: Create combined output
        output = {
            'typhoon_data': data,
            'image_path': img_path
        }
        
        print("\nStep 3: Creating combined JSON output...")
        print(json.dumps(output, indent=2)[:500] + "...")
        
        # Clean up
        Path(img_path).unlink()
        print("\n✓ Example completed successfully!")
    else:
        print("✗ Failed to extract image")


def example_2_stream_mode():
    """Example 2: Extract data and image as stream (no file saving)"""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Extract data and image as stream (no file saving)")
    print("=" * 80)
    
    # Sample PDF path
    pdf_path = "dataset/pdfs/pagasa-22-TC18/PAGASA_22-TC18_Rosal_TCB#01.pdf"
    
    if not Path(pdf_path).exists():
        print(f"Error: PDF not found: {pdf_path}")
        return
    
    # Step 1: Extract typhoon data
    print("\nStep 1: Extracting typhoon data...")
    extractor = TyphoonBulletinExtractor()
    data = extractor.extract_from_pdf(pdf_path)
    
    if not data:
        print("✗ Failed to extract data")
        return
    
    print(f"✓ Data extracted for: {data.get('typhoon_name')}")
    
    # Step 2: Extract image as stream
    print("\nStep 2: Extracting image as stream (no file saving)...")
    img_extractor = TyphoonImageExtractor()
    img_stream = img_extractor.extract_image(pdf_path)
    
    if img_stream:
        print(f"✓ Image extracted to memory")
        print(f"  Image size: {len(img_stream.getvalue())} bytes")
        
        # Step 3: Convert to base64 for API/JSON output
        print("\nStep 3: Converting image to base64...")
        img_base64 = base64.b64encode(img_stream.getvalue()).decode('utf-8')
        
        # Create API-ready output
        api_output = {
            'typhoon_data': data,
            'image_base64': img_base64[:100] + "..."  # Truncated for display
        }
        
        print("\nAPI-ready output structure:")
        print(json.dumps(api_output, indent=2)[:800] + "...")
        
        print("\n✓ Example completed successfully!")
        print("  Note: Image was never written to disk - kept in memory only")
    else:
        print("✗ Failed to extract image")


def example_3_html_extraction():
    """Example 3: Extract image from HTML source"""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Extract image from HTML source")
    print("=" * 80)
    
    # HTML path
    html_path = "bin/PAGASA BULLETIN PAGE/PAGASA.html"
    
    if not Path(html_path).exists():
        print(f"Error: HTML not found: {html_path}")
        return
    
    # Extract image from HTML
    print("\nExtracting image from HTML (higher quality)...")
    img_extractor = TyphoonImageExtractor()
    img_stream = img_extractor.extract_image_from_html(html_path, tab_index=1)
    
    if img_stream:
        print(f"✓ Image extracted from HTML")
        print(f"  Image size: {len(img_stream.getvalue())} bytes")
        print(f"  Note: HTML extraction typically provides higher resolution images")
        
        # Compare with PDF extraction
        print("\nFor comparison, extracting from PDF...")
        pdf_path = "dataset/pdfs/pagasa-22-TC18/PAGASA_22-TC18_Rosal_TCB#01.pdf"
        if Path(pdf_path).exists():
            pdf_img_stream = img_extractor.extract_image_from_pdf(pdf_path)
            if pdf_img_stream:
                print(f"  PDF image size: {len(pdf_img_stream.getvalue())} bytes")
                
                ratio = len(img_stream.getvalue()) / len(pdf_img_stream.getvalue())
                print(f"  HTML/PDF size ratio: {ratio:.1f}x")
        
        print("\n✓ Example completed successfully!")
    else:
        print("✗ Failed to extract image from HTML")


def example_4_batch_processing():
    """Example 4: Batch processing multiple PDFs with image extraction"""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Batch processing with image extraction")
    print("=" * 80)
    
    # Find sample PDFs
    pdf_dir = Path("dataset/pdfs/pagasa-22-TC18")
    
    if not pdf_dir.exists():
        print(f"Error: Directory not found: {pdf_dir}")
        return
    
    pdf_files = list(pdf_dir.glob("*.pdf"))[:3]  # Process first 3 PDFs
    
    if not pdf_files:
        print("No PDF files found")
        return
    
    print(f"\nProcessing {len(pdf_files)} bulletins...")
    
    extractor = TyphoonBulletinExtractor()
    img_extractor = TyphoonImageExtractor()
    
    results = []
    
    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"\n[{i}/{len(pdf_files)}] Processing: {pdf_path.name}")
        
        # Extract data
        data = extractor.extract_from_pdf(str(pdf_path))
        
        if not data:
            print("  ✗ Failed to extract data")
            continue
        
        # Extract image (stream mode - no file saving)
        img_stream = img_extractor.extract_image(str(pdf_path))
        
        if img_stream:
            img_base64 = base64.b64encode(img_stream.getvalue()).decode('utf-8')
            
            result = {
                'bulletin_number': i,
                'typhoon_name': data.get('typhoon_name'),
                'updated_datetime': data.get('updated_datetime'),
                'image_size': len(img_stream.getvalue()),
                'has_image': True
            }
            
            results.append(result)
            print(f"  ✓ Extracted: {data.get('typhoon_name')}")
            print(f"    Image size: {len(img_stream.getvalue())} bytes")
        else:
            print("  ✗ Failed to extract image")
    
    print(f"\n{'=' * 80}")
    print(f"BATCH PROCESSING SUMMARY")
    print(f"{'=' * 80}")
    print(f"Total bulletins processed: {len(results)}")
    print(f"Successfully extracted: {len([r for r in results if r['has_image']])} images")
    
    print("\n✓ Example completed successfully!")


def main():
    """Run all examples"""
    print("\n" + "=" * 80)
    print("TYPHOON IMAGE EXTRACTION - INTEGRATION EXAMPLES")
    print("=" * 80)
    print()
    
    try:
        example_1_extract_and_save()
        example_2_stream_mode()
        example_3_html_extraction()
        example_4_batch_processing()
        
        print("\n" + "=" * 80)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY ✓")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
