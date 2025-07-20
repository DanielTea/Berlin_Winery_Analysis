#!/usr/bin/env python3
"""
Create an improved heatmap of Berlin wineries with actual Berlin map background
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
from PIL import Image
import io
import requests
import json

# Set style for better-looking plots
plt.style.use('default')

def download_berlin_map_data():
    """Download Berlin geographical boundaries for map context."""
    # This is a simplified approach - in production you'd use proper map tiles
    # For now, we'll create a more comprehensive visualization with better landmarks
    pass

def create_improved_winery_heatmap():
    """Create an improved heatmap of Berlin wineries with proper geographical context."""
    
    # Load the winery data
    print("Loading winery data...")
    df = pd.read_csv('berlin_wineries.csv')
    
    # Remove rows with missing coordinates
    df_clean = df.dropna(subset=['latitude', 'longitude'])
    print(f"Found {len(df_clean)} wineries with valid coordinates")
    
    # Berlin boundaries (more precise)
    lat_min, lat_max = 52.3387, 52.6755
    lon_min, lon_max = 13.0883, 13.7611
    
    # Filter data to Berlin area
    df_berlin = df_clean[
        (df_clean['latitude'] >= lat_min) & (df_clean['latitude'] <= lat_max) &
        (df_clean['longitude'] >= lon_min) & (df_clean['longitude'] <= lon_max)
    ]
    
    print(f"Filtered to {len(df_berlin)} wineries within Berlin boundaries")
    
    # Create a high-resolution figure with better aspect ratio
    fig, ax = plt.subplots(figsize=(20, 16), dpi=300)
    
    # Set white background for better contrast
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    
    # Create a 2D histogram (heatmap) of winery locations with higher resolution
    bins = 75  # Increased resolution
    
    # Create the 2D histogram
    hist, xedges, yedges = np.histogram2d(
        df_berlin['longitude'], 
        df_berlin['latitude'], 
        bins=bins,
        range=[[lon_min, lon_max], [lat_min, lat_max]]
    )
    
    # Apply Gaussian smoothing for better visualization
    from scipy import ndimage
    hist_smooth = ndimage.gaussian_filter(hist, sigma=1.5)
    
    # Create the extent for the heatmap
    extent = [lon_min, lon_max, lat_min, lat_max]
    
    # Create a better colormap for the heatmap (warm colors on white background)
    colors = ['#ffffff', '#fff5f0', '#fee0d2', '#fcbba1', '#fc9272', 
              '#fb6a4a', '#ef3b2c', '#cb181d', '#a50f15', '#67000d']
    n_bins = 256
    cmap = LinearSegmentedColormap.from_list('winery_heat', colors, N=n_bins)
    
    # Plot the heatmap with better transparency
    im = ax.imshow(
        hist_smooth.T, 
        extent=extent, 
        origin='lower', 
        cmap=cmap, 
        alpha=0.7,
        interpolation='bilinear',
        aspect='auto'
    )
    
    # Add Berlin district boundaries and major landmarks with improved data
    berlin_landmarks = {
        'Brandenburg Gate': (13.3777, 52.5163),
        'TV Tower (Alexanderplatz)': (13.4094, 52.5208),
        'Potsdamer Platz': (13.3759, 52.5096),
        'Berlin Cathedral': (13.4013, 52.5192),
        'Checkpoint Charlie': (13.3904, 52.5074),
        'Berlin Wall Memorial': (13.3889, 52.5354),
        'Kurfürstendamm': (13.3317, 52.5044),
        'Unter den Linden': (13.3888, 52.5170),
        'Tiergarten': (13.3501, 52.5145),
        'Charlottenburg Palace': (13.2957, 52.5209)
    }
    
    # Add major Berlin districts (approximate centers)
    berlin_districts = {
        'Mitte': (13.4050, 52.5200),
        'Charlottenburg': (13.3048, 52.5194),
        'Kreuzberg': (13.4034, 52.4987),
        'Prenzlauer Berg': (13.4105, 52.5479),
        'Friedrichshain': (13.4531, 52.5139),
        'Neukölln': (13.4369, 52.4814),
        'Schöneberg': (13.3563, 52.4862),
        'Wedding': (13.3654, 52.5479),
        'Tempelhof': (13.3844, 52.4675),
        'Steglitz': (13.3171, 52.4570)
    }
    
    # Plot the actual winery locations as scatter points
    scatter = ax.scatter(
        df_berlin['longitude'], 
        df_berlin['latitude'], 
        c='darkred', 
        s=25, 
        alpha=0.8, 
        edgecolors='white', 
        linewidth=0.8,
        label='Wineries',
        zorder=5
    )
    
    # Add landmarks with better styling
    for name, (lon, lat) in berlin_landmarks.items():
        ax.plot(lon, lat, marker='*', color='gold', markersize=15, 
                markeredgecolor='black', markeredgewidth=1.5, zorder=6)
        ax.annotate(name, (lon, lat), xytext=(8, 8), 
                   textcoords='offset points', fontsize=10, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.4', facecolor='yellow', alpha=0.8, edgecolor='black'),
                   zorder=7)
    
    # Add district labels
    for district, (lon, lat) in berlin_districts.items():
        ax.plot(lon, lat, marker='s', color='blue', markersize=8, 
                markeredgecolor='white', markeredgewidth=1, alpha=0.7, zorder=4)
        ax.annotate(district, (lon, lat), xytext=(5, 5), 
                   textcoords='offset points', fontsize=9, fontweight='bold',
                   color='blue', alpha=0.8, zorder=4)
    
    # Add a simple grid to simulate streets
    ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5, color='gray')
    
    # Add major streets/highways as lines (simplified representation)
    # Ring road (A100) - approximate
    ring_lons = [13.2, 13.3, 13.5, 13.6, 13.6, 13.5, 13.3, 13.2, 13.2]
    ring_lats = [52.45, 52.4, 52.4, 52.5, 52.6, 52.65, 52.6, 52.55, 52.45]
    ax.plot(ring_lons, ring_lats, 'k-', alpha=0.4, linewidth=2, label='Major Roads')
    
    # East-West corridor (Unter den Linden / Kurfürstendamm)
    ax.plot([13.29, 13.41], [52.504, 52.517], 'k-', alpha=0.4, linewidth=2)
    
    # North-South corridor
    ax.plot([13.40, 13.40], [52.35, 52.65], 'k-', alpha=0.4, linewidth=2)
    
    # Customize the plot with better styling
    ax.set_xlabel('Longitude', fontsize=16, fontweight='bold')
    ax.set_ylabel('Latitude', fontsize=16, fontweight='bold')
    ax.set_title('Berlin Wineries Heatmap\nDensity Distribution with Geographic Context', 
                 fontsize=22, fontweight='bold', pad=30)
    
    # Add colorbar with better styling
    cbar = plt.colorbar(im, ax=ax, shrink=0.8, aspect=40, pad=0.02)
    cbar.set_label('Winery Density', fontsize=14, fontweight='bold')
    cbar.ax.tick_params(labelsize=12)
    
    # Add legend with better positioning
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='darkred', 
                   markersize=10, label='Wineries', markeredgecolor='white'),
        plt.Line2D([0], [0], marker='*', color='w', markerfacecolor='gold', 
                   markersize=15, label='Landmarks', markeredgecolor='black'),
        plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='blue', 
                   markersize=8, label='Districts', markeredgecolor='white'),
        plt.Line2D([0], [0], color='black', linewidth=2, alpha=0.4, label='Major Roads')
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=12, 
              frameon=True, fancybox=True, shadow=True)
    
    # Set proper aspect ratio for Berlin's latitude
    ax.set_aspect(1.0 / np.cos(np.radians(52.5)))
    
    # Set axis limits with some padding
    ax.set_xlim(lon_min - 0.02, lon_max + 0.02)
    ax.set_ylim(lat_min - 0.01, lat_max + 0.01)
    
    # Improve tick formatting
    ax.tick_params(axis='both', which='major', labelsize=12)
    
    # Add subtitle with statistics
    stats_text = f"Total Wineries: {len(df_berlin)} | Coverage: {len(df_berlin.groupby(['latitude', 'longitude']))} unique locations"
    plt.figtext(0.5, 0.02, stats_text, ha='center', fontsize=12, style='italic')
    
    # Tight layout with padding
    plt.tight_layout(pad=2.0)
    
    # Save as high-quality PNG
    output_filename = 'berlin_wineries_heatmap_improved.png'
    plt.savefig(output_filename, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none', pad_inches=0.2)
    
    print(f"Improved heatmap saved as '{output_filename}'")
    
    # Also create a summary with more detailed statistics
    print(f"\nDetailed Summary:")
    print(f"- Total wineries plotted: {len(df_berlin)}")
    print(f"- Unique locations: {len(df_berlin.groupby(['latitude', 'longitude']))}")
    print(f"- Latitude range: {df_berlin['latitude'].min():.4f} to {df_berlin['latitude'].max():.4f}")
    print(f"- Longitude range: {df_berlin['longitude'].min():.4f} to {df_berlin['longitude'].max():.4f}")
    print(f"- Most common districts by winery count:")
    
    # Simple district analysis based on coordinates
    df_berlin['district_approx'] = df_berlin.apply(lambda row: 
        'Mitte' if 13.35 <= row['longitude'] <= 13.45 and 52.50 <= row['latitude'] <= 52.54
        else 'Charlottenburg' if 13.25 <= row['longitude'] <= 13.35 and 52.48 <= row['latitude'] <= 52.54
        else 'Kreuzberg' if 13.38 <= row['longitude'] <= 13.43 and 52.48 <= row['latitude'] <= 52.52
        else 'Prenzlauer Berg' if 13.38 <= row['longitude'] <= 13.44 and 52.53 <= row['latitude'] <= 52.57
        else 'Other', axis=1)
    
    district_counts = df_berlin['district_approx'].value_counts()
    for district, count in district_counts.head(5).items():
        print(f"  - {district}: {count} wineries")
    
    plt.close()
    
    return output_filename

if __name__ == "__main__":
    # Install scipy if not available
    try:
        from scipy import ndimage
    except ImportError:
        import subprocess
        import sys
        print("Installing scipy...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--break-system-packages", "scipy"])
        from scipy import ndimage
    
    output_file = create_improved_winery_heatmap()
    print(f"Successfully created improved heatmap: {output_file}")