# OCR Setup Guide

This guide explains how to install OCR support for processing image-based/scanned PDFs with the advisory scraper.

## Two OCR Options

The script supports **two OCR methods**:

### Option 1: EasyOCR (Recommended for No Admin Rights) ✅

**Pure Python library - no system installation needed!**

```bash
# Quick install (Python 3.8.10 compatible)
pip install -r requirements-ocr-easyocr.txt

# OR install manually:
# pip install easyocr pdf2image
```

**Pros:**
- ✅ No system-level installation required
- ✅ Works without admin/sudo permissions
- ✅ Easy to install on any platform
- ✅ Good accuracy

**Cons:**
- ⚠️ Slower than Tesseract (first run downloads model ~100MB)
- ⚠️ Uses more memory

**Best for:** Users without admin rights, Windows users, quick setup

---

### Option 2: Tesseract (Faster, Requires System Package)

```bash
# Step 1: Install Python library
pip install pytesseract pdf2image

# OR install from requirements file (Python 3.8.10 compatible)
pip install -r requirements-ocr-tesseract.txt

# Step 2: Install system package (requires admin/sudo)
# See platform-specific instructions below
```

**Pros:**
- ✅ Faster processing
- ✅ Lower memory usage
- ✅ Mature, well-tested

**Cons:**
- ⚠️ Requires system-level installation
- ⚠️ Needs admin/sudo permissions

**Best for:** Users with admin rights, production environments

---

## Installation Instructions

### Option 1: EasyOCR (No System Install)

```bash
# Install Python dependencies (Python 3.8.10 compatible)
pip install -r requirements-ocr-easyocr.txt

# OR install manually:
# pip install easyocr pdf2image

# That's it! No system package needed.
```

**Verify installation:**
```bash
python -c "import easyocr; print('EasyOCR: OK')"
python -c "from pdf2image import convert_from_path; print('pdf2image: OK')"
```

---

### Option 2: Tesseract (With System Package)

#### Step 1: Install Python Dependencies

```bash
pip install pytesseract pdf2image
```

#### Step 2: Install Tesseract OCR Engine (System Package)

##### Ubuntu/Debian/WSL
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

##### macOS
```bash
brew install tesseract
```

##### Windows
1. Download the installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer
3. Add Tesseract to your system PATH

#### Step 3: Verify Installation

Test that OCR is working:

```bash
python -c "import pytesseract; print('pytesseract:', pytesseract.__version__)"
python -c "from pdf2image import convert_from_path; print('pdf2image: OK')"
tesseract --version
```

## Usage

Once installed, the advisory scraper will automatically use OCR when it detects image-based PDFs:

```bash
# Auto-detects and uses OCR if needed
python advisory_scraper.py "scanned-document.pdf"

# Force OCR mode
python advisory_scraper.py --ocr "document.pdf"
```

## Troubleshooting

### "tesseract is not installed" error
- Make sure you installed the **system package** (step 2 above), not just the Python library
- Verify installation: `tesseract --version`

### "Unable to get page count" error (Windows)
- Install poppler for Windows: https://github.com/oschwartz10612/poppler-windows/releases
- Add poppler's bin directory to your system PATH

### "No such file or directory: 'tesseract'" error (macOS)
- Ensure tesseract is installed: `brew install tesseract`
- Check PATH: `which tesseract`

## Optional: OCR is Not Required

The advisory scraper works fine without OCR for regular text-based PDFs. OCR is only needed for:
- Scanned documents
- Image-based PDFs
- PDFs without a text layer

If you don't need OCR support, you can skip this installation and the script will work normally for text-based PDFs.
