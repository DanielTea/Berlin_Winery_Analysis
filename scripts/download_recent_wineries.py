#!/usr/bin/env python3
"""
Download Berlin wineries with temporal data to identify recently opened establishments
"""

import requests
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any
import time

def get_berlin_wineries_with_dates():
    """Download winery data from OpenStreetMap with temporal information."""
    
    overpass_url = "http://overpass-api.de/api/interpreter"
    
    # Enhanced Overpass query to get temporal metadata
    overpass_query = """
    [out:json][timeout:30];
    (
      area["ISO3166-1"="DE"]["admin_level"="2"];
      area(pivot)["name"="Berlin"]["admin_level"="4"];
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
    
    print("Querying Overpass API for wineries in Berlin with temporal data...")
    
    try:
        response = requests.post(overpass_url, data=overpass_query, timeout=60)
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
            
            # Extract temporal metadata
            timestamp = element.get('timestamp', '')
            version = element.get('version', 1)
            changeset = element.get('changeset', '')
            
            # Parse timestamp
            created_date = None
            if timestamp:
                try:
                    created_date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                except:
                    pass
            
            # Create winery entry with temporal data
            winery = {
                'id': element.get('id'),
                'type': element.get('type'),
                'name': tags.get('name', 'Unknown'),
                'latitude': lat,
                'longitude': lon,
                'amenity': tags.get('amenity', ''),
                'shop': tags.get('shop', ''),
                'craft': tags.get('craft', ''),
                'street': tags.get('addr:street', ''),
                'housenumber': tags.get('addr:housenumber', ''),
                'postcode': tags.get('addr:postcode', ''),
                'city': tags.get('addr:city', ''),
                'phone': tags.get('phone', ''),
                'website': tags.get('website', ''),
                'email': tags.get('email', ''),
                'opening_hours': tags.get('opening_hours', ''),
                'description': tags.get('description', ''),
                'start_date': tags.get('start_date', ''),  # Explicit opening date if available
                'opening_date': tags.get('opening_date', ''),  # Alternative opening date field
                'osm_timestamp': timestamp,  # When the OSM object was created/modified
                'osm_version': version,  # Version number (higher = more recent edits)
                'osm_changeset': changeset,
                'created_date': created_date.isoformat() if created_date else '',
                'district': '',  # Will be filled by geocoding
            }
            
            wineries.append(winery)
        
        print(f"Found {len(wineries)} wine-related establishments in Berlin")
        return wineries
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading data: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        return []

def classify_by_recency(wineries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Classify wineries by how recently they were added/opened."""
    
    current_date = datetime.now()
    two_years_ago = current_date - timedelta(days=730)
    one_year_ago = current_date - timedelta(days=365)
    
    for winery in wineries:
        recency_score = 0
        recency_category = "unknown"
        
        # Check explicit opening dates first
        opening_date = None
        if winery.get('start_date'):
            try:
                opening_date = datetime.fromisoformat(winery['start_date'])
            except:
                pass
        elif winery.get('opening_date'):
            try:
                opening_date = datetime.fromisoformat(winery['opening_date'])
            except:
                pass
        
        # If we have an explicit opening date, use that
        if opening_date:
            if opening_date >= two_years_ago:
                if opening_date >= one_year_ago:
                    recency_score = 10  # Very recent (< 1 year)
                    recency_category = "very_recent"
                else:
                    recency_score = 8   # Recent (1-2 years)
                    recency_category = "recent"
            else:
                recency_score = 2       # Older
                recency_category = "established"
        else:
            # Fall back to OSM metadata
            if winery.get('created_date'):
                try:
                    osm_date = datetime.fromisoformat(winery['created_date'])
                    if osm_date >= two_years_ago:
                        if osm_date >= one_year_ago:
                            recency_score = 7   # Likely recent (based on OSM data)
                            recency_category = "likely_recent"
                        else:
                            recency_score = 5   # Possibly recent
                            recency_category = "possibly_recent"
                    else:
                        recency_score = 1       # OSM entry is old
                        recency_category = "established"
                except:
                    pass
            
            # Additional scoring based on version number (more edits = potentially more recent changes)
            version = winery.get('osm_version', 1)
            if version > 5:
                recency_score += 2  # Frequently updated
            elif version > 2:
                recency_score += 1  # Some updates
        
        winery['recency_score'] = recency_score
        winery['recency_category'] = recency_category
        winery['is_recent'] = recency_score >= 5  # Consider recent if score >= 5
    
    return wineries

