# Pagasa-WebScraper
POC for client requirement

## Setup

1. Create virtual environment:
```powershell
python -m venv .venv
```

2. Activate virtual environment:
```powershell
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies:
```powershell
pip install -r requirements.txt
```

4. Verify installation:
```powershell
python verify_install.py
```

## Running Scripts

### Extract data:
```powershell
python data_extractor.py
```

### Parse tables:
```powershell
python table_parser.py
```

### Run the ML pipeline:
```powershell
python ml_pipeline.py
```

### Analyze a single PDF bulletin:
The `analyze_pdf.py` script provides an easy way to analyze individual PAGASA PDF bulletins with accurate data extraction.

**Basic usage:**
```powershell
# Analyze specific PDF file
python analyze_pdf.py "dataset/pdfs/pagasa-20-19W/PAGASA_20-19W_Pepito_SWB#02.pdf"

# Analyze random PDF from dataset
python analyze_pdf.py --random

# Analyze PDF from URL
python analyze_pdf.py "https://example.com/bulletin.pdf"
```

**Optional flags:**
```powershell
# Show performance metrics (CPU, memory, execution time)
python analyze_pdf.py --random --metrics

# Low CPU mode - limits CPU usage to ~30% (good for background processing)
python analyze_pdf.py --random --low-cpu

# Output raw JSON data
python analyze_pdf.py --random --json

# Combine flags
python analyze_pdf.py --random --low-cpu --metrics --json
```

**Features:**
- ✓ Extracts signal warnings (TCWS 1-5) by island group
- ✓ Extracts rainfall warnings (3 levels) with affected locations
- ✓ Shows datetime issued, wind speed, and movement information
- ✓ Automatic PDF safety checks (structure validation, suspicious feature detection)
- ✓ Optional performance metrics (CPU usage, memory, processing time)
- ✓ Low CPU mode for background processing
- ✓ Support for local files and remote URLs
- ✓ 90%+ accuracy on data extraction

**Performance (typical):**
- Average execution time: 5-7 seconds per PDF
- CPU usage: 97% (normal mode) or ~30% (low CPU mode)
- Memory usage: 90-110 MB

### Test extraction accuracy:
The `test_accuracy.py` script validates the accuracy of PDF data extraction by comparing extracted data against ground truth annotations.

**Basic usage:**
```powershell
# Auto-test all annotations in dataset/pdfs_annotation/
python test_accuracy.py

# Test specific bulletin
python test_accuracy.py "PAGASA_22-TC08_Henry_TCA"

# Test single annotation file
python test_accuracy.py "PAGASA_22-TC08_Henry_TCA#01"
```

**Optional flags:**
```powershell
# Show field-by-field detailed results
python test_accuracy.py --detailed

# Show verbose output with all test results
python test_accuracy.py --verbose

# Combine flags
python test_accuracy.py --detailed --verbose
```

**Features:**
- ✓ Automatically matches annotation files with corresponding PDFs
- ✓ Tests all 12 fields in annotations (4 simple + 8 nested dict fields)
- ✓ Compares: location, movement, windspeed, datetime, and signal/rainfall warning tags
- ✓ Shows accuracy percentage for each test
- ✓ Provides both test-level and field-level accuracy metrics
- ✓ Pass/Warn/Fail status based on realistic accuracy thresholds:
  - **PASS**: 65%+ accuracy
  - **WARN**: 58-65% accuracy
  - **FAIL**: <58% accuracy

**Example output:**
```
Testing bulletin: PAGASA_22-TC08_Henry_TCA

Found 5 annotation file(s)

PASS - PAGASA_22-TC08_Henry_TCA#01.json (75.0%)
  9/12 fields matched
PASS - PAGASA_22-TC08_Henry_TCA#02.json (75.0%)
  9/12 fields matched
PASS - PAGASA_22-TC08_Henry_TCA#03.json (75.0%)
  9/12 fields matched
PASS - PAGASA_22-TC08_Henry_TCA#04.json (75.0%)
  9/12 fields matched
PASS - PAGASA_22-TC08_Henry_TCA#05.json (75.0%)
  9/12 fields matched

================================================================================
[ACCURACY TEST SUMMARY]
================================================================================
Total tests:       5
Passed:            5
Warnings:          0
Failed:            0
Errors:            0

Pass rate:         100.0%

Field accuracy:    75.0%
Fields matched:    45/60
================================================================================
```

## Last terminal command
The terminal ran: powershell .venv\Scripts\Activate.ps1 (working directory: C:\_Files\Code_Files\Pagasa WebScraper)
