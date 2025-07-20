#!/usr/bin/env python3
"""
Create an interactive map of Berlin wineries using real map tiles
"""

import pandas as pd
import folium
from folium.plugins import HeatMap
import json

def create_real_berlin_wineries_map():
    """Create an interactive map of Berlin wineries on a real map."""
    
    # Load the winery data
    print("Loading winery data...")
    df = pd.read_csv('berlin_wineries.csv')
    
    # Remove rows with missing coordinates
    df_clean = df.dropna(subset=['latitude', 'longitude'])
    print(f"Found {len(df_clean)} wineries with valid coordinates")
    
    # Berlin boundaries
    lat_min, lat_max = 52.3387, 52.6755
    lon_min, lon_max = 13.0883, 13.7611
    
    # Filter data to Berlin area
    df_berlin = df_clean[
        (df_clean['latitude'] >= lat_min) & (df_clean['latitude'] <= lat_max) &
        (df_clean['longitude'] >= lon_min) & (df_clean['longitude'] <= lon_max)
    ]
    
    print(f"Filtered to {len(df_berlin)} wineries within Berlin boundaries")
    
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
    
    # Add individual winery markers with clustering for better performance
    from folium.plugins import MarkerCluster
    marker_cluster = MarkerCluster().add_to(m)
    
    # Add markers for each winery
    for idx, row in df_berlin.iterrows():
        # Create popup text with winery information
        popup_text = f"""
        <b>{row['name']}</b><br>
        Type: {row.get('type', 'N/A')}<br>
        Address: {row.get('street', 'N/A')} {row.get('housenumber', '')}<br>
        Postcode: {row.get('postcode', 'N/A')}<br>
        Phone: {row.get('phone', 'N/A')}<br>
        Website: {row.get('website', 'N/A')}<br>
        Hours: {row.get('opening_hours', 'N/A')}
        """
        
        # Determine marker color based on type or amenity
        if 'wine' in str(row.get('shop', '')).lower():
            icon_color = 'red'
            icon = 'wine-glass'
        else:
            icon_color = 'purple'
            icon = 'shopping-cart'
        
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
            icon=folium.Icon(color='green', icon='star', prefix='fa')
        ).add_to(m)
    
    # Add a layer control to toggle between different views
    folium.LayerControl().add_to(m)
    
    # Add a legend
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 200px; height: 120px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px">
    <b>Berlin Wineries Map</b><br>
    <i class="fa fa-wine-glass" style="color:red"></i> Wine Shops<br>
    <i class="fa fa-shopping-cart" style="color:purple"></i> Other Wineries<br>
    <i class="fa fa-star" style="color:green"></i> Landmarks<br>
    <br>
    <b>Heatmap:</b> Blue (low) → Red (high density)
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Save the map
    output_file = 'berlin_wineries_real_map.html'
    m.save(output_file)
    print(f"Interactive map saved as {output_file}")
    
    # Also create a static version using folium's screenshot capability
    try:
        # This requires selenium and a webdriver, but let's try
        import time
        print("Creating static image version...")
        # Note: This might require additional setup for selenium webdriver
        
    except Exception as e:
        print(f"Could not create static image: {e}")
        print("You can still view the interactive HTML map")
    
    return m, output_file

def create_density_analysis():
    """Create additional analysis of winery density by district."""
    
    # Load the data
    df = pd.read_csv('berlin_wineries.csv')
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
    
    print("\nWinery density by district (approximate):")
    for district, count in sorted(district_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"{district}: {count} wineries")
    
    return district_counts

if __name__ == "__main__":
    print("Creating real map visualization of Berlin wineries...")
    
    # Create the interactive map
    map_obj, output_file = create_real_berlin_wineries_map()
    
    # Create density analysis
    district_analysis = create_density_analysis()
    
    print(f"\nVisualization complete!")
    print(f"Open {output_file} in your web browser to view the interactive map.")
    print(f"Total unique winery locations plotted: {len(pd.read_csv('berlin_wineries.csv').dropna(subset=['latitude', 'longitude']))}")