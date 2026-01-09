#!/usr/bin/env python
"""
PAGASA Weather Advisory PDF Scraper

Scrapes PDFs from PAGASA's weather advisory page.
Extracts PDF files from elements with class "col-md-12 article-content weather-advisory".

Usage:
    python advisory_scraper.py
    
Downloads PDFs to: dataset/pdfs_advisory/
"""

import requests
import sys
import os
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import time


# Configuration
TARGET_URL = "https://www.pagasa.dost.gov.ph/weather/weather-advisory"
OUTPUT_DIR = Path(__file__).parent / "dataset" / "pdfs_advisory"


def setup_output_directory():
    """Create output directory if it doesn't exist."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[INFO] Output directory: {OUTPUT_DIR}")


def fetch_page_html(url):
    """
    Fetch HTML content from a URL.
    
    Args:
        url: URL to fetch
        
    Returns:
        HTML content as string, or None if failed
    """
    print(f"[STEP 1] Fetching page from: {url}")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        print("[SUCCESS] Page HTML retrieved")
        return response.text
        
    except requests.RequestException as e:
        print(f"[ERROR] Failed to fetch page: {e}")
        return None


def _has_advisory_classes(class_attr):
    """
    Check if element has required advisory classes.
    
    Args:
        class_attr: Class attribute value
        
    Returns:
        True if element has all required classes
    """
    return class_attr and 'col-md-12' in class_attr and 'article-content' in class_attr and 'weather-advisory' in class_attr


def extract_pdfs_from_advisory_elements(html_content, base_url):
    """
    Extract PDF links from elements with class "col-md-12 article-content weather-advisory".
    
    Args:
        html_content: HTML content to parse
        base_url: Base URL for resolving relative links
        
    Returns:
        List of PDF URLs found
    """
    print("[STEP 2] Parsing HTML and extracting PDFs...")
    
    soup = BeautifulSoup(html_content, 'html.parser')
    pdf_urls = []
    
    # Find all elements with the specified classes
    advisory_elements = soup.find_all('div', class_=_has_advisory_classes)
    
    if not advisory_elements:
        print("[WARNING] No elements found with class 'col-md-12 article-content weather-advisory'")
        # Try alternative search strategies
        advisory_elements = soup.find_all('div', class_='article-content weather-advisory')
        if not advisory_elements:
            advisory_elements = soup.find_all('div', class_='weather-advisory')
        
        if advisory_elements:
            print(f"[INFO] Found {len(advisory_elements)} element(s) using alternative search")
    else:
        print(f"[INFO] Found {len(advisory_elements)} advisory element(s)")
    
    # Extract PDF links from found elements
    for element in advisory_elements:
        links = element.find_all('a', href=True)
        for link in links:
            href = link.get('href', '')
            
            # Check if it's a PDF link
            if href.endswith('.pdf') or '.pdf' in href.lower():
                # Resolve relative URLs
                if not href.startswith('http'):
                    href = urljoin(base_url, href)
                
                if href not in pdf_urls:
                    pdf_urls.append(href)
                    print(f"[FOUND] PDF: {href}")
    
    print(f"[SUCCESS] Found {len(pdf_urls)} PDF(s)")
    return pdf_urls


def download_pdf(pdf_url, output_dir):
    """
    Download a PDF file.
    
    Args:
        pdf_url: URL of the PDF to download
        output_dir: Directory to save the PDF
        
    Returns:
        Path to downloaded file, or None if failed
    """
    try:
        # Generate filename
        parsed_url = urlparse(pdf_url)
        filename = os.path.basename(parsed_url.path)
        
        # Clean filename
        if not filename or not filename.endswith('.pdf'):
            filename = f"advisory_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        
        output_path = output_dir / filename
        
        # Check if file already exists
        if output_path.exists():
            print(f"[SKIP] File already exists: {filename}")
            return output_path
        
        # Download PDF
        print(f"[DOWNLOAD] Downloading: {filename}")
        response = requests.get(pdf_url, timeout=60)
        response.raise_for_status()
        
        # Save to file
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        print(f"[SUCCESS] Saved: {output_path}")
        return output_path
        
    except requests.RequestException as e:
        print(f"[ERROR] Failed to download PDF: {e}")
        return None
    except IOError as e:
        print(f"[ERROR] Failed to save PDF: {e}")
        return None


def main():
    """Main entry point."""
    print("="*70)
    print("PAGASA WEATHER ADVISORY PDF SCRAPER")
    print("="*70)
    print(f"Target URL: {TARGET_URL}")
    print()
    
    # Setup
    setup_output_directory()
    
    # Fetch HTML
    html_content = fetch_page_html(TARGET_URL)
    if not html_content:
        print("\n[ERROR] Failed to fetch page")
        return 1
    
    # Extract PDFs
    pdf_urls = extract_pdfs_from_advisory_elements(html_content, TARGET_URL)
    
    if not pdf_urls:
        print("\n[INFO] No PDFs found on the page")
        return 0
    
    # Download PDFs
    print(f"\n[STEP 3] Downloading {len(pdf_urls)} PDF(s)...")
    downloaded_files = []
    
    for i, pdf_url in enumerate(pdf_urls, 1):
        print(f"\n[{i}/{len(pdf_urls)}] Processing: {pdf_url}")
        
        output_path = download_pdf(pdf_url, OUTPUT_DIR)
        if output_path:
            downloaded_files.append(output_path)
        
        # Be nice to the server
        if i < len(pdf_urls):
            time.sleep(1)
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total PDFs downloaded: {len(downloaded_files)}")
    print(f"Output directory: {OUTPUT_DIR}")
    
    if downloaded_files:
        print("\nDownloaded files:")
        for filepath in downloaded_files:
            print(f"  - {filepath.name}")
    
    print("\n[COMPLETE] Scraping finished successfully")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Scraping cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
