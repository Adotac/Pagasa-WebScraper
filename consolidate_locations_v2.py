"""
Consolidate all Philippine locations (regions, provinces, municipalities, cities, barangays) 
into 3 major island groups: Luzon, Visayas, Mindanao.

This script reads PSGC CSV files and creates a unified CSV mapping all locations to island groups.
"""

import pandas as pd
from pathlib import Path
import csv

# Define region-to-island-group mapping based on Philippine administrative divisions
REGION_TO_ISLAND_GROUP = {
    '01': 'Luzon',      # Region I (Ilocos Region)
    '02': 'Luzon',      # Region II (Cagayan Valley)
    '03': 'Luzon',      # Region III (Central Luzon)
    '04': 'Luzon',      # Region IV-A (CALABARZON)
    '05': 'Luzon',      # Region V (Bicol Region)
    '14': 'Luzon',      # CAR (Cordillera Administrative Region)
    '13': 'Luzon',      # NCR (National Capital Region)
    '17': 'Luzon',      # MIMAROPA Region
    
    '06': 'Visayas',    # Region VI (Western Visayas)
    '07': 'Visayas',    # Region VII (Central Visayas)
    '08': 'Visayas',    # Region VIII (Eastern Visayas)
    
    '09': 'Mindanao',   # Region IX (Zamboanga Peninsula)
    '10': 'Mindanao',   # Region X (Northern Mindanao)
    '11': 'Mindanao',   # Region XI (Davao Region)
    '12': 'Mindanao',   # Region XII (SOCCSKSARGEN)
    '16': 'Mindanao',   # Region XIII (Caraga)
    '19': 'Mindanao',   # BARMM (Bangsamoro Autonomous Region in Muslim Mindanao)
}

def consolidate_locations():
    """Consolidate all locations into island groups"""
    base_path = Path("dataset/psgc_csv")
    output_path = Path("bin")
    output_path.mkdir(exist_ok=True)
    
    all_locations = []
    
    # Read regions
    print("Reading regions...")
    regions_df = pd.read_csv(base_path / "regions_2023-07-17.csv")
    for _, row in regions_df.iterrows():
        region_code = str(row['code']).zfill(2)
        island_group = REGION_TO_ISLAND_GROUP.get(region_code, 'Unknown')
        all_locations.append({
            'location_name': row['name'],
            'location_type': 'Region',
            'code': region_code,
            'parent_code': None,
            'island_group': island_group
        })
    
    # Read provinces
    print("Reading provinces...")
    provinces_df = pd.read_csv(base_path / "provinces_2023-07-17.csv")
    for _, row in provinces_df.iterrows():
        region_code = str(row['region_code']).zfill(2)
        island_group = REGION_TO_ISLAND_GROUP.get(region_code, 'Unknown')
        all_locations.append({
            'location_name': row['name'],
            'location_type': 'Province',
            'code': str(row['code']).zfill(3),
            'parent_code': region_code,
            'island_group': island_group
        })
    
    # Read cities
    print("Reading cities...")
    cities_df = pd.read_csv(base_path / "cities_2023-07-17.csv")
    for _, row in cities_df.iterrows():
        province_code = str(row['province_code']).zfill(3) if 'province_code' in row.index else None
        region_code = str(row['region_code']).zfill(2) if 'region_code' in row.index else 'Unknown'
        
        island_group = REGION_TO_ISLAND_GROUP.get(region_code, 'Unknown')
        all_locations.append({
            'location_name': row['name'],
            'location_type': 'City',
            'code': str(row['code']).zfill(3),
            'parent_code': province_code,
            'island_group': island_group
        })
    
    # Read municipalities
    print("Reading municipalities...")
    municipalities_df = pd.read_csv(base_path / "municipalities_2023-07-17.csv")
    for _, row in municipalities_df.iterrows():
        province_code = str(row['province_code']).zfill(3) if 'province_code' in row.index else None
        region_code = str(row['region_code']).zfill(2) if 'region_code' in row.index else 'Unknown'
        
        island_group = REGION_TO_ISLAND_GROUP.get(region_code, 'Unknown')
        all_locations.append({
            'location_name': row['name'],
            'location_type': 'Municipality',
            'code': str(row['code']).zfill(3),
            'parent_code': province_code,
            'island_group': island_group
        })
    
    # Read barangays
    print("Reading barangays...")
    barangays_df = pd.read_csv(base_path / "barangays_2023-07-17.csv")
    for _, row in barangays_df.iterrows():
        municipality_code = str(row['city_code']).zfill(3) if 'city_code' in row.index else None
        region_code = str(row['region_code']).zfill(2) if 'region_code' in row.index else 'Unknown'
        
        island_group = REGION_TO_ISLAND_GROUP.get(region_code, 'Unknown')
        all_locations.append({
            'location_name': row['name'],
            'location_type': 'Barangay',
            'code': str(row['code']).zfill(4),
            'parent_code': municipality_code,
            'island_group': island_group
        })
    
    # Create DataFrame and save
    consolidated_df = pd.DataFrame(all_locations)
    output_file = output_path / "consolidated_locations.csv"
    consolidated_df.to_csv(output_file, index=False)
    
    print(f"\nConsolidation complete!")
    print(f"Total locations: {len(consolidated_df)}")
    print(f"\nIsland group distribution:")
    print(consolidated_df['island_group'].value_counts())
    print(f"\nOutput saved to: {output_file}")
    
    return consolidated_df

if __name__ == "__main__":
    consolidate_locations()