def add_district_info(wineries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Add district information based on coordinates."""
    
    # Berlin district boundaries (approximate)
    districts = {
        'Mitte': {'lat_min': 52.50, 'lat_max': 52.55, 'lon_min': 13.35, 'lon_max': 13.42},
        'Prenzlauer Berg': {'lat_min': 52.52, 'lat_max': 52.56, 'lon_min': 13.40, 'lon_max': 13.45},
        'Charlottenburg': {'lat_min': 52.49, 'lat_max': 52.53, 'lon_min': 13.28, 'lon_max': 13.35},
        'Kreuzberg': {'lat_min': 52.49, 'lat_max': 52.52, 'lon_min': 13.38, 'lon_max': 13.42},
        'Neukölln': {'lat_min': 52.45, 'lat_max': 52.50, 'lon_min': 13.40, 'lon_max': 13.47},
        'Friedrichshain': {'lat_min': 52.50, 'lat_max': 52.53, 'lon_min': 13.42, 'lon_max': 13.48},
        'Schöneberg': {'lat_min': 52.46, 'lat_max': 52.50, 'lon_min': 13.33, 'lon_max': 13.38},
        'Wedding': {'lat_min': 52.53, 'lat_max': 52.57, 'lon_min': 13.33, 'lon_max': 13.38},
        'Tempelhof': {'lat_min': 52.45, 'lat_max': 52.49, 'lon_min': 13.38, 'lon_max': 13.42},
        'Steglitz': {'lat_min': 52.44, 'lat_max': 52.48, 'lon_min': 13.31, 'lon_max': 13.36},
    }
    
    for winery in wineries:
        lat = winery.get('latitude')
        lon = winery.get('longitude')
        
        if lat and lon:
            district_found = False
            for district_name, bounds in districts.items():
                if (bounds['lat_min'] <= lat <= bounds['lat_max'] and 
                    bounds['lon_min'] <= lon <= bounds['lon_max']):
                    winery['district'] = district_name
                    district_found = True
                    break
            
            if not district_found:
                winery['district'] = 'Other'
    
    return wineries

def save_recent_wineries_data(wineries: List[Dict[str, Any]]) -> None:
    """Save winery data with temporal analysis."""
    
    # Save to JSON
    json_filename = "../data/berlin_wineries_recent.json"
    try:
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(wineries, f, indent=2, ensure_ascii=False)
        print(f"Data saved to {json_filename}")
    except Exception as e:
        print(f"Error saving to JSON: {e}")
    
    # Save to CSV
    csv_filename = "../data/berlin_wineries_recent.csv"
    try:
        df = pd.DataFrame(wineries)
        df.to_csv(csv_filename, index=False, encoding='utf-8')
        print(f"Data saved to {csv_filename}")
    except Exception as e:
        print(f"Error saving to CSV: {e}")

def analyze_recent_trends(wineries: List[Dict[str, Any]]) -> None:
    """Analyze and report on recent winery trends."""
    
    print("\n=== TEMPORAL ANALYSIS ===")
    
    # Count by recency category
    recency_counts = {}
    district_recent_counts = {}
    
    for winery in wineries:
        category = winery.get('recency_category', 'unknown')
        district = winery.get('district', 'Unknown')
        
        recency_counts[category] = recency_counts.get(category, 0) + 1
        
        if winery.get('is_recent', False):
            district_recent_counts[district] = district_recent_counts.get(district, 0) + 1
    
    print("\nRecency Distribution:")
    for category, count in sorted(recency_counts.items()):
        print(f"  {category}: {count}")
    
    print(f"\nRecent Wineries by District (last 2 years):")
    sorted_districts = sorted(district_recent_counts.items(), key=lambda x: x[1], reverse=True)
    for district, count in sorted_districts:
        print(f"  {district}: {count} recent wineries")
    
    # Show some examples of recent wineries
    recent_wineries = [w for w in wineries if w.get('is_recent', False)]
    if recent_wineries:
        print(f"\nSample recent wineries ({len(recent_wineries)} total):")
        for i, winery in enumerate(recent_wineries[:5]):
            print(f"  {i+1}. {winery['name']} ({winery['district']})")
            if winery.get('start_date'):
                print(f"     Opening date: {winery['start_date']}")
            elif winery.get('osm_timestamp'):
                print(f"     OSM added: {winery['osm_timestamp'][:10]}")
            print(f"     Recency score: {winery['recency_score']}")

def main():
    """Main function to download and analyze recent winery data."""
    print("Berlin Recent Wineries Analyzer")
    print("=" * 40)
    
    # Download data
    wineries = get_berlin_wineries_with_dates()
    
    if not wineries:
        print("No winery data retrieved. Exiting.")
        return
    
    # Add temporal classification
    wineries = classify_by_recency(wineries)
    
    # Add district information
    wineries = add_district_info(wineries)
    
    # Save data
    save_recent_wineries_data(wineries)
    
    # Analyze trends
    analyze_recent_trends(wineries)
    
    print(f"\nAnalysis complete! Data saved to:")
    print("- ../data/berlin_wineries_recent.json")
    print("- ../data/berlin_wineries_recent.csv")

if __name__ == "__main__":
    main() 