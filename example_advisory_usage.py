#!/usr/bin/env python
"""
Example usage of advisory_scraper.

This demonstrates how the advisory extractor works.
"""

def main():
    """Display example usage."""
    print("="*70)
    print("ADVISORY EXTRACTOR - USAGE EXAMPLES")
    print("="*70)
    print()
    print("The advisory extractor parses rainfall warnings from HTML pages:")
    print("  https://www.pagasa.dost.gov.ph/weather/weather-advisory")
    print()
    print("Usage Examples:")
    print("="*70)
    print()
    print("1. Scrape from live URL and extract:")
    print("   python advisory_scraper.py")
    print()
    print("2. Extract from web archive URL:")
    print("   python advisory_scraper.py --archive")
    print()
    print("3. Extract from web archive with custom timestamp:")
    print("   python advisory_scraper.py --archive --timestamp 20251108223833")
    print()
    print("4. Extract from custom URL:")
    print("   python advisory_scraper.py 'https://example.com/weather/advisory'")
    print()
    print("5. JSON-only output (for piping):")
    print("   python advisory_scraper.py --json")
    print()
    print("="*70)
    print("HTML PARSING")
    print("="*70)
    print()
    print("The script parses HTML DOM to extract rainfall data:")
    print("- Looks for commented text in 'weekly-content-adv' div")
    print("- Extracts locations from all date columns (Today, Tomorrow, etc.)")
    print("- Validates locations against consolidated_locations.csv")
    print("- Stops at non-matching locations or 'Potential Impacts' text")
    print()
    print("="*70)
    print("OUTPUT FORMAT")
    print("="*70)
    print()
    print("JSON with 3 warning levels (red/orange/yellow):")
    print("- Red: >200mm rainfall")
    print("- Orange: 100-200mm rainfall")
    print("- Yellow: 50-100mm rainfall")
    print()
    print("Example output:")
    print("""
{
  "source_url": "https://www.pagasa.dost.gov.ph/weather/weather-advisory",
  "rainfall_warnings": {
    "red": ["Isabela", "Quirino", "Nueva Vizcaya", ...],
    "orange": ["Pangasinan", "Cagayan", "Apayao", ...],
    "yellow": ["Ilocos Norte", "Ilocos Sur", ...]
  }
}
    """)
    print()


if __name__ == "__main__":
    main()
