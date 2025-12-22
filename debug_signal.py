import pdfplumber
import re

# Get section
with pdfplumber.open('dataset/pdfs/pagasa-22-TC08/PAGASA_22-TC08_Henry_TCB#04.pdf') as pdf:
    full_text = '\n'.join([page.extract_text() or '' for page in pdf.pages])

from typhoon_extraction_ml import SignalWarningExtractor, LocationMatcher
extractor = SignalWarningExtractor(LocationMatcher())
section = extractor._extract_signal_section(full_text)

lines = section.split('\n')

# Find header
header_idx = -1
for i, line in enumerate(lines):
    if 'tcws no' in line.lower():
        header_idx = i
        break

# Simulate the parser
i = header_idx + 2  # Start at signal line
print(f'Signal line: {repr(lines[i])}')

i += 1  # Move to next line
raw_content = []

# Collect until "Potential impacts"
while i < len(lines):
    next_line = lines[i]
    next_stripped = next_line.strip()
    
    print(f'Line {i}: {repr(next_stripped)}')
    
    # Check end marker
    if 'POTENTIAL IMPACTS' in next_stripped.upper():
        print('  -> FOUND END MARKER')
        break
    
    if next_stripped:
        raw_content.append(next_stripped)
    
    i += 1

print(f'\nRaw content: {raw_content}')

# Join and clean
full_text = ' '.join(raw_content)
print(f'\nJoined: {repr(full_text)}')

# Remove parenthetical
full_text = re.sub(r'\s*\([^)]*\)', '', full_text)
print(f'After removing parens: {repr(full_text)}')

# Clean whitespace
full_text = re.sub(r'\s+', ' ', full_text).strip()
print(f'After whitespace cleanup: {repr(full_text)}')
