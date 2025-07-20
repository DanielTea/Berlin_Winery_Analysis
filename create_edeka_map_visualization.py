#!/usr/bin/env python3
"""
Create an interactive map of Berlin Edeka stores using real map tiles
"""

import pandas as pd
import folium
from folium.plugins import HeatMap
import json

def create_real_berlin_edekas_map():
    """Create an interactive map of Berlin Edeka stores on a real map."""
    
    # Load the Edeka data
    print("Loading Edeka store data...")
    df = pd.read_csv('berlin_edekas.csv')
    
    # Remove rows with missing coordinates
    df_clean = df.dropna(subset=['latitude', 'longitude'])
    print(f"Found {len(df_clean)} Edeka stores with valid coordinates")
    
    # Berlin boundaries
    lat_min, lat_max = 52.3387, 52.6755
    lon_min, lon_max = 13.0883, 13.7611
    
    # Filter data to Berlin area
    df_berlin = df_clean[
        (df_clean['latitude'] >= lat_min) & (df_clean['latitude'] <= lat_max) &
        (df_clean['longitude'] >= lon_min) & (df_clean['longitude'] <= lon_max)
    ]
    
    print(f"Filtered to {len(df_berlin)} Edeka stores within Berlin boundaries")
    
    # Create a Folium map centered on Berlin
    berlin_center = [52.520008, 13.404954]  # Berlin center coordinates
    m = folium.Map(
        location=berlin_center,
        zoom_start=11,
        tiles='OpenStreetMap'
    )
    
    # Add different tile layers for user choice
    folium.TileLayer('cartodbpositron', name='CartoDB Positron', attr='© CartoDB').add_to(m)
    folium.TileLayer('cartodbdark_matter', name='CartoDB Dark', attr='© CartoDB').add_to(m)
    folium.TileLayer('stamenterrain', name='Terrain', attr='© Stamen Design').add_to(m)
    
    # Prepare data for heatmap
    heat_data = [[row['latitude'], row['longitude']] for idx, row in df_berlin.iterrows()]
    
    # Add heatmap layer
    HeatMap(
        heat_data,
        min_opacity=0.2,
        max_zoom=18,
        radius=15,
        blur=10,
        gradient={
            0.0: 'blue',
            0.2: 'cyan', 
            0.4: 'lime',
            0.6: 'yellow',
            0.8: 'orange',
            1.0: 'red'
        }
    ).add_to(m)
    
    # Add individual Edeka markers with clustering for better performance
    from folium.plugins import MarkerCluster
    marker_cluster = MarkerCluster().add_to(m)
    
    # Add markers for each Edeka store
    for idx, row in df_berlin.iterrows():
        # Create popup text with store information
        popup_text = f"""
        <b>{row['name']}</b><br>
        Brand: {row.get('brand', 'N/A')}<br>
        Type: {row.get('shop', 'N/A')}<br>
        Address: {row.get('street', 'N/A')} {row.get('housenumber', '')}<br>
        Postcode: {row.get('postcode', 'N/A')}<br>
        Phone: {row.get('phone', 'N/A')}<br>
        Website: {row.get('website', 'N/A')}<br>
        Hours: {row.get('opening_hours', 'N/A')}<br>
        Wheelchair: {row.get('wheelchair', 'N/A')}<br>
        Parking: {row.get('parking', 'N/A')}
        """
        
        # Determine marker color based on shop type
        if 'supermarket' in str(row.get('shop', '')).lower():
            icon_color = 'blue'
            icon = 'shopping-cart'
        elif 'convenience' in str(row.get('shop', '')).lower():
            icon_color = 'green'
            icon = 'shopping-basket'
        else:
            icon_color = 'orange'
            icon = 'shopping-bag'
        
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=folium.Popup(popup_text, max_width=300),
            tooltip=row['name'],
            icon=folium.Icon(color=icon_color, icon=icon, prefix='fa')
        ).add_to(marker_cluster)
    
    # Add Berlin landmarks for reference
    landmarks = {
        'Brandenburg Gate': [52.5163, 13.3777],
        'TV Tower (Alexanderplatz)': [52.5208, 13.4094],
        'Potsdamer Platz': [52.5096, 13.3759],
        'Berlin Cathedral': [52.5192, 13.4013],
        'Checkpoint Charlie': [52.5074, 13.3904],
        'Berlin Wall Memorial': [52.5354, 13.3889],
        'Charlottenburg Palace': [52.5209, 13.2957]
    }
    
    # Add landmark markers
    for name, coords in landmarks.items():
        folium.Marker(
            location=coords,
            popup=f"<b>{name}</b><br>Famous Berlin Landmark",
            tooltip=name,
            icon=folium.Icon(color='red', icon='star', prefix='fa')
        ).add_to(m)
    
    # Add a layer control to toggle between different views
    folium.LayerControl().add_to(m)
    
    # Add a legend
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 220px; height: 140px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px">
    <b>Berlin Edeka Stores Map</b><br>
    <i class="fa fa-shopping-cart" style="color:blue"></i> Supermarkets<br>
    <i class="fa fa-shopping-basket" style="color:green"></i> Convenience Stores<br>
    <i class="fa fa-shopping-bag" style="color:orange"></i> Other Stores<br>
    <i class="fa fa-star" style="color:red"></i> Landmarks<br>
    <br>
    <b>Heatmap:</b> Blue (low) → Red (high density)
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Save the map
    output_file = 'berlin_edekas_real_map.html'
    m.save(output_file)
    print(f"Interactive map saved as {output_file}")
    
    return m, output_file

