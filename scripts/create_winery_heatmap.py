#!/usr/bin/env python3
"""
Create a heatmap of Berlin wineries on a map and save as PNG
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
from PIL import Image
import io
import requests
from scipy import ndimage

# Set style for better-looking plots
plt.style.use('default')
sns.set_palette("viridis")

def create_winery_heatmap():
    """Create a heatmap of Berlin wineries and save as PNG."""
    
    # Load the winery data
    print("Loading winery data...")
    df = pd.read_csv('../data/berlin_wineries.csv')
    
    # Remove rows with missing coordinates
    df_clean = df.dropna(subset=['latitude', 'longitude'])
    print(f"Found {len(df_clean)} wineries with valid coordinates")
    
    # Berlin boundaries (approximate)
    lat_min, lat_max = 52.3, 52.7
    lon_min, lon_max = 13.0, 13.8
    
    # Filter data to Berlin area
    df_berlin = df_clean[
        (df_clean['latitude'] >= lat_min) & (df_clean['latitude'] <= lat_max) &
        (df_clean['longitude'] >= lon_min) & (df_clean['longitude'] <= lon_max)
    ]
    
    print(f"Filtered to {len(df_berlin)} wineries within Berlin boundaries")
    
    # Create a high-resolution figure
    fig, ax = plt.subplots(figsize=(16, 12), dpi=300)
    
    # Create a 2D histogram (heatmap) of winery locations
    # Higher bins for better resolution
    bins = 50
    
    # Create the 2D histogram
    hist, xedges, yedges = np.histogram2d(
        df_berlin['longitude'], 
        df_berlin['latitude'], 
        bins=bins,
        range=[[lon_min, lon_max], [lat_min, lat_max]]
    )
    
    # Apply Gaussian smoothing for better visualization
    from scipy import ndimage
    hist_smooth = ndimage.gaussian_filter(hist, sigma=1.0)
    
    # Create the heatmap
    extent = [lon_min, lon_max, lat_min, lat_max]
    
    # Use a custom colormap
    colors = ['#000033', '#000055', '#000077', '#0000BB', '#0000FF', 
              '#3333FF', '#6666FF', '#9999FF', '#CCCCFF', '#FFFFFF',
              '#FFCCCC', '#FF9999', '#FF6666', '#FF3333', '#FF0000',
              '#CC0000', '#990000', '#660000']
    n_bins = 100
    cmap = LinearSegmentedColormap.from_list('winery_heat', colors, N=n_bins)
    
    # Plot the heatmap
    im = ax.imshow(
        hist_smooth.T, 
        extent=extent, 
        origin='lower', 
        cmap=cmap, 
        alpha=0.8,
        interpolation='bilinear'
    )
    
    # Overlay the actual winery locations as points
    scatter = ax.scatter(
        df_berlin['longitude'], 
        df_berlin['latitude'], 
        c='white', 
        s=15, 
        alpha=0.9, 
        edgecolors='black', 
        linewidth=0.5,
        label='Wineries'
    )
    
    # Customize the plot
    ax.set_xlabel('Longitude', fontsize=14, fontweight='bold')
    ax.set_ylabel('Latitude', fontsize=14, fontweight='bold')
    ax.set_title('Berlin Wineries Heatmap\nDensity Distribution of Wine Shops and Stores', 
                 fontsize=18, fontweight='bold', pad=20)
    
    # Add grid
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, shrink=0.8, aspect=30)
    cbar.set_label('Winery Density', fontsize=12, fontweight='bold')
    cbar.ax.tick_params(labelsize=10)
    
    # Add legend
    ax.legend(loc='upper right', fontsize=12)
    
    # Add some key Berlin landmarks for reference (approximate coordinates)
    landmarks = {
        'Brandenburg Gate': (13.3777, 52.5163),
        'TV Tower': (13.4094, 52.5208),
        'Potsdamer Platz': (13.3759, 52.5096)
    }
    
    for name, (lon, lat) in landmarks.items():
        ax.plot(lon, lat, marker='*', color='gold', markersize=12, 
                markeredgecolor='black', markeredgewidth=1)
        ax.annotate(name, (lon, lat), xytext=(5, 5), 
                   textcoords='offset points', fontsize=10, 
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
    
    # Set aspect ratio to be approximately correct for Berlin's latitude
    ax.set_aspect(1.0 / np.cos(np.radians(52.5)))
    
    # Tight layout
    plt.tight_layout()
    
    # Save as high-quality PNG
    output_filename = '../outputs/berlin_wineries_heatmap.png'
    plt.savefig(output_filename, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    print(f"Heatmap saved as '{output_filename}'")
    
    # Also create a summary
    print(f"\nSummary:")
    print(f"- Total wineries plotted: {len(df_berlin)}")
    print(f"- Latitude range: {df_berlin['latitude'].min():.4f} to {df_berlin['latitude'].max():.4f}")
    print(f"- Longitude range: {df_berlin['longitude'].min():.4f} to {df_berlin['longitude'].max():.4f}")
    
    # Show the plot (won't display in headless mode, but good for debugging)
    # plt.show()
    
    plt.close()
    
    return output_filename

if __name__ == "__main__":
    output_file = create_winery_heatmap()
    print(f"Successfully created heatmap: {output_file}")