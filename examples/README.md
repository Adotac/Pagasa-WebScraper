# Examples

This directory contains example scripts demonstrating how to use the PAGASA WebScraper components.

## Available Examples

### 1. `example_advisory_usage.py`
Demonstrates how to use the advisory scraper to extract rainfall warning data from PAGASA weather advisory pages.

**Usage:**
```bash
python examples/example_advisory_usage.py
```

### 2. `example_image_extraction.py`
Shows how to extract typhoon track images from PAGASA bulletin PDFs and HTML pages.

**Usage:**
```bash
python examples/example_image_extraction.py
```

### 3. `example_main_usage.py`
Comprehensive examples showing how to use the main pipeline programmatically, including:
- Basic usage with HTML files
- Processing all typhoons
- JSON output generation
- Multiple sources
- Integration patterns for automated monitoring

**Usage:**
```bash
python examples/example_main_usage.py
```

### 4. `example_scraper_usage.py`
Demonstrates how to use the bulletin scraper to extract PDF links from PAGASA bulletin pages.

**Usage:**
```bash
python examples/example_scraper_usage.py
```

## Running Examples

All examples can be run directly from the repository root:

```bash
# Run from repository root
cd /path/to/Pagasa-WebScraper
python examples/example_main_usage.py
```

Or from within the examples directory:

```bash
# Run from examples directory
cd examples
python example_main_usage.py
```

## Notes

- Most examples expect certain data files to be present in the `bin/` and `dataset/` directories
- Some examples may require internet connectivity to fetch live data from PAGASA
- Check each example script's docstring for specific requirements and usage details
