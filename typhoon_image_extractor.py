#!/usr/bin/env python
"""
Typhoon Image Extractor - Extract typhoon track images from HTML/URL or PDF.

This module provides two methods for extracting typhoon track images:
1. From live URL/HTML by locating the image element within tcwb-{number} sections
2. From PDF files using precise page coordinates (fallback method)

The image is always on the first page of PAGASA typhoon bulletins, located on the
right side of the table containing typhoon location, intensity, and movement data.
"""

import io
import re
import requests
from pathlib import Path
from typing import Optional, Tuple, Union
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import pdfplumber
from PIL import Image


class TyphoonImageExtractor:
    """Extract typhoon track images from HTML pages or PDF files"""
    
    def __init__(self):
        """Initialize the extractor"""
        pass
    
    def extract_image_from_html(
        self, 
        source: str, 
        tab_index: int = 1
    ) -> Optional[io.BytesIO]:
        """
        Extract typhoon track image from HTML page (live URL or local file).
        
        This method locates the tcwb-{tab_index} element and extracts the
        typhoon track image from within it.
        
        Args:
            source: URL or local file path to HTML content
            tab_index: Tab index number (default: 1 for first typhoon)
            
        Returns:
            BytesIO stream containing image data, or None if extraction fails
        """
        # Load HTML content
        try:
            if source.startswith('http://') or source.startswith('https://'):
                response = requests.get(source, timeout=30)
                response.raise_for_status()
                html_content = response.text
                base_url = source
            else:
                filepath = Path(source).resolve()
                if not filepath.exists():
                    print(f"Error: HTML file not found: {source}")
                    return None
                with open(filepath, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                # For local files, use the directory as base path
                base_url = None  # Will handle relative paths differently
        except Exception as e:
            print(f"Error loading HTML: {e}")
            return None
        
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find the tab panel with id=tcwb-{tab_index}
        tab_id = f'tcwb-{tab_index}'
        tab_panel = soup.find('div', id=tab_id)
        
        if not tab_panel:
            print(f"Error: Tab panel '{tab_id}' not found in HTML")
            return None
        
        # Find the image within this tab panel
        # Look for img tag with class containing 'image-preview' or 'img-responsive'
        img_tag = tab_panel.find('img', class_=lambda x: x and ('image-preview' in x or 'img-responsive' in x))
        
        if not img_tag:
            # Fallback: find any img tag in the tab panel
            img_tag = tab_panel.find('img')
        
        if not img_tag or not img_tag.get('src'):
            print(f"Error: No image found in tab panel '{tab_id}'")
            return None
        
        # Get image URL
        img_src = img_tag.get('src')
        
        # Handle relative URLs
        if not img_src.startswith('http'):
            # For local HTML files with relative paths
            if base_url and source.startswith('http'):
                img_url = urljoin(base_url, img_src)
            else:
                # Local file: resolve relative to HTML file location
                html_dir = Path(source).resolve().parent
                img_path = html_dir / img_src
                if not img_path.exists():
                    print(f"Error: Image file not found: {img_path}")
                    return None
                # Read local image file
                with open(img_path, 'rb') as f:
                    img_data = f.read()
                return io.BytesIO(img_data)
        else:
            img_url = img_src
        
        # Download the image
        try:
            response = requests.get(img_url, timeout=30)
            response.raise_for_status()
            return io.BytesIO(response.content)
        except Exception as e:
            print(f"Error downloading image from {img_url}: {e}")
            return None
    
    def extract_image_from_pdf(
        self, 
        pdf_path: str,
        page_number: int = 0
    ) -> Optional[io.BytesIO]:
        """
        Extract typhoon track image from PDF by cropping the region adjacent to
        Location/Intensity/Movement data.
        
        The typhoon track map is on the first page, on the RIGHT SIDE at the same
        vertical level as the "Location", "Intensity", and "Movement" text fields.
        Since it's not always embedded as a separate image object, we crop that
        region of the page and render it as an image.
        
        Args:
            pdf_path: Path to PDF file
            page_number: Page number to extract from (default: 0 for first page)
            
        Returns:
            BytesIO stream containing image data, or None if extraction fails
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                if page_number >= len(pdf.pages):
                    print(f"Error: Page {page_number} not found in PDF")
                    return None
                
                page = pdf.pages[page_number]
                
                # Strategy: Find the Location/Intensity/Movement text section
                # and crop the adjacent right-side area to capture the track map
                
                try:
                    words = page.extract_words()
                    location_y = None
                    intensity_y = None
                    movement_y = None
                    
                    # Find the key text positions
                    header_bottom_y = None
                    for word in words:
                        if 'Location' in word['text'] and word['x0'] < 100:
                            location_y = word['top']
                        elif word['text'] == 'Intensity' and word['x0'] < 100:
                            intensity_y = word['top']
                        elif 'Movement' in word['text'] and word['x0'] < 150:
                            movement_y = word['top']
                        
                        # Track header/first row bottom - text in the top 150 pixels
                        if word['top'] < 150:
                            if header_bottom_y is None or word['bottom'] > header_bottom_y:
                                header_bottom_y = word['bottom']
                    
                    # Find the "TRACK AND INTENSITY FORECAST" heading to use as bottom boundary
                    forecast_heading_y = None
                    for word in words:
                        if word['text'] == 'TRACK':
                            # Check if this is part of the forecast heading
                            nearby_words = [w for w in words if abs(w['top'] - word['top']) < 5]
                            nearby_text = ' '.join([w['text'] for w in sorted(nearby_words, key=lambda x: x['x0'])])
                            if 'INTENSITY' in nearby_text and 'FORECAST' in nearby_text:
                                forecast_heading_y = word['top']
                                break
                    
                    if location_y and movement_y:
                        # Define the crop region for the track map
                        # It should be on the right side, at the same Y-level as the data
                        
                        # Y coordinates: Use Location cell's top as the top boundary
                        # This ensures we start right at the Location row, excluding the header
                        y_top = location_y
                        
                        # Bottom boundary: stop at the "TRACK AND INTENSITY FORECAST" heading
                        if forecast_heading_y:
                            y_bottom = forecast_heading_y - 5  # Stop 5px before the heading
                        else:
                            # Fallback if heading not found
                            y_bottom = max(movement_y, intensity_y if intensity_y else movement_y) + 80
                        
                        # X coordinates: Start from the right side of the Location/Intensity/Movement cells
                        # Find the rightmost edge of these text cells to exclude them from the image
                        location_word = next((w for w in words if 'Location' in w['text']), None)
                        intensity_word = next((w for w in words if 'Intensity' in w['text']), None)
                        movement_word = next((w for w in words if 'Movement' in w['text']), None)
                        
                        # Get the rightmost x coordinate of these cells
                        cell_right_edges = []
                        if location_word:
                            cell_right_edges.append(location_word['x1'])
                        if intensity_word:
                            cell_right_edges.append(intensity_word['x1'])
                        if movement_word:
                            cell_right_edges.append(movement_word['x1'])
                        
                        if cell_right_edges:
                            # Start from the right edge of the cells, with a small margin
                            x_left = max(cell_right_edges) + 10
                        else:
                            # Fallback: use middle of page
                            x_left = page.width * 0.50
                        
                        x_right = page.width - 40   # Leave small margin on right
                        
                        # Crop and convert to image at higher resolution for clarity
                        cropped_region = page.crop((x_left, y_top, x_right, y_bottom))
                        pil_image = cropped_region.to_image(resolution=300)
                        
                        # Save to BytesIO
                        img_bytes = io.BytesIO()
                        pil_image.save(img_bytes, format='PNG')
                        img_bytes.seek(0)
                        
                        return img_bytes
                    
                except Exception as e:
                    print(f"Error using text-based positioning: {e}")
                
                # Fallback: Try to extract from embedded images if text-based approach fails
                if page.images:
                    # Look for images that might be the track map
                    best_image = None
                    max_score = 0
                    
                    for img_info in page.images:
                        width = img_info['x1'] - img_info['x0']
                        height = img_info['y1'] - img_info['y0']
                        area = width * height
                        x_center = (img_info['x0'] + img_info['x1']) / 2
                        
                        # Must be on right side
                        if x_center <= page.width / 2:
                            continue
                        
                        # Must be reasonably sized
                        if area < 10000:
                            continue
                        
                        # Check if image contains forecast table text
                        try:
                            cropped_area = page.crop((img_info['x0'], img_info['y0'], 
                                                     img_info['x1'], img_info['y1']))
                            img_text = cropped_area.extract_text() or ""
                            
                            # Skip forecast table images
                            forecast_indicators = ['Legazpi', 'Daet', 'Baler', 'Kapangan', 'Bacnotan', 
                                                  'TY WNW', 'STY', 'STS', 'PAR)', 'Batanes']
                            indicator_count = sum(1 for indicator in forecast_indicators if indicator in img_text)
                            
                            if indicator_count >= 3:
                                continue
                        except:
                            pass
                        
                        # Score based on position and size
                        score = area
                        
                        # Prefer images in upper-middle vertical range
                        from_top = page.height - img_info['y1']
                        if 150 < from_top < 400:
                            score *= 2.0
                        elif 100 < from_top < 500:
                            score *= 1.5
                        
                        if score > max_score:
                            max_score = score
                            best_image = img_info
                    
                    if best_image:
                        # Extract the image
                        x0, y0, x1, y1 = best_image['x0'], best_image['y0'], best_image['x1'], best_image['y1']
                        cropped_page = page.crop((x0, y0, x1, y1))
                        pil_image = cropped_page.to_image(resolution=150)
                        
                        img_bytes = io.BytesIO()
                        pil_image.save(img_bytes, format='PNG')
                        img_bytes.seek(0)
                        
                        return img_bytes
                
                print("Error: Could not identify typhoon track image region")
                return None
                
        except Exception as e:
            print(f"Error extracting image from PDF: {e}")
            return None
    
        except Exception as e:
            print(f"Error extracting image from PDF: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def save_image(
        self, 
        img_stream: io.BytesIO, 
        output_path: str
    ) -> bool:
        """
        Save image stream to a file.
        
        Args:
            img_stream: BytesIO stream containing image data
            output_path: Path where to save the image
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Reset stream position
            img_stream.seek(0)
            
            # Ensure output directory exists
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save to file
            with open(output_path, 'wb') as f:
                f.write(img_stream.read())
            
            # Reset stream position for potential reuse
            img_stream.seek(0)
            
            return True
        except Exception as e:
            print(f"Error saving image to {output_path}: {e}")
            return False
    
    def extract_image(
        self,
        source: str,
        tab_index: int = 1,
        save_path: Optional[str] = None
    ) -> Union[io.BytesIO, Tuple[io.BytesIO, str], None]:
        """
        Extract typhoon track image from source (auto-detect HTML/URL vs PDF).
        
        Args:
            source: URL, HTML file path, or PDF file path
            tab_index: Tab index for HTML extraction (default: 1)
            save_path: Optional path to save image. If provided, also returns the path
            
        Returns:
            - BytesIO stream if save_path is None
            - Tuple (BytesIO stream, save_path) if save_path is provided
            - None if extraction fails
        """
        # Determine source type
        is_pdf = False
        
        if source.startswith('http://') or source.startswith('https://'):
            # Check if URL points to PDF
            if source.lower().endswith('.pdf'):
                is_pdf = True
        else:
            # Local file - check extension
            if Path(source).suffix.lower() == '.pdf':
                is_pdf = True
        
        # Extract image using appropriate method
        if is_pdf:
            img_stream = self.extract_image_from_pdf(source)
        else:
            img_stream = self.extract_image_from_html(source, tab_index)
        
        if not img_stream:
            return None
        
        # Save if requested
        if save_path:
            if self.save_image(img_stream, save_path):
                return (img_stream, save_path)
            else:
                return None
        
        return img_stream


def main():
    """Command-line interface for testing"""
    import sys
    
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nUsage:")
        print("  python typhoon_image_extractor.py <source> [--save <output_path>] [--tab <index>]")
        print("\nExamples:")
        print("  python typhoon_image_extractor.py 'bin/PAGASA BULLETIN PAGE/PAGASA.html'")
        print("  python typhoon_image_extractor.py dataset/pdfs/sample.pdf --save typhoon_track.png")
        print("  python typhoon_image_extractor.py https://www.pagasa.dost.gov.ph/... --tab 2")
        sys.exit(1)
    
    source = sys.argv[1]
    save_path = None
    tab_index = 1
    
    # Parse arguments
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--save' and i + 1 < len(sys.argv):
            save_path = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--tab' and i + 1 < len(sys.argv):
            tab_index = int(sys.argv[i + 1])
            i += 2
        else:
            i += 1
    
    # Extract image
    extractor = TyphoonImageExtractor()
    result = extractor.extract_image(source, tab_index, save_path)
    
    if result:
        if save_path:
            img_stream, path = result
            print(f"Success! Image saved to: {path}")
            print(f"Image size: {len(img_stream.getvalue())} bytes")
        else:
            print(f"Success! Image extracted to memory stream")
            print(f"Image size: {len(result.getvalue())} bytes")
    else:
        print("Failed to extract image")
        sys.exit(1)


if __name__ == "__main__":
    main()