def create_density_analysis():
    """Create additional analysis of Edeka store density by district."""
    
    # Load the data
    df = pd.read_csv('berlin_edekas.csv')
    df_clean = df.dropna(subset=['latitude', 'longitude'])
    
    # Berlin district approximations (this is simplified - in reality you'd use proper GIS data)
    districts = {
        'Mitte': {'lat_range': (52.51, 52.54), 'lon_range': (13.37, 13.42)},
        'Charlottenburg': {'lat_range': (52.50, 52.53), 'lon_range': (13.28, 13.33)},
        'Kreuzberg': {'lat_range': (52.49, 52.51), 'lon_range': (13.38, 13.43)},
        'Prenzlauer Berg': {'lat_range': (52.53, 52.56), 'lon_range': (13.40, 13.43)},
        'Friedrichshain': {'lat_range': (52.51, 52.53), 'lon_range': (13.43, 13.47)},
        'Neukölln': {'lat_range': (52.46, 52.49), 'lon_range': (13.43, 13.46)},
        'Schöneberg': {'lat_range': (52.48, 52.50), 'lon_range': (13.35, 13.38)},
        'Wedding': {'lat_range': (52.54, 52.57), 'lon_range': (13.34, 13.38)},
        'Spandau': {'lat_range': (52.53, 52.57), 'lon_range': (13.18, 13.25)},
        'Tempelhof': {'lat_range': (52.46, 52.49), 'lon_range': (13.38, 13.42)},
    }
    
    district_counts = {}
    for district, bounds in districts.items():
        lat_min, lat_max = bounds['lat_range']
        lon_min, lon_max = bounds['lon_range']
        
        count = len(df_clean[
            (df_clean['latitude'] >= lat_min) & (df_clean['latitude'] <= lat_max) &
            (df_clean['longitude'] >= lon_min) & (df_clean['longitude'] <= lon_max)
        ])
        
        district_counts[district] = count
    
    print("\nEdeka store density by district (approximate):")
    for district, count in sorted(district_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"{district}: {count} stores")
    
    return district_counts

def create_postcode_analysis():
    """Analyze Edeka distribution by postcode."""
    
    # Load the data
    df = pd.read_csv('berlin_edekas.csv')
    df_clean = df.dropna(subset=['postcode'])
    
    # Count stores by postcode
    postcode_counts = df_clean['postcode'].value_counts()
    
    print(f"\nEdeka stores by postcode (top 15):")
    for postcode, count in postcode_counts.head(15).items():
        print(f"{postcode}: {count} stores")
    
    return postcode_counts

def create_accessibility_analysis():
    """Analyze wheelchair accessibility of Edeka stores."""
    
    # Load the data
    df = pd.read_csv('berlin_edekas.csv')
    
    # Count wheelchair accessibility
    wheelchair_stats = df['wheelchair'].value_counts()
    total_stores = len(df)
    
    print(f"\nWheelchair accessibility analysis:")
    print(f"Total stores analyzed: {total_stores}")
    
    for status, count in wheelchair_stats.items():
        percentage = (count / total_stores) * 100
        print(f"{status}: {count} stores ({percentage:.1f}%)")
    
    return wheelchair_stats

if __name__ == "__main__":
    print("Creating map visualization of Berlin Edeka stores...")
    
    # Create the interactive map
    map_obj, output_file = create_real_berlin_edekas_map()
    
    # Create various analyses
    district_analysis = create_density_analysis()
    postcode_analysis = create_postcode_analysis()
    accessibility_analysis = create_accessibility_analysis()
    
    print(f"\nVisualization complete!")
    print(f"Open {output_file} in your web browser to view the interactive map.")
    
    # Load and display final statistics
    df = pd.read_csv('berlin_edekas.csv')
    df_clean = df.dropna(subset=['latitude', 'longitude'])
    print(f"Total unique Edeka store locations plotted: {len(df_clean)}")