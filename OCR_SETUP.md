# OCR Setup Guide

**NOTE: OCR support has been removed from this project to eliminate heavy dependencies like PyTorch (~500MB).**

The `advisory_scraper.py` script now only works with text-based PDFs (PDFs with extractable text layers).

## What This Means

- ✅ **Text-based PDFs**: Work perfectly (most PAGASA PDFs are text-based)
- ❌ **Scanned/Image PDFs**: Not supported
- ✅ **No heavy dependencies**: Installation is much faster and lighter

## If You Need OCR

If you encounter scanned/image-based PDFs that cannot be extracted, you have a few options:

1. **Convert PDF to text-based format** - Use Adobe Acrobat or similar tools to add a text layer
2. **Use online OCR services** - Upload to services like OCR.space or similar
3. **Install separate OCR tools** - Use dedicated OCR software outside of this project

## How to Check if a PDF is Text-Based

```bash
python advisory_scraper.py "your-file.pdf"
```

If you see:
- ✅ `[INFO] Processing X table(s)` - PDF is text-based and extraction works
- ❌ `[WARNING] PDF is image-based (scanned document) with no extractable text` - PDF cannot be processed

Most PAGASA weather advisory PDFs are text-based and will work without any issues.
