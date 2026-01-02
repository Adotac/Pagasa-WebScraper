#!/usr/bin/env python
"""
Main script: Combines web scraping and PDF analysis for PAGASA bulletins.

This script:
1. Uses scrape_bulletin.py to detect typhoon names and extract PDF links
2. Selects the latest PDF for each typhoon
3. Analyzes the latest PDF using analyze_pdf.py functionality

By default, outputs raw JSON data to stdout (for easy piping/parsing).
Use --verbose flag to see progress messages (sent to stderr).

Usage:
    python main.py                      # Uses default bin/PAGASA.html, outputs JSON
    python main.py <html_file_path>     # Uses specified HTML file, outputs JSON
    python main.py <url>                # Scrapes from URL, outputs JSON
    python main.py --help               # Show help message

Options:
    --verbose                           # Show progress messages (to stderr)
    --low-cpu                           # Limit CPU usage to ~30%
    --metrics                           # Show performance metrics (to stderr)

Examples:
    python main.py                                      # Pure JSON output
    python main.py --verbose                            # JSON + progress messages
    python main.py > output.json                        # Save JSON to file
    python main.py --verbose 2>/dev/null                # JSON only (suppress logs)
    python main.py | jq '.data.typhoon_windspeed'       # Parse with jq
"""

import sys
import json
import time
import psutil
import os
from pathlib import Path
from scrape_bulletin import scrape_bulletin
from typhoon_extraction_ml import TyphoonBulletinExtractor
import requests
import tempfile
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from contextlib import contextmanager


@contextmanager
def suppress_stdout():
    """Context manager to suppress stdout output."""
    with open(os.devnull, 'w') as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout


def get_typhoon_names_and_pdfs(source, verbose=False):
    """
    Extract typhoon names and PDF links from PAGASA bulletin page.
    
    This function extends the scrape_bulletin functionality to also
    capture typhoon names from the HTML tabs.
    
    Args:
        source: File path or URL to HTML content
        verbose: If True, show loading messages
        
    Returns:
        List of tuples: [(typhoon_name, [pdf_urls]), ...]
        If no names available, returns [("Unknown", [pdf_urls]), ...]
    """
    # Load HTML content
    if source.startswith('http://') or source.startswith('https://'):
        if verbose:
            print(f"Loading HTML from URL: {source}", file=sys.stderr)
        response = requests.get(source, timeout=30)
        response.raise_for_status()
        html_content = response.text
    else:
        filepath = Path(source)
        if not filepath.exists():
            raise FileNotFoundError(f"HTML file not found: {source}")
        if verbose:
            print(f"Loading HTML from file: {source}", file=sys.stderr)
        with open(filepath, 'r', encoding='utf-8') as f:
            html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Try to extract typhoon names from tabs
    tab_list = soup.find('ul', class_='nav nav-tabs')
    typhoon_names = []
    
    if tab_list:
        tabs = tab_list.find_all('li', role='presentation')
        for tab in tabs:
            tab_link = tab.find('a')
            if tab_link:
                typhoon_name = tab_link.get_text(strip=True)
                typhoon_names.append(typhoon_name)
    
    # Get PDF links using the existing scraper (suppress its output if not verbose)
    if verbose:
        pdf_links_by_typhoon = scrape_bulletin(source)
    else:
        with suppress_stdout():
            pdf_links_by_typhoon = scrape_bulletin(source)
    
    # Combine names with PDF links
    result = []
    for i, pdf_links in enumerate(pdf_links_by_typhoon):
        if i < len(typhoon_names):
            name = typhoon_names[i]
        else:
            name = f"Typhoon {i+1}"
        result.append((name, pdf_links))
    
    return result


def get_latest_pdf(pdf_urls):
    """
    Select the latest PDF from a list of PDF URLs.
    
    Assumes PDFs are ordered chronologically, with the latest last.
    
    Args:
        pdf_urls: List of PDF URLs
        
    Returns:
        Latest PDF URL, or None if list is empty
    """
    if not pdf_urls:
        return None
    return pdf_urls[-1]


