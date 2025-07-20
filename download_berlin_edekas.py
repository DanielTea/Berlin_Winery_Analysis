#!/usr/bin/env python3
"""
Script to download the locations of all Edeka stores in Berlin using OpenStreetMap data.
Uses the Overpass API to query for Edeka supermarkets in Berlin.
"""

import requests
import json
import csv
import time
from typing import List, Dict, Any

def get_berlin_edekas() -> List[Dict[str, Any]]:
    """
    Query Overpass API for Edeka stores in Berlin.
    Returns a list of dictionaries containing location data.
    """
    # Overpass API endpoint
    overpass_url = "http://overpass-api.de/api/interpreter"
    
    # Overpass QL query for Edeka stores in Berlin - simplified for better performance
    # This searches for shops with Edeka in the name or brand
    overpass_query = """
    [out:json][timeout:60];
    (
      area["name"="Berlin"]["admin_level"="4"];
    )->.searchArea;
    (
      node["shop"="supermarket"]["brand"="Edeka"](area.searchArea);
      node["shop"="supermarket"]["name"~"Edeka"](area.searchArea);
      way["shop"="supermarket"]["brand"="Edeka"](area.searchArea);
      way["shop"="supermarket"]["name"~"Edeka"](area.searchArea);
    );
    out center meta;
    """
    
    print("Querying Overpass API for Edeka stores in Berlin...")
    
    try:
        response = requests.post(overpass_url, data=overpass_query, timeout=90)
        response.raise_for_status()
        data = response.json()
        
        edekas = []
        
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
            
            # Create edeka entry
            edeka = {
                'id': element.get('id'),
                'type': element.get('type'),
                'name': tags.get('name', 'Unknown'),
                'brand': tags.get('brand', ''),
                'latitude': lat,
                'longitude': lon,
                'shop': tags.get('shop', ''),
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
                'operator': tags.get('operator', ''),
                'wheelchair': tags.get('wheelchair', ''),
                'parking': tags.get('parking', ''),
                'all_tags': tags
            }
            
            edekas.append(edeka)
        
        print(f"Found {len(edekas)} Edeka stores in Berlin")
        return edekas
        
    except requests.RequestException as e:
        print(f"Error querying Overpass API: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        return []

def save_to_json(edekas: List[Dict[str, Any]], filename: str = "berlin_edekas.json") -> None:
    """Save Edeka data to JSON file."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(edekas, f, indent=2, ensure_ascii=False)
        print(f"Data saved to {filename}")
    except Exception as e:
        print(f"Error saving to JSON: {e}")

def save_to_csv(edekas: List[Dict[str, Any]], filename: str = "berlin_edekas.csv") -> None:
    """Save Edeka data to CSV file."""
    if not edekas:
        print("No data to save to CSV")
        return
        
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'id', 'type', 'name', 'brand', 'latitude', 'longitude', 
                'shop', 'street', 'housenumber', 'postcode', 'city', 
                'phone', 'website', 'email', 'opening_hours', 'description',
                'operator', 'wheelchair', 'parking'
            ]
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for edeka in edekas:
                row = {
                    'id': edeka['id'],
                    'type': edeka['type'],
                    'name': edeka['name'],
                    'brand': edeka['brand'],
                    'latitude': edeka['latitude'],
                    'longitude': edeka['longitude'],
                    'shop': edeka['shop'],
                    'street': edeka['address']['street'],
                    'housenumber': edeka['address']['housenumber'],
                    'postcode': edeka['address']['postcode'],
                    'city': edeka['address']['city'],
                    'phone': edeka['contact']['phone'],
                    'website': edeka['contact']['website'],
                    'email': edeka['contact']['email'],
                    'opening_hours': edeka['opening_hours'],
                    'description': edeka['description'],
                    'operator': edeka['operator'],
                    'wheelchair': edeka['wheelchair'],
                    'parking': edeka['parking']
                }
                writer.writerow(row)
                
        print(f"Data saved to {filename}")
    except Exception as e:
        print(f"Error saving to CSV: {e}")

def print_summary(edekas: List[Dict[str, Any]]) -> None:
    """Print a summary of the downloaded data."""
    if not edekas:
        print("No Edeka stores found.")
        return
        
    print(f"\n=== SUMMARY ===")
    print(f"Total Edeka stores found: {len(edekas)}")
    
    # Count by shop type
    shop_types = {}
    for edeka in edekas:
        shop_type = edeka['shop'] or 'other'
        shop_types[shop_type] = shop_types.get(shop_type, 0) + 1
    
    print("\nBreakdown by shop type:")
    for shop_type, count in sorted(shop_types.items()):
        print(f"  {shop_type}: {count}")
    
    # Count by district (based on postcode)
    districts = {}
    for edeka in edekas:
        postcode = edeka['address']['postcode']
        if postcode and len(postcode) >= 5:
            district = postcode[:5]
            districts[district] = districts.get(district, 0) + 1
    
    print("\nTop districts by postcode:")
    for district, count in sorted(districts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {district}: {count} stores")
    
    # Show some examples
    print(f"\nSample entries:")
    for i, edeka in enumerate(edekas[:3]):
        print(f"  {i+1}. {edeka['name']}")
        if edeka['address']['street']:
            addr = f"{edeka['address']['street']} {edeka['address']['housenumber']}".strip()
            print(f"     Address: {addr}")
        if edeka['address']['postcode']:
            print(f"     Postcode: {edeka['address']['postcode']}")
        print(f"     Coordinates: {edeka['latitude']}, {edeka['longitude']}")
        if edeka['opening_hours']:
            print(f"     Hours: {edeka['opening_hours']}")
        print()

def main():
    """Main function to download and save Edeka data."""
    print("Berlin Edeka Stores Downloader")
    print("=" * 35)
    
    # Download Edeka data
    edekas = get_berlin_edekas()
    
    if not edekas:
        print("No Edeka data retrieved. Exiting.")
        return
    
    # Save data in multiple formats
    save_to_json(edekas)
    save_to_csv(edekas)
    
    # Print summary
    print_summary(edekas)
    
    print("\nDownload complete! Check the generated files:")
    print("- berlin_edekas.json (JSON format)")
    print("- berlin_edekas.csv (CSV format)")

if __name__ == "__main__":
    main()