#!/usr/bin/env python3
"""
Script to download the locations of all wineries in Berlin using OpenStreetMap data.
Uses the Overpass API to query for wineries and wine shops in Berlin.
"""

import requests
import json
import csv
import time
from typing import List, Dict, Any

def get_berlin_wineries() -> List[Dict[str, Any]]:
    """
    Query Overpass API for wineries and wine-related businesses in Berlin.
    Returns a list of dictionaries containing location data.
    """
    # Overpass API endpoint
    overpass_url = "http://overpass-api.de/api/interpreter"
    
    # Overpass QL query for wineries and wine shops in Berlin
    # This searches for:
    # - Amenities tagged as "bar" with wine specialization
    # - Shops tagged as "wine" 
    # - Any amenity tagged as "winery"
    # - Craft businesses that are wineries
    overpass_query = """
    [out:json][timeout:25];
    (
      area["name"="Berlin"]["admin_level"="4"];
    )->.searchArea;
    (
      node["amenity"="bar"]["drink:wine"="yes"](area.searchArea);
      node["shop"="wine"](area.searchArea);
      node["amenity"="winery"](area.searchArea);
      node["craft"="winery"](area.searchArea);
      way["amenity"="bar"]["drink:wine"="yes"](area.searchArea);
      way["shop"="wine"](area.searchArea);
      way["amenity"="winery"](area.searchArea);
      way["craft"="winery"](area.searchArea);
      relation["amenity"="bar"]["drink:wine"="yes"](area.searchArea);
      relation["shop"="wine"](area.searchArea);
      relation["amenity"="winery"](area.searchArea);
      relation["craft"="winery"](area.searchArea);
    );
    out center meta;
    """
    
    print("Querying Overpass API for wineries in Berlin...")
    
    try:
        response = requests.post(overpass_url, data=overpass_query, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        wineries = []
        
        for element in data.get('elements', []):
            # Extract coordinates
            if element['type'] == 'node':
                lat = element.get('lat')
                lon = element.get('lon')
            elif 'center' in element:
                lat = element['center'].get('lat')
                lon = element['center'].get('lon')
            else:
                continue
                
            # Extract tags
            tags = element.get('tags', {})
            
            # Create winery entry
            winery = {
                'id': element.get('id'),
                'type': element.get('type'),
                'name': tags.get('name', 'Unknown'),
                'latitude': lat,
                'longitude': lon,
                'amenity': tags.get('amenity', ''),
                'shop': tags.get('shop', ''),
                'craft': tags.get('craft', ''),
                'address': {
                    'street': tags.get('addr:street', ''),
                    'housenumber': tags.get('addr:housenumber', ''),
                    'postcode': tags.get('addr:postcode', ''),
                    'city': tags.get('addr:city', ''),
                },
                'contact': {
                    'phone': tags.get('phone', ''),
                    'website': tags.get('website', ''),
                    'email': tags.get('email', ''),
                },
                'opening_hours': tags.get('opening_hours', ''),
                'description': tags.get('description', ''),
                'wine_types': tags.get('drink:wine', ''),
                'all_tags': tags
            }
            
            wineries.append(winery)
        
        print(f"Found {len(wineries)} wine-related establishments in Berlin")
        return wineries
        
    except requests.RequestException as e:
        print(f"Error querying Overpass API: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        return []

def save_to_json(wineries: List[Dict[str, Any]], filename: str = "berlin_wineries.json") -> None:
    """Save winery data to JSON file."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(wineries, f, indent=2, ensure_ascii=False)
        print(f"Data saved to {filename}")
    except Exception as e:
        print(f"Error saving to JSON: {e}")

def save_to_csv(wineries: List[Dict[str, Any]], filename: str = "berlin_wineries.csv") -> None:
    """Save winery data to CSV file."""
    if not wineries:
        print("No data to save to CSV")
        return
        
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'id', 'type', 'name', 'latitude', 'longitude', 
                'amenity', 'shop', 'craft', 'street', 'housenumber', 
                'postcode', 'city', 'phone', 'website', 'email', 
                'opening_hours', 'description'
            ]
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for winery in wineries:
                row = {
                    'id': winery['id'],
                    'type': winery['type'],
                    'name': winery['name'],
                    'latitude': winery['latitude'],
                    'longitude': winery['longitude'],
                    'amenity': winery['amenity'],
                    'shop': winery['shop'],
                    'craft': winery['craft'],
                    'street': winery['address']['street'],
                    'housenumber': winery['address']['housenumber'],
                    'postcode': winery['address']['postcode'],
                    'city': winery['address']['city'],
                    'phone': winery['contact']['phone'],
                    'website': winery['contact']['website'],
                    'email': winery['contact']['email'],
                    'opening_hours': winery['opening_hours'],
                    'description': winery['description']
                }
                writer.writerow(row)
                
        print(f"Data saved to {filename}")
    except Exception as e:
        print(f"Error saving to CSV: {e}")

def print_summary(wineries: List[Dict[str, Any]]) -> None:
    """Print a summary of the downloaded data."""
    if not wineries:
        print("No wineries found.")
        return
        
    print(f"\n=== SUMMARY ===")
    print(f"Total establishments found: {len(wineries)}")
    
    # Count by type
    types = {}
    for winery in wineries:
        if winery['amenity']:
            key = f"amenity={winery['amenity']}"
        elif winery['shop']:
            key = f"shop={winery['shop']}"
        elif winery['craft']:
            key = f"craft={winery['craft']}"
        else:
            key = "other"
        types[key] = types.get(key, 0) + 1
    
    print("\nBreakdown by type:")
    for type_name, count in sorted(types.items()):
        print(f"  {type_name}: {count}")
    
    # Show some examples
    print(f"\nSample entries:")
    for i, winery in enumerate(wineries[:3]):
        print(f"  {i+1}. {winery['name']}")
        if winery['address']['street']:
            addr = f"{winery['address']['street']} {winery['address']['housenumber']}".strip()
            print(f"     Address: {addr}")
        print(f"     Coordinates: {winery['latitude']}, {winery['longitude']}")
        if winery['contact']['website']:
            print(f"     Website: {winery['contact']['website']}")
        print()

def main():
    """Main function to download and save winery data."""
    print("Berlin Wineries Downloader")
    print("=" * 30)
    
    # Download winery data
    wineries = get_berlin_wineries()
    
    if not wineries:
        print("No winery data retrieved. Exiting.")
        return
    
    # Save data in multiple formats
    save_to_json(wineries)
    save_to_csv(wineries)
    
    # Print summary
    print_summary(wineries)
    
    print("\nDownload complete! Check the generated files:")
    print("- berlin_wineries.json (JSON format)")
    print("- berlin_wineries.csv (CSV format)")

if __name__ == "__main__":
    main()