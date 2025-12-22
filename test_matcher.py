#!/usr/bin/env python
from typhoon_extraction_ml import LocationMatcher

matcher = LocationMatcher()

# Test specific locations from the annotation
test_locations = [
    'Cagayan',
    'Isabela',
    'Metro Manila',
    'Catanduanes',
    'Silvino Lobos',
    'Northern Samar',
    'Leyte',
    'Dinagat Islands',
    'Surigao del Norte',
    'Biliran',
    'Cebu',
    'Iloilo',
]

for loc in test_locations:
    island = matcher.find_island_group(loc)
    print(f"{loc:25} -> {island}")
