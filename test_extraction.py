#!/usr/bin/env python
"""Quick test of extraction algorithm"""

from typhoon_extraction_ml import LocationMatcher, TyphoonBulletinExtractor
import time
import json

print("Testing LocationMatcher...")
start = time.time()
matcher = LocationMatcher()
print(f"Loaded in {time.time() - start:.2f}s")

result = matcher.find_island_group("Batanes")
print(f"Batanes: {result}")

result = matcher.find_island_group("Cagayan")
print(f"Cagayan: {result}")

print("\nTesting full extraction...")
extractor = TyphoonBulletinExtractor()
data = extractor.extract_from_pdf('dataset/pdfs/pagasa-20-19W/PAGASA_20-19W_Pepito_SWB#05.pdf')

signals = {k: data[k] for k in data if 'signal' in k}
print(json.dumps(signals, indent=2))
