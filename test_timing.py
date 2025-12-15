#!/usr/bin/env python
"""Quick timing test"""

import time
from typhoon_extraction_ml import TyphoonBulletinExtractor

print("Initializing extractor...")
start = time.time()
extractor = TyphoonBulletinExtractor()
init_time = time.time() - start
print(f"  Done in {init_time:.2f}s")

pdf_path = 'dataset/pdfs/pagasa-20-19W/PAGASA_20-19W_Pepito_SWB#01.pdf'
print(f"\nExtracting {pdf_path}...")
start = time.time()
data = extractor.extract_from_pdf(pdf_path)
extract_time = time.time() - start
print(f"  Done in {extract_time:.2f}s")

print(f"\nTotal time: {init_time + extract_time:.2f}s")