def download_pdf_if_needed(pdf_url, verbose=False):
    """
    Download PDF from URL to temporary file if needed.
    
    Args:
        pdf_url: URL or local path to PDF
        verbose: If True, show download messages
        
    Returns:
        Tuple of (local_path, is_temp) where is_temp indicates if cleanup is needed
    """
    if pdf_url.startswith('http://') or pdf_url.startswith('https://'):
        if verbose:
            print(f"  Downloading PDF from: {pdf_url}", file=sys.stderr)
        try:
            response = requests.get(pdf_url, timeout=30)
            response.raise_for_status()
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                tmp.write(response.content)
                temp_path = tmp.name
            
            if verbose:
                print(f"  Saved to temporary file: {temp_path}", file=sys.stderr)
            return temp_path, True
        except requests.exceptions.RequestException as e:
            if verbose:
                print(f"  Error downloading PDF: {e}", file=sys.stderr)
            return None, False
    else:
        # Local file
        if not Path(pdf_url).exists():
            if verbose:
                print(f"  Error: Local file not found: {pdf_url}", file=sys.stderr)
            return None, False
        return pdf_url, False


def analyze_pdf(pdf_path, low_cpu_mode=False):
    """
    Analyze a PDF using the TyphoonBulletinExtractor.
    
    Args:
        pdf_path: Path to PDF file
        low_cpu_mode: Whether to limit CPU usage
        
    Returns:
        Dictionary of extracted data, or None on failure
    """
    extractor = TyphoonBulletinExtractor()
    process = psutil.Process(os.getpid())
    
    try:
        data = extractor.extract_from_pdf(pdf_path)
        
        # Apply CPU throttling if enabled
        if low_cpu_mode:
            from analyze_pdf import cpu_throttle
            cpu_throttle(process, target_cpu_percent=30)
        
        return data
    except Exception as e:
        print(f"  Error analyzing PDF: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        del extractor


def display_results(typhoon_name, data):
    """Display extraction results in a readable format."""
    print("\n" + "=" * 80)
    print(f"PAGASA BULLETIN ANALYSIS - {typhoon_name}")
    print("=" * 80)
    
    # Basic Info
    print("\n[BASIC INFORMATION]")
    print(f"  Issued:       {data.get('updated_datetime', 'N/A')}")
    print(f"  Location:     {data.get('typhoon_location_text', 'N/A')}")
    print(f"  Wind Speed:   {data.get('typhoon_windspeed', 'N/A')}")
    print(f"  Movement:     {data.get('typhoon_movement', 'N/A')}")
    
    # Signal Warnings
    print("\n[SIGNAL WARNINGS (TCWS)]")
    signal_found = False
    for level in range(1, 6):
        tag_key = f'signal_warning_tags{level}'
        tag = data.get(tag_key, {})
        
        # Check if any island group has locations
        has_locations = any(tag.get(ig) for ig in ['Luzon', 'Visayas', 'Mindanao', 'Other'])
        
        if has_locations:
            signal_found = True
            print(f"\n  Signal {level}:")
            for island_group in ['Luzon', 'Visayas', 'Mindanao', 'Other']:
                locations = tag.get(island_group)
                if locations:
                    print(f"    {island_group:12} -> {locations}")
    
    if not signal_found:
        print("  [OK] No tropical cyclone wind signals in effect")
    
    # Rainfall Warnings
    print("\n[RAINFALL WARNINGS]")
    rainfall_found = False
    
    rainfall_levels = {
        1: "Level 1 - Intense Rainfall (>30mm/hr, RED)",
        2: "Level 2 - Heavy Rainfall (15-30mm/hr, ORANGE)",
        3: "Level 3 - Heavy Rainfall Advisory (7.5-15mm/hr, YELLOW)"
    }
    
    for level in range(1, 4):
        tag_key = f'rainfall_warning_tags{level}'
        tag = data.get(tag_key, {})
        
        # Check if any island group has locations
        has_locations = any(tag.get(ig) for ig in ['Luzon', 'Visayas', 'Mindanao', 'Other'])
        
        if has_locations:
            rainfall_found = True
            print(f"\n  {rainfall_levels[level]}:")
            for island_group in ['Luzon', 'Visayas', 'Mindanao', 'Other']:
                locations = tag.get(island_group)
                if locations:
                    print(f"    {island_group:12} -> {locations}")
    
    if not rainfall_found:
        print("  [OK] No rainfall warnings issued")
    
    print("\n" + "=" * 80 + "\n")


def main():
    """Main entry point."""
    # Parse arguments
    if '--help' in sys.argv or '-h' in sys.argv:
        print(__doc__)
        sys.exit(0)
    
    low_cpu_mode = '--low-cpu' in sys.argv
    show_metrics = '--metrics' in sys.argv
    verbose = '--verbose' in sys.argv
    
    # Filter out flags to get source
    args = [arg for arg in sys.argv[1:] if not arg.startswith('--')]
    
    # Determine source
    if args:
        source = args[0]
    else:
        default_html = Path(__file__).parent / "bin" / "PAGASA.html"
        if not default_html.exists():
            if verbose:
                print("Error: Default HTML file not found at bin/PAGASA.html", file=sys.stderr)
                print(f"Usage: python {sys.argv[0]} <html_file_or_url>", file=sys.stderr)
            sys.exit(1)
        source = str(default_html)
        if verbose:
            print(f"No source provided, using default: {source}", file=sys.stderr)
    
    start_time = time.time()
    process = psutil.Process(os.getpid())
    process.cpu_percent(interval=None)  # Initialize CPU monitoring
    time.sleep(0.1)
    
    if low_cpu_mode and verbose:
        print("[*] Low CPU mode enabled - limiting to ~30% CPU usage\n", file=sys.stderr)
    
    try:
        # Step 1: Extract typhoon names and PDF links
        if verbose:
            print("\n[STEP 1] Scraping PAGASA bulletin page...", file=sys.stderr)
            print("-" * 80, file=sys.stderr)
        typhoons_data = get_typhoon_names_and_pdfs(source, verbose=verbose)
        
        if not typhoons_data:
            if verbose:
                print("Error: No typhoons found in the bulletin page.", file=sys.stderr)
            sys.exit(1)
        
        if verbose:
            print(f"\nFound {len(typhoons_data)} typhoon(s):", file=sys.stderr)
            for name, pdfs in typhoons_data:
                print(f"  - {name}: {len(pdfs)} bulletin(s)", file=sys.stderr)
        
        # Step 2: Select the latest PDF from the first typhoon
        if verbose:
            print("\n[STEP 2] Selecting latest bulletin...", file=sys.stderr)
            print("-" * 80, file=sys.stderr)
        
        # Use the first typhoon (most recent)
        typhoon_name, pdf_urls = typhoons_data[0]
        latest_pdf = get_latest_pdf(pdf_urls)
        
        if not latest_pdf:
            if verbose:
                print(f"Error: No PDFs found for {typhoon_name}", file=sys.stderr)
            sys.exit(1)
        
        if verbose:
            print(f"  Typhoon: {typhoon_name}", file=sys.stderr)
            print(f"  Latest bulletin: {latest_pdf}", file=sys.stderr)
        
        # Step 3: Download PDF if needed
        if verbose:
            print("\n[STEP 3] Preparing PDF for analysis...", file=sys.stderr)
            print("-" * 80, file=sys.stderr)
        pdf_path, is_temp = download_pdf_if_needed(latest_pdf, verbose=verbose)
        
        if not pdf_path:
            if verbose:
                print("Error: Failed to access PDF", file=sys.stderr)
            sys.exit(1)
        
        # Step 4: Analyze the PDF
        if verbose:
            print("\n[STEP 4] Analyzing PDF...", file=sys.stderr)
            print("-" * 80, file=sys.stderr)
            print(f"  Processing: {Path(pdf_path).name}", file=sys.stderr)
        
        data = analyze_pdf(pdf_path, low_cpu_mode)
        
        if not data:
            if verbose:
                print("Error: Failed to extract data from PDF", file=sys.stderr)
            sys.exit(1)
        
        # Step 5: Display results - always output JSON by default
        output = {
            'typhoon_name': typhoon_name,
            'pdf_url': latest_pdf,
            'data': data
        }
        print(json.dumps(output, indent=2))
        
        # Cleanup
        if is_temp and pdf_path:
            try:
                Path(pdf_path).unlink()
                if verbose:
                    print(f"[CLEANUP] Removed temporary file: {pdf_path}", file=sys.stderr)
            except Exception as e:
                if verbose:
                    print(f"Warning: Could not delete temp file: {e}", file=sys.stderr)
        
        # Performance metrics
        elapsed = time.time() - start_time
        
        if show_metrics:
            cpu_percent = process.cpu_percent(interval=None)
            memory_info = process.memory_info()
            
            print(f"\n{'='*80}", file=sys.stderr)
            print("[PERFORMANCE METRICS]", file=sys.stderr)
            print(f"  Total execution time: {elapsed:.2f}s", file=sys.stderr)
            print(f"  Average CPU usage:    {cpu_percent:.1f}%", file=sys.stderr)
            print(f"  Memory used:          {memory_info.rss / 1024 / 1024:.2f} MB", file=sys.stderr)
            if low_cpu_mode:
                print(f"  Low CPU mode:         Enabled", file=sys.stderr)
            print(f"{'='*80}\n", file=sys.stderr)
        
        if verbose:
            print(f"\n[SUCCESS] Analysis completed in {elapsed:.2f}s", file=sys.stderr)
        
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Process stopped by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
