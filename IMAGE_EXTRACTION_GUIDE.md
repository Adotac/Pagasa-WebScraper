# Typhoon Image Extraction Feature

## Overview

The typhoon image extraction feature allows you to extract typhoon track images from PAGASA bulletin PDFs or HTML pages. The feature supports two extraction methods and two output modes.

## Extraction Methods

### Method 1: HTML/URL Extraction
Extracts the typhoon track image directly from the PAGASA bulletin HTML page by locating the image within the `tcwb-{number}` tab element.

**Advantages:**
- Higher quality image (original resolution)
- Faster extraction
- Works with both live URLs and local HTML files

**Use when:**
- Processing from HTML source
- Need high-quality track images
- Source is PAGASA bulletin page

### Method 2: PDF Extraction (Fallback)
Extracts the typhoon track image from the PDF bulletin by identifying the largest image on the right side of the first page.

**Advantages:**
- Works when only PDF is available
- No need for HTML source
- Reliable for standard PAGASA bulletin format

**Use when:**
- Processing from PDF source
- HTML source not available
- Processing archived PDFs

## Output Modes

### Stream Mode (`--stream`)
Returns the image as a base64-encoded string along with the JSON data as a tuple: `[json_data, base64_image]`

**Use when:**
- Need to process image in memory
- Building APIs or web services
- Don't want to save files to disk

### Save Mode (`--save-image`)
Saves the image to disk with an auto-generated filename based on typhoon name and datetime.

**Use when:**
- Need to keep image files
- Creating archives
- Easier inspection of results

## Usage

### With analyze_pdf.py (Single PDF Analysis)

#### Extract and save image to file:
```bash
python analyze_pdf.py "path/to/bulletin.pdf" --extract-image --save-image
```

Output includes image path:
```json
{
  "typhoon_name": "Tropical Storm DANTE",
  "updated_datetime": "2025-07-23T17:00:00+0000",
  "image_path": "typhoon_track_Tropical_Storm_DANTE_2025-07-23T17-00-00+0000.png",
  ...
}
```

#### Extract image as base64 stream:
```bash
python analyze_pdf.py "path/to/bulletin.pdf" --extract-image --stream --json
```

Output format:
```json
[
  {
    "typhoon_name": "Tropical Storm DANTE",
    "updated_datetime": "2025-07-23T17:00:00+0000",
    ...
  },
  "iVBORw0KGgoAAAANSUhEUgAA..." // base64 image data
]
```

### With main.py (Automated Pipeline)

#### Extract from HTML and save image:
```bash
python main.py "bin/PAGASA BULLETIN PAGE/PAGASA.html" --extract-image --save-image
```

#### Extract from HTML and return as stream:
```bash
python main.py "bin/PAGASA BULLETIN PAGE/PAGASA.html" --extract-image --stream
```

#### Process with live URL (if accessible):
```bash
python main.py "https://www.pagasa.dost.gov.ph/tropical-cyclone/severe-weather-bulletin" --extract-image --save-image --verbose
```

### Standalone Image Extractor

You can also use the `typhoon_image_extractor.py` module directly:

#### Extract from PDF:
```bash
python typhoon_image_extractor.py "path/to/bulletin.pdf" --save output.png
```

#### Extract from HTML:
```bash
python typhoon_image_extractor.py "bin/PAGASA BULLETIN PAGE/PAGASA.html" --save output.png --tab 1
```

#### Extract from URL:
```bash
python typhoon_image_extractor.py "https://example.com/bulletin.html" --save output.png --tab 1
```

## Python API Usage

```python
from typhoon_image_extractor import TyphoonImageExtractor

# Initialize extractor
extractor = TyphoonImageExtractor()

# Extract from PDF (stream mode)
img_stream = extractor.extract_image_from_pdf("path/to/bulletin.pdf")
# img_stream is a BytesIO object

# Extract from HTML (stream mode)
img_stream = extractor.extract_image_from_html("path/to/page.html", tab_index=1)

# Auto-detect source and save to file
img_stream, img_path = extractor.extract_image(
    "path/to/source",  # PDF or HTML
    tab_index=1,        # For HTML extraction
    save_path="output.png"
)

# Save stream to file manually
extractor.save_image(img_stream, "custom_path.png")
```

## Image Filename Format

When using `--save-image`, files are automatically named using the pattern:
```
typhoon_track_{typhoon_name}_{datetime}.png
```

Example:
```
typhoon_track_Tropical_Storm_DANTE_2025-07-23T17-00-00+0000.png
```

## Important Notes

1. **Single PDF Analysis Only**: The `--extract-image` flag is designed for single PDF/bulletin analysis. It does NOT apply to batch operations.

2. **Method Auto-Detection**: The system automatically chooses the appropriate extraction method:
   - HTML/URL sources → Method 1 (HTML extraction)
   - PDF sources → Method 2 (PDF extraction)

3. **Tab Index**: For HTML extraction, the default tab index is 1 (first typhoon). Adjust using `--tab` parameter if needed.

4. **No Temp Files**: In stream mode, images are never written to disk - they remain in memory only.

5. **Image Quality**: 
   - HTML extraction: Full resolution (typically 800x600 or higher)
   - PDF extraction: Extracted at 150 DPI (suitable for analysis)

6. **Dependencies**: Uses existing packages only:
   - `requests` - For downloading images from URLs
   - `BeautifulSoup4` - For parsing HTML
   - `pdfplumber` - For PDF image extraction
   - `Pillow` - For image processing

## Error Handling

The extractor includes robust error handling:
- Missing source files
- Network errors (for URLs)
- Invalid HTML structure
- Missing images in PDFs
- Invalid tab indices

All errors are reported with descriptive messages.

## Testing

Run the test suite to verify the functionality:
```bash
python test_image_extraction.py
```

This tests:
1. PDF extraction (stream and save modes)
2. HTML extraction (stream and save modes)
3. Integration with analyze_pdf.py
4. Integration with main.py

## Examples

### Example 1: Quick analysis with image
```bash
python analyze_pdf.py "dataset/pdfs/sample.pdf" --extract-image --save-image
```

### Example 2: API-ready output
```bash
python main.py --extract-image --stream > api_output.json
```

### Example 3: Archive all bulletins with images
```bash
for pdf in dataset/pdfs/**/*.pdf; do
    python analyze_pdf.py "$pdf" --extract-image --save-image --json > "${pdf%.pdf}.json"
done
```

### Example 4: Extract from wayback machine
```bash
python main.py "https://web.archive.org/web/20251109044718/https://www.pagasa.dost.gov.ph/tropical-cyclone/severe-weather-bulletin" --extract-image --save-image --verbose
```

## Troubleshooting

**Image not found in HTML**
- Check if the tab index is correct
- Verify HTML structure matches expected format
- Try different tab index with `--tab` parameter

**Image extraction from PDF failed**
- Ensure PDF contains images on first page
- Check if PDF is a valid PAGASA bulletin format
- Try using HTML source instead

**Network errors**
- Check internet connectivity
- Try using local HTML/PDF files
- Use wayback machine archives if live site is unavailable

## Performance

- HTML extraction: < 1 second (local files), 1-5 seconds (remote URLs)
- PDF extraction: 1-3 seconds per bulletin
- Stream mode: No disk I/O, minimal memory usage
- Save mode: One disk write per image

## Future Enhancements

Possible future improvements:
- Batch image extraction from multiple PDFs
- Image comparison/analysis features
- Animated track generation from multiple bulletins
- Integration with mapping services
- Image quality enhancement
