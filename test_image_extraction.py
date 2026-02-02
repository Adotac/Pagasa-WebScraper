#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for typhoon image extraction functionality.

Copyright (c) 2026 JMontero
Licensed under the MIT License. See LICENSE file in the project root for details.

This script tests both extraction methods:
1. Extract from HTML
2. Extract from PDF

And both output modes:
1. Stream mode (returns base64)
2. Save mode (saves to file)
"""

import sys
import os
from pathlib import Path
from typhoon_image_extractor import TyphoonImageExtractor


def test_pdf_extraction():
    """Test image extraction from PDF"""
    print("=" * 80)
    print("TEST 1: Extract image from PDF")
    print("=" * 80)
    
    pdf_path = "dataset/pdfs/pagasa-22-TC18/PAGASA_22-TC18_Rosal_TCB#01.pdf"
    
    if not Path(pdf_path).exists():
        print(f"Error: Test PDF not found: {pdf_path}")
        return False
    
    extractor = TyphoonImageExtractor()
    
    # Test stream mode
    print("\nTest 1a: Stream mode (PDF)")
    img_stream = extractor.extract_image_from_pdf(pdf_path)
    
    if img_stream:
        print(f"✓ Success! Image size: {len(img_stream.getvalue())} bytes")
    else:
        print("✗ Failed to extract image")
        return False
    
    # Test save mode
    print("\nTest 1b: Save mode (PDF)")
    save_path = "/tmp/test_pdf_extraction.png"
    result = extractor.extract_image(pdf_path, save_path=save_path)
    
    if result and Path(save_path).exists():
        img_stream, path = result
        print(f"✓ Success! Image saved to: {path}")
        print(f"  Image size: {len(img_stream.getvalue())} bytes")
        # Clean up
        os.remove(save_path)
    else:
        print("✗ Failed to save image")
        return False
    
    return True


def test_html_extraction():
    """Test image extraction from HTML"""
    print("\n" + "=" * 80)
    print("TEST 2: Extract image from HTML")
    print("=" * 80)
    
    html_path = "bin/PAGASA BULLETIN PAGE/PAGASA.html"
    
    if not Path(html_path).exists():
        print(f"Error: Test HTML not found: {html_path}")
        return False
    
    extractor = TyphoonImageExtractor()
    
    # Test stream mode
    print("\nTest 2a: Stream mode (HTML)")
    img_stream = extractor.extract_image_from_html(html_path, tab_index=1)
    
    if img_stream:
        print(f"✓ Success! Image size: {len(img_stream.getvalue())} bytes")
    else:
        print("✗ Failed to extract image")
        return False
    
    # Test save mode
    print("\nTest 2b: Save mode (HTML)")
    save_path = "/tmp/test_html_extraction.png"
    result = extractor.extract_image(html_path, tab_index=1, save_path=save_path)
    
    if result and Path(save_path).exists():
        img_stream, path = result
        print(f"✓ Success! Image saved to: {path}")
        print(f"  Image size: {len(img_stream.getvalue())} bytes")
        # Clean up
        os.remove(save_path)
    else:
        print("✗ Failed to save image")
        return False
    
    return True


def test_analyze_pdf_integration():
    """Test integration with analyze_pdf.py"""
    print("\n" + "=" * 80)
    print("TEST 3: Integration with analyze_pdf.py")
    print("=" * 80)
    
    pdf_path = "dataset/pdfs/pagasa-22-TC18/PAGASA_22-TC18_Rosal_TCB#01.pdf"
    
    if not Path(pdf_path).exists():
        print(f"Error: Test PDF not found: {pdf_path}")
        return False
    
    # Test with --save-image flag
    print("\nTest 3a: analyze_pdf.py with --save-image")
    cmd = f'python analyze_pdf.py "{pdf_path}" --extract-image --save-image --json > /dev/null 2>&1'
    result = os.system(cmd)
    
    # Check if image was created
    saved_images = list(Path.cwd().glob("typhoon_track_*.png"))
    
    if result == 0 and saved_images:
        print(f"✓ Success! Image saved: {saved_images[0].name}")
        # Clean up
        for img in saved_images:
            img.unlink()
    else:
        print("✗ Failed to save image via analyze_pdf.py")
        return False
    
    # Test with --stream flag
    print("\nTest 3b: analyze_pdf.py with --stream")
    cmd = f'python analyze_pdf.py "{pdf_path}" --extract-image --stream --json > /tmp/test_stream_output.json 2>&1'
    result = os.system(cmd)
    
    if result == 0:
        print("✓ Success! Stream mode executed")
        # Clean up
        if Path("/tmp/test_stream_output.json").exists():
            os.remove("/tmp/test_stream_output.json")
    else:
        print("✗ Failed to execute stream mode via analyze_pdf.py")
        return False
    
    return True


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("TYPHOON IMAGE EXTRACTION - TEST SUITE")
    print("=" * 80)
    print()
    
    results = {
        "PDF Extraction": test_pdf_extraction(),
        "HTML Extraction": test_html_extraction(),
        "analyze_pdf.py Integration": test_analyze_pdf_integration()
    }
    
    print("\n" + "=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)
    
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name:40} {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 80)
    if all_passed:
        print("ALL TESTS PASSED ✓")
    else:
        print("SOME TESTS FAILED ✗")
    print("=" * 80)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
