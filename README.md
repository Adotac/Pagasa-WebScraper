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


## Last terminal command
The terminal ran: powershell .venv\Scripts\Activate.ps1 (working directory: C:\_Files\Code_Files\Pagasa WebScraper)
