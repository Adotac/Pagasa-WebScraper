#!/usr/bin/env python
import pdfplumber
import re
from typhoon_extraction_ml import SignalWarningExtractor, LocationMatcher

matcher = LocationMatcher()
sig_extractor = SignalWarningExtractor(matcher)

pdf_path = 'dataset/pdfs/pagasa-25-TC21/PAGASA_25-TC21_Uwan_TCB#03.pdf'
with pdfplumber.open(pdf_path) as pdf:
    full_text = "\n".join([page.extract_text() or "" for page in pdf.pages])

# Extract signal section
signal_section = sig_extractor._extract_signal_section(full_text)
if not signal_section:
    print("Failed to extract signal section!")
    exit(1)

lines = signal_section.split('\n')
full_text_sig = '\n'.join(lines)

# Find all signal numbers
signal_matches = []
for sig_num in range(1, 6):
    pattern = rf'\n{sig_num}\n|\b{sig_num}\b'
    for match in re.finditer(pattern, full_text_sig):
        signal_matches.append((match.start(), sig_num, match))

# Sort by position
signal_matches.sort(key=lambda x: x[0])

print(f"Found {len(signal_matches)} signal instances in order:")
for pos, sig_num, _ in signal_matches:
    context = full_text_sig[max(0, pos-20):pos+50]
    print(f"  Signal {sig_num} at pos {pos}: ...{repr(context)}...")

# Extract and show signal 1 block
print("\n" + "="*100)
print("SIGNAL 1 EXTRACTION:")

for idx, (pos, sig_num, match) in enumerate(signal_matches):
    if sig_num != 1:
        continue
    
    sig_start = match.end()
    
    # Find end
    if idx + 1 < len(signal_matches):
        sig_end = signal_matches[idx + 1][0]
    else:
        sig_end = len(full_text_sig)
    
    signal_block = full_text_sig[sig_start:sig_end].strip()
    
    print(f"Raw block (first 300 chars):\n{signal_block[:300]}\n")
    
    # Clean it
    block_lines = signal_block.split('\n')
    clean_lines = []
    
    for line in block_lines:
        stripped = line.strip()
        if not stripped:
            continue
        if any(marker in stripped.lower() for marker in 
               ['wind threat:', 'gale-forc', 'strong winds', 'prevailing winds',
                'warning lead time:', 'range of wind speeds:', 'potential impacts',
                'minor to moderate', 'minor threat', 'moderate threat', 'property',
                'page', 'prepared by', 'weather', 'pagasa', 'bulletin']):
            continue
        if stripped in ['-', '--', '- -']:
            continue
        clean_lines.append(stripped)
    
    location_text = ' '.join(clean_lines)
    location_text = location_text.replace(' and ', ', ').strip()
    
    print(f"Cleaned text (first 300 chars):\n{location_text[:300]}\n")
    
    # Split by commas
    location_parts = re.split(r',\s*', location_text)
    print(f"Found {len(location_parts)} location parts:")
    
    for i, part in enumerate(location_parts[:15]):  # First 15
        part = part.strip()
        if not part or len(part) < 2:
            continue
        island = matcher.find_island_group(part)
        print(f"  {i}: '{part[:40]}...' -> {island}")
