#!/usr/bin/env python
"""
Example usage of advisory_scraper.

This demonstrates how the advisory scraper works.
"""

def main():
    """Display example usage."""
    print("="*60)
    print("ADVISORY SCRAPER - USAGE")
    print("="*60)
    print()
    print("The advisory scraper directly fetches PDFs from:")
    print("  https://www.pagasa.dost.gov.ph/weather/weather-advisory")
    print()
    print("Usage:")
    print("  python advisory_scraper.py")
    print()
    print("Output location:")
    print("  dataset/pdfs_advisory/")
    print()
    print("What it does:")
    print("  1. Fetches live HTML from PAGASA weather advisory page")
    print("  2. Finds elements with class 'col-md-12 article-content weather-advisory'")
    print("  3. Extracts PDF links from those elements")
    print("  4. Downloads PDFs to output directory")
    print()


if __name__ == "__main__":
    main()
