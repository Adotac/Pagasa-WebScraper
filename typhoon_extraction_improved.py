"""
PAGASA PDF Extraction Algorithm - Table-Based Extraction

This module extracts typhoon bulletin data from PDFs using table detection
and heuristic pattern recognition to achieve high-accuracy extraction
of signal warnings and rainfall data following the official PAGASA table format.
"""

import re
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import pdfplumber
from datetime import datetime
import json


class LocationMatcher:
    """Matches location names from PDFs to Philippine administrative divisions"""
    
    REGION_MAPPING = {
        'Ilocos Region': 'Luzon',
        'Cagayan Valley': 'Luzon',
        'Central Luzon': 'Luzon',
        'CALABARZON': 'Luzon',
        'MIMAROPA': 'Luzon',
        'Bicol Region': 'Luzon',
        'Western Visayas': 'Visayas',
        'Central Visayas': 'Visayas',
        'Eastern Visayas': 'Visayas',
        'Zamboanga Peninsula': 'Mindanao',
        'Northern Mindanao': 'Mindanao',
        'Davao Region': 'Mindanao',
        'SOCCSKSARGEN': 'Mindanao',
        'Caraga': 'Mindanao',
        'Bangsamoro': 'Mindanao',
        'BARMM': 'Mindanao',
        'National Capital Region': 'Luzon',
        'NCR': 'Luzon',
        'Cordillera Administrative Region': 'Luzon',
        'CAR': 'Luzon',
    }
    
    def __init__(self, consolidated_csv_path: str = "bin/consolidated_locations.csv"):
        """Load consolidated locations mapping"""
        self.locations_df = pd.read_csv(consolidated_csv_path)
        
        self.priority = {'Province': 5, 'Region': 4, 'City': 3, 'Municipality': 2, 'Barangay': 1}
        
        self.location_dict = {}
        self.island_groups_dict = {'Luzon': set(), 'Visayas': set(), 'Mindanao': set()}
        
        grouped = {}
        for _, row in self.locations_df.iterrows():
            name_key = row['location_name'].lower()
            priority = self.priority.get(row['location_type'], 0)
            island_group = row['island_group']
            
            if name_key not in grouped:
                grouped[name_key] = {'priority': priority, 'island_group': island_group}
            elif priority > grouped[name_key]['priority']:
                grouped[name_key] = {'priority': priority, 'island_group': island_group}
        
        for name_key, info in grouped.items():
            self.location_dict[name_key] = info['island_group']
            if info['island_group'] in self.island_groups_dict:
                self.island_groups_dict[info['island_group']].add(name_key)
    
    def find_island_group(self, location_name: str) -> Optional[str]:
        """Find which island group a location belongs to"""
        if not location_name:
            return None
        
        name_lower = location_name.lower().strip()
        
        if name_lower in self.location_dict:
            return self.location_dict[name_lower]
        
        for known_location, island_group in self.location_dict.items():
            if name_lower in known_location or known_location in name_lower:
                return island_group
        
        for region_name, island_group in self.REGION_MAPPING.items():
            if region_name.lower() == name_lower:
                return island_group
            if region_name.lower() in name_lower or name_lower in region_name.lower():
                return island_group
        
        return None


class DateTimeExtractor:
    """Extracts datetime information from bulletin text"""
    
    @staticmethod
    def extract_issue_datetime(text: str) -> Optional[str]:
        """Extract 'Issued at' datetime pattern"""
        text_clean = re.sub(r'\s+', ' ', text)
        
        patterns = [
            r'ISSUED\s+AT\s+(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)[,\s]+\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4})',
            r'ISSUED\s+AT\s+(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)[,\s]+\d{1,2}\s+\w+\s+\d{4})',
            r'ISSUED\s*AT\s*([0-9]{1,2}:[0-9]{2}[AP]M[^0-9]*\d{1,2}\s+\w+\s+\d{4})',
            r'ISSUEDAT\s*([0-9]{1,2}:[0-9]{2}[AP]M[,\s]*\d{1,2}\s*\w+\s*\d{4})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_clean, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    @staticmethod
    def normalize_datetime(datetime_str: str) -> str:
        """Normalize datetime string to standard format"""
        if not datetime_str:
            return None
        
        try:
            dt = pd.to_datetime(datetime_str)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return datetime_str


class TableParser:
    """Parses table structures from PDF text"""
    
    @staticmethod
    def extract_tables_from_text(text: str) -> List[Dict[str, Any]]:
        """
        Extract table structures from text.
        Returns list of detected tables with their content.
        """
        tables = []
        text_lower = text.lower()
        
        # Signal table pattern
        if 'tropical cyclone wind signals' in text_lower or 'tcws' in text_lower:
            signal_table = TableParser._extract_signal_table(text)
            if signal_table:
                tables.append(signal_table)
        
        # Rainfall/Hazards table pattern
        if 'hazards affecting land areas' in text_lower or 'rainfall' in text_lower:
            rainfall_table = TableParser._extract_rainfall_table(text)
            if rainfall_table:
                tables.append(rainfall_table)
        
        return tables
    
    @staticmethod
    def _extract_signal_table(text: str) -> Optional[Dict[str, Any]]:
        """Extract wind signal table from text"""
        # Look for table header
        patterns = [
            r'tropical\s+cyclone\s+wind\s+signals\s+in\s+effect(.*?)(?:hazard|rainfall|$)',
            r'tcws(.*?)(?:hazard|rainfall|$)',
        ]
        
        table_content = None
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                table_content = match.group(1)
                break
        
        if not table_content:
            return None
        
        return {
            'type': 'signal',
            'content': table_content
        }
    
    @staticmethod
    def _extract_rainfall_table(text: str) -> Optional[Dict[str, Any]]:
        """Extract rainfall/hazards table from text"""
        patterns = [
            r'hazards\s+affecting\s+land\s+areas(.*?)(?:wind|$)',
            r'rainfall(.*?)(?:wind|$)',
        ]
        
        table_content = None
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                table_content = match.group(1)
                break
        
        if not table_content:
            return None
        
        return {
            'type': 'rainfall',
            'content': table_content
        }


class SignalWarningExtractor:
    """Extracts Tropical Cyclone Wind Signal warnings (TCWS 1-5) from table structures"""
    
    def __init__(self, location_matcher: LocationMatcher):
        self.location_matcher = location_matcher
    
    def extract_signals(self, text: str) -> Dict[int, Dict[str, Optional[str]]]:
        """
        Extract signal warnings from text.
        Returns: {signal_level: {island_group: location_string}}
        """
        result = {1: {}, 2: {}, 3: {}, 4: {}, 5: {}}
        
        text_lower = text.lower()
        text_clean = re.sub(r'\s+', ' ', text_lower)
        
        # Check for "no signal" statement
        if 'no tropical cyclone wind signal' in text_clean or 'no wind signal' in text_clean:
            return result
        
        # Extract signal section
        signal_section = self._extract_signal_section(text_clean)
        if not signal_section:
            return result
        
        # Try to parse table structure
        signals_with_locations = self._parse_signal_table(signal_section, text)
        
        return signals_with_locations
    
    def _extract_signal_section(self, text: str) -> str:
        """Extract the signals/winds section from bulletin"""
        patterns = [
            r'tropical\s+cyclone\s+wind\s+signals\s+in\s+effect(.*?)(?:hazard|rainfall|$)',
            r'wind\s+signals?(.*?)(?:hazard|rainfall|$)',
            r'tcws(.*?)(?:hazard|rainfall|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1)
        
        return None
    
    def _parse_signal_table(self, table_text: str, full_text: str) -> Dict[int, Dict[str, Optional[str]]]:
        """
        Parse signal table to extract signal levels and associated locations.
        Looks for signal numbers (1-5) and maps them to island groups and locations.
        """
        result = {1: {}, 2: {}, 3: {}, 4: {}, 5: {}}
        
        # Strategy: Find signal numbers mentioned, then extract locations that follow
        # For each signal level, find the next occurrence and extract locations
        
        signal_patterns = [
            (r'(?:signal|tcws|no\.)\s*[#]?(\d)(?:\s|[:\-])', 1),  # "Signal 1:", "TCWS 1", etc.
            (r'\*?\*?(\d)\*?\*?\s*(?:\||—)', 1),  # "1 |" or "1 |"
            (r'tcws\s*(\d)\s*[:\-]', 1),  # "TCWS 1:"
        ]
        
        # Find all signal numbers in table
        signal_mentions = {}
        for pattern, offset in signal_patterns:
            for match in re.finditer(pattern, table_text, re.IGNORECASE):
                signal_num = int(match.group(1))
                if 1 <= signal_num <= 5:
                    if signal_num not in signal_mentions:
                        signal_mentions[signal_num] = match.start()
        
        if not signal_mentions:
            # Fallback: Try to identify highest signal mentioned in text
            highest_signal = self._identify_highest_signal(table_text)
            if highest_signal:
                # Extract all locations mentioned after signal keywords
                locations_by_group = self._extract_locations_from_section(table_text, full_text)
                for island_group, locations in locations_by_group.items():
                    if locations:
                        result[highest_signal][island_group] = ', '.join(locations)
            return result
        
        # For each signal found, extract locations
        for signal_num in sorted(signal_mentions.keys()):
            start_pos = signal_mentions[signal_num]
            
            # Find next signal or end of table
            next_signal_pos = len(table_text)
            for other_signal in signal_mentions:
                if other_signal > signal_num:
                    pos = signal_mentions[other_signal]
                    if pos < next_signal_pos:
                        next_signal_pos = pos
            
            # Extract content for this signal
            signal_content = table_text[start_pos:next_signal_pos]
            
            # Extract locations for each island group
            locations_by_group = self._extract_locations_from_section(signal_content, full_text)
            
            for island_group, locations in locations_by_group.items():
                if locations:
                    result[signal_num][island_group] = ', '.join(locations)
        
        return result
    
    def _identify_highest_signal(self, text: str) -> Optional[int]:
        """Identify highest signal number mentioned in text"""
        highest = None
        patterns = [
            r'(?:signal|tcws)[^0-9]*?(\d)',
            r'signal\s+(?:no\.?\s+)?(\d)',
            r'tcws\s+(\d)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                signal_num = int(match)
                if signal_num > 0 and signal_num <= 5:
                    if highest is None or signal_num > highest:
                        highest = signal_num
        
        return highest
    
    def _extract_locations_from_section(self, section: str, full_text: str) -> Dict[str, List[str]]:
        """Extract locations for each island group from a section"""
        result = {'Luzon': [], 'Visayas': [], 'Mindanao': [], 'Other': []}
        
        # Look for island group mentions
        section_lower = section.lower()
        
        # Pattern: "Luzon: location1, location2, ..." or "over Luzon: ..."
        island_group_patterns = [
            (r'(?:luzon|over\s+luzon)[\s:\-]*([^,\n]*(?:,[^,\n]*)*)', 'Luzon'),
            (r'(?:visayas|over\s+visayas)[\s:\-]*([^,\n]*(?:,[^,\n]*)*)', 'Visayas'),
            (r'(?:mindanao|over\s+mindanao)[\s:\-]*([^,\n]*(?:,[^,\n]*)*)', 'Mindanao'),
        ]
        
        for pattern, island_group in island_group_patterns:
            matches = re.findall(pattern, section_lower, re.IGNORECASE)
            for match in matches:
                # Parse location names from match
                locations = [loc.strip() for loc in match.split(',') if loc.strip()]
                if locations:
                    result[island_group].extend(locations)
        
        # Also try extracting from full text after island group headers
        if not any(result.values()):
            # Look for explicit island group names followed by locations
            for island_group_name in ['luzon', 'visayas', 'mindanao']:
                pattern = f'{island_group_name}\\s+([^\\n{{\\|]*?)(?:visayas|mindanao|luzon|hazard|rainfall|wind|$)'
                match = re.search(pattern, full_text, re.IGNORECASE | re.DOTALL)
                if match:
                    locations_text = match.group(1)
                    locations = self._parse_locations_from_text(locations_text)
                    for loc in locations:
                        island = 'Luzon' if island_group_name == 'luzon' else \
                                 'Visayas' if island_group_name == 'visayas' else 'Mindanao'
                        if loc not in result[island]:
                            result[island].append(loc)
        
        return result
    
    def _parse_locations_from_text(self, text: str) -> List[str]:
        """Parse location names from text"""
        locations = []
        
        # Remove parenthetical clarifications for now
        text = re.sub(r'\([^)]*\)', '', text)
        
        # Split by common delimiters
        parts = re.split(r'[,;]', text)
        
        for part in parts:
            part = part.strip()
            if part and len(part) > 2:
                locations.append(part)
        
        return locations


class RainfallWarningExtractor:
    """Extracts Rainfall warnings from table structures"""
    
    def __init__(self, location_matcher: LocationMatcher):
        self.location_matcher = location_matcher
    
    def extract_rainfall_warnings(self, text: str) -> Dict[str, Dict[str, Optional[str]]]:
        """
        Extract rainfall warnings for each island group with location names.
        Returns: {warning_level: {island_group: location_string}}
        """
        result = {1: {}, 2: {}, 3: {}}
        
        text_clean = re.sub(r'\s+', ' ', text.lower())
        
        # Extract rainfall section
        rainfall_section = self._extract_rainfall_section(text_clean)
        if not rainfall_section:
            return result
        
        # Identify warning levels in rainfall section
        warning_levels = self._identify_rainfall_levels(rainfall_section)
        
        if not warning_levels:
            return result
        
        # Extract locations for each warning level
        for level in sorted(warning_levels.keys()):
            level_content = warning_levels[level]
            locations_by_group = self._extract_locations_from_rainfall_section(level_content, text)
            
            for island_group, locations in locations_by_group.items():
                if locations:
                    result[level][island_group] = ', '.join(locations)
        
        return result
    
    def _extract_rainfall_section(self, text: str) -> str:
        """Extract the rainfall/hazards section"""
        patterns = [
            r'(?:hazards affecting|rainfall)(.*?)(?:winds:|$)',
            r'(?:rainfall)(.*?)(?:winds:|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1)
        
        return text
    
    def _identify_rainfall_levels(self, text: str) -> Dict[int, str]:
        """Identify rainfall warning levels and their content"""
        result = {}
        
        # Look for intensity descriptors that map to levels
        # Level 1: intense/extremely heavy
        # Level 2: heavy/moderate to heavy
        # Level 3: light to moderate/advisory
        
        level_keywords = {
            1: ['intense', 'extremely heavy', '>30', 'flash flood'],
            2: ['heavy', '15-30', 'moderate flooding'],
            3: ['moderate', 'light to moderate', '7.5-15', 'advisory'],
        }
        
        for level, keywords in level_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    # Found this level - extract content
                    # Find the section for this level
                    pattern = f'{keyword}.*?(?:{"intense|extremely heavy|heavy|moderate|light to moderate|advisory"}|$)'
                    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                    if match:
                        result[level] = match.group(0)
        
        # If no levels found, assume level 2 for any rainfall mentioned
        if not result:
            if 'rainfall' in text or 'rain' in text:
                result[2] = text
        
        return result
    
    def _extract_locations_from_rainfall_section(self, section: str, full_text: str) -> Dict[str, List[str]]:
        """Extract locations from a rainfall section"""
        result = {'Luzon': [], 'Visayas': [], 'Mindanao': [], 'Other': []}
        
        section_lower = section.lower()
        
        # Extract over/across mentions
        over_patterns = [
            r'over\s+([^.;]*)',
            r'across\s+([^.;]*)',
            r'affecting\s+([^.;]*)',
        ]
        
        location_text = ""
        for pattern in over_patterns:
            matches = re.findall(pattern, section_lower, re.IGNORECASE)
            location_text += " ".join(matches) + " "
        
        if not location_text.strip():
            location_text = section
        
        # Parse locations and categorize by island group
        locations = self._parse_rainfall_locations(location_text)
        
        for location in locations:
            island_group = self.location_matcher.find_island_group(location)
            if island_group:
                if location not in result[island_group]:
                    result[island_group].append(location)
            else:
                if location not in result['Other']:
                    result['Other'].append(location)
        
        # Clean up empty groups
        return {k: v for k, v in result.items() if v}
    
    def _parse_rainfall_locations(self, text: str) -> List[str]:
        """Parse location names from rainfall section"""
        locations = []
        
        # Remove parenthetical clarifications
        text = re.sub(r'\([^)]*\)', '', text)
        
        # Split by common delimiters
        parts = re.split(r'[,;]', text)
        
        for part in parts:
            part = part.strip()
            # Remove common non-location words
            part = re.sub(r'(?:and|or|including|islands?|province|region|the|rest|of|portion|northern|southern|eastern|western|central)\s+', '', part, flags=re.IGNORECASE)
            part = part.strip()
            
            if part and len(part) > 2:
                locations.append(part)
        
        return locations


class TyphoonBulletinExtractor:
    """Main extractor that combines all components"""
    
    def __init__(self):
        self.location_matcher = LocationMatcher()
        self.datetime_extractor = DateTimeExtractor()
        self.signal_extractor = SignalWarningExtractor(self.location_matcher)
        self.rainfall_extractor = RainfallWarningExtractor(self.location_matcher)
    
    def extract_from_pdf(self, pdf_path: str) -> Dict:
        """Extract complete TyphoonHubType data from PDF"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                full_text = "\n".join([page.extract_text() or "" for page in pdf.pages])
        except Exception as e:
            print(f"Error reading PDF {pdf_path}: {e}")
            return None
        
        # Extract components
        issue_datetime = self.datetime_extractor.extract_issue_datetime(full_text)
        normalized_datetime = self.datetime_extractor.normalize_datetime(issue_datetime)
        
        typhoon_location = self._extract_typhoon_location(full_text)
        typhoon_movement = self._extract_typhoon_movement(full_text)
        typhoon_windspeed = self._extract_typhoon_windspeed(full_text)
        
        signals_by_level = self.signal_extractor.extract_signals(full_text)
        rainfall_by_level = self.rainfall_extractor.extract_rainfall_warnings(full_text)
        
        # Build result structure
        result = {
            'typhoon_location_text': typhoon_location,
            'typhoon_movement': typhoon_movement,
            'typhoon_windspeed': typhoon_windspeed,
            'updated_datetime': normalized_datetime,
            'signal_warning_tags1': self._build_island_group_dict_from_warnings(signals_by_level, 1),
            'signal_warning_tags2': self._build_island_group_dict_from_warnings(signals_by_level, 2),
            'signal_warning_tags3': self._build_island_group_dict_from_warnings(signals_by_level, 3),
            'signal_warning_tags4': self._build_island_group_dict_from_warnings(signals_by_level, 4),
            'signal_warning_tags5': self._build_island_group_dict_from_warnings(signals_by_level, 5),
            'rainfall_warning_tags1': self._build_island_group_dict_from_warnings(rainfall_by_level, 1),
            'rainfall_warning_tags2': self._build_island_group_dict_from_warnings(rainfall_by_level, 2),
            'rainfall_warning_tags3': self._build_island_group_dict_from_warnings(rainfall_by_level, 3),
        }
        
        return result
    
    def _extract_typhoon_location(self, text: str) -> str:
        """Extract current typhoon location text"""
        text_clean = re.sub(r'\s+', ' ', text)
        
        # Better pattern to avoid capturing garbage
        patterns = [
            r'located\s+([^.]*?(?:latitude|longitude|km|miles|east|west|north|south)[^.]*)',
            r'centered\s+([^.]*?(?:latitude|longitude|km|miles|east|west|north|south)[^.]*)',
            r'(?:at|near)\s+([^.]*?(?:latitude|longitude|km|miles|east|west|north|south)[^.]*)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_clean, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                # Limit length to avoid garbage
                if len(location) < 200:
                    return location
        
        return "Location not found"
    
    def _extract_typhoon_movement(self, text: str) -> str:
        """Extract typhoon movement information"""
        text_clean = re.sub(r'\s+', ' ', text)
        
        patterns = [
            r'(?:will|is expected to|forecast)\s+move\s+([^.]*?(?:northwest|northeast|west|east|north|south)[^.]*)',
            r'on\s+the\s+forecast\s+track[^.]*',
            r'(?:will|forecast)[^.]*?(?:westward|northwestward|northward|eastward|southward)[^.]*',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_clean, re.IGNORECASE)
            if match:
                movement = match.group(0).strip()
                if len(movement) < 200:
                    return movement
        
        return "Movement information not found"
    
    def _extract_typhoon_windspeed(self, text: str) -> str:
        """Extract maximum sustained wind speed"""
        text_clean = re.sub(r'\s+', ' ', text)
        
        patterns = [
            r'maximum\s+sustained\s+(?:wind)?s?\s+of\s+(\d+)\s*(?:km/h|kph)',
            r'(?:wind)?s?\s+of\s+(\d+)\s*(?:km/h|kph|km/hr)(?:\s+(?:sustained|wind))?',
            r'(\d+)\s*(?:km/h|kph|km/hr)(?:\s+(?:sustained|wind|maximum))?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_clean, re.IGNORECASE)
            if match:
                return f"Maximum sustained winds of {match.group(1)} km/h near the center"
        
        return "Wind speed not found"
    
    def _build_island_group_dict_from_warnings(self, warnings_by_level: Dict[int, Dict[str, Optional[str]]], level: int) -> Dict:
        """Build IslandGroupType dictionary for specific warning level"""
        result = {
            'Luzon': None,
            'Visayas': None,
            'Mindanao': None,
            'Other': None
        }
        
        if level in warnings_by_level:
            level_data = warnings_by_level[level]
            for island_group, location_string in level_data.items():
                if island_group in result:
                    result[island_group] = location_string
        
        return result


def extract_from_directory(pdfs_directory: str, output_json: str = "bin/extracted_typhoon_data.json"):
    """Extract data from all PDFs in a directory"""
    extractor = TyphoonBulletinExtractor()
    results = []
    
    pdfs_path = Path(pdfs_directory)
    pdf_files = list(pdfs_path.rglob("*.pdf"))
    
    print(f"Found {len(pdf_files)} PDF files")
    
    for i, pdf_file in enumerate(pdf_files):
        print(f"Processing [{i+1}/{len(pdf_files)}] {pdf_file.name}...")
        data = extractor.extract_from_pdf(str(pdf_file))
        if data:
            data['source_file'] = str(pdf_file)
            results.append(data)
    
    with open(output_json, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nExtracted {len(results)} bulletins")
    print(f"Results saved to {output_json}")
    
    return results


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = "dataset/pdfs"
    
    extract_from_directory(directory)
