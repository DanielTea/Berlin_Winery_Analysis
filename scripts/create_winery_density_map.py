#!/usr/bin/env python3
"""
Create a winery density map showing wineries per square kilometer by Berlin district.
This provides a true measure of winery concentration accounting for district size.
"""

import pandas as pd
import folium
from folium.plugins import HeatMap
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Rectangle

def load_winery_data():
    """Load winery data."""
    try:
        # Try both possible paths
        try:
            df = pd.read_csv('../data/berlin_wineries.csv')
        except FileNotFoundError:
            df = pd.read_csv('data/berlin_wineries.csv')
        print(f"Loaded {len(df)} wineries")
        return df
    except FileNotFoundError:
        print("Winery data not found. Please run the main analysis first.")
        return None

def get_district_boundaries_and_areas():
    """Define Berlin district boundaries and calculate their areas."""
    
    # Berlin district boundaries with more precise coordinates and area estimates
    districts = {
        'Mitte': {
            'bounds': {'lat_min': 52.500, 'lat_max': 52.550, 'lon_min': 13.350, 'lon_max': 13.420},
            'area_km2': 39.5,  # Official area in km²
            'center': [52.525, 13.385],
            'population': 383000,
            'description': 'Historic center, government district'
        },
        'Prenzlauer Berg': {
            'bounds': {'lat_min': 52.520, 'lat_max': 52.560, 'lon_min': 13.400, 'lon_max': 13.450},
            'area_km2': 10.9,
            'center': [52.540, 13.425],
            'population': 165000,
            'description': 'Trendy residential area'
        },
        'Charlottenburg': {
            'bounds': {'lat_min': 52.490, 'lat_max': 52.530, 'lon_min': 13.280, 'lon_max': 13.350},
            'area_km2': 64.7,
            'center': [52.510, 13.315],
            'population': 129000,
            'description': 'Western district, shopping area'
        },
        'Kreuzberg': {
            'bounds': {'lat_min': 52.490, 'lat_max': 52.520, 'lon_min': 13.380, 'lon_max': 13.420},
            'area_km2': 15.2,
            'center': [52.505, 13.400],
            'population': 154000,
            'description': 'Cultural hub, nightlife'
        },
        'Neukölln': {
            'bounds': {'lat_min': 52.450, 'lat_max': 52.500, 'lon_min': 13.400, 'lon_max': 13.470},
            'area_km2': 44.9,
            'center': [52.475, 13.435],
            'population': 329000,
            'description': 'Diverse, gentrifying area'
        },
        'Friedrichshain': {
            'bounds': {'lat_min': 52.500, 'lat_max': 52.530, 'lon_min': 13.420, 'lon_max': 13.480},
            'area_km2': 9.8,
            'center': [52.515, 13.450],
            'population': 289000,
            'description': 'Young, alternative scene'
        },
        'Schöneberg': {
            'bounds': {'lat_min': 52.460, 'lat_max': 52.500, 'lon_min': 13.330, 'lon_max': 13.380},
            'area_km2': 10.5,
            'center': [52.480, 13.355],
            'population': 349000,
            'description': 'LGBTQ+ district, cafes'
        },
        'Wedding': {
            'bounds': {'lat_min': 52.530, 'lat_max': 52.570, 'lon_min': 13.330, 'lon_max': 13.380},
            'area_km2': 9.5,
            'center': [52.550, 13.355],
            'population': 87000,
            'description': 'Up-and-coming area'
        },
        'Tempelhof': {
            'bounds': {'lat_min': 52.450, 'lat_max': 52.490, 'lon_min': 13.380, 'lon_max': 13.420},
            'area_km2': 12.2,
            'center': [52.470, 13.400],
            'population': 56000,
            'description': 'Former airport area'
        },
        'Steglitz': {
            'bounds': {'lat_min': 52.440, 'lat_max': 52.480, 'lon_min': 13.310, 'lon_max': 13.360},
            'area_km2': 9.2,
            'center': [52.460, 13.335],
            'population': 105000,
            'description': 'Residential, family area'
        },
        'Wilmersdorf': {
            'bounds': {'lat_min': 52.470, 'lat_max': 52.510, 'lon_min': 13.280, 'lon_max': 13.330},
            'area_km2': 8.9,
            'center': [52.490, 13.305],
            'population': 94000,
            'description': 'Upscale residential'
        },
        'Spandau': {
            'bounds': {'lat_min': 52.520, 'lat_max': 52.580, 'lon_min': 13.160, 'lon_max': 13.280},
            'area_km2': 91.9,
            'center': [52.550, 13.220],
            'population': 245000,
            'description': 'Historic town, outskirts'
        }
    }
    
    return districts

def assign_districts_to_wineries(df, districts):
    """Assign each winery to its district and calculate district statistics."""
    
    # Add district column
    df['district'] = 'Other'
    
    for idx, winery in df.iterrows():
        lat = winery.get('latitude')
        lon = winery.get('longitude')
        
        if lat and lon:
            for district_name, district_info in districts.items():
                bounds = district_info['bounds']
                if (bounds['lat_min'] <= lat <= bounds['lat_max'] and 
                    bounds['lon_min'] <= lon <= bounds['lon_max']):
                    df.loc[idx, 'district'] = district_name
                    break
    
    # Calculate district statistics
    district_stats = []
    
    for district_name, district_info in districts.items():
        district_wineries = df[df['district'] == district_name]
        winery_count = len(district_wineries)
        area_km2 = district_info['area_km2']
        density = winery_count / area_km2 if area_km2 > 0 else 0
        
        stats = {
            'district': district_name,
            'winery_count': winery_count,
            'area_km2': area_km2,
            'density_per_km2': round(density, 3),
            'population': district_info['population'],
            'wineries_per_100k_people': round((winery_count / district_info['population']) * 100000, 2) if district_info['population'] > 0 else 0,
            'center': district_info['center'],
            'description': district_info['description']
        }
        district_stats.append(stats)
    
    # Add "Other" areas (wineries not in defined districts)
    other_wineries = df[df['district'] == 'Other']
    if len(other_wineries) > 0:
        # Estimate area for "Other" (remaining Berlin area)
        total_defined_area = sum(d['area_km2'] for d in districts.values())
        berlin_total_area = 891.7  # Total Berlin area in km²
        other_area = berlin_total_area - total_defined_area
        
        other_stats = {
            'district': 'Other',
            'winery_count': len(other_wineries),
            'area_km2': other_area,
            'density_per_km2': round(len(other_wineries) / other_area, 3) if other_area > 0 else 0,
            'population': 800000,  # Rough estimate for remaining areas
            'wineries_per_100k_people': round((len(other_wineries) / 800000) * 100000, 2),
            'center': [52.520, 13.405],  # Berlin center
            'description': 'Other Berlin areas'
        }
        district_stats.append(other_stats)
    
    district_stats_df = pd.DataFrame(district_stats)
    district_stats_df = district_stats_df.sort_values('density_per_km2', ascending=False)
    
    return df, district_stats_df

def create_density_interactive_map(df, district_stats_df, districts):
    """Create an interactive map showing winery density by district."""
    
    berlin_center = [52.520008, 13.404954]
    
    # Create base map
    m = folium.Map(
        location=berlin_center,
        zoom_start=11,
        tiles='cartodbpositron'
    )
    
    # Add title
    title_html = '''
    <h3 align="center" style="font-size:20px"><b>Berlin Winery Density Map</b></h3>
    <p align="center" style="font-size:14px">Wineries per Square Kilometer by District</p>
    '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    # Color scheme based on density
    max_density = district_stats_df['density_per_km2'].max()
    
    def get_density_color(density):
        if density == 0:
            return '#f7f7f7'  # Light gray for no wineries
        elif density < 0.5:
            return '#fde68a'  # Light yellow
        elif density < 1.0:
            return '#fbbf24'  # Yellow
        elif density < 2.0:
            return '#f59e0b'  # Orange
        elif density < 3.0:
            return '#dc2626'  # Red
        else:
            return '#7f1d1d'  # Dark red
    
    # Add district rectangles/circles with density information
    for idx, district_data in district_stats_df.iterrows():
        district_name = district_data['district']
        density = district_data['density_per_km2']
        winery_count = district_data['winery_count']
        area = district_data['area_km2']
        
        if district_name in districts:
            center = districts[district_name]['center']
            bounds = districts[district_name]['bounds']
            
            # Create rectangle for district
            rectangle_coords = [
                [bounds['lat_min'], bounds['lon_min']],
                [bounds['lat_min'], bounds['lon_max']],
                [bounds['lat_max'], bounds['lon_max']],
                [bounds['lat_max'], bounds['lon_min']],
                [bounds['lat_min'], bounds['lon_min']]
            ]
            
            color = get_density_color(density)
            
            popup_text = f"""
            <b>{district_name}</b><br>
            <strong>Density: {density} wineries/km²</strong><br>
            Wineries: {winery_count}<br>
            Area: {area} km²<br>
            Population: {district_data['population']:,}<br>
            Wineries per 100k people: {district_data['wineries_per_100k_people']}<br>
            <em>{district_data['description']}</em>
            """
            
            folium.Polygon(
                locations=rectangle_coords,
                popup=folium.Popup(popup_text, max_width=300),
                tooltip=f"{district_name}: {density} wineries/km²",
                color='white',
                weight=2,
                fillColor=color,
                fillOpacity=0.7
            ).add_to(m)
            
            # Add density label in center
            folium.Marker(
                location=center,
                popup=folium.Popup(popup_text, max_width=300),
                tooltip=f"{district_name}: {density}/km²",
                icon=folium.DivIcon(
                    html=f'<div style="text-align: center; font-weight: bold; font-size: 14px; color: black; background: white; border: 2px solid black; border-radius: 5px; padding: 2px;">{density}</div>',
                    icon_size=(60, 20),
                    icon_anchor=(30, 10)
                )
            ).add_to(m)
    
    # Add individual winery markers
    for idx, winery in df.iterrows():
        lat = winery['latitude']
        lon = winery['longitude']
        name = winery['name']
        district = winery['district']
        
        popup_text = f"""
        <b>{name}</b><br>
        District: {district}<br>
        """
        
        # Color code by district density
        district_data = district_stats_df[district_stats_df['district'] == district]
        if len(district_data) > 0:
            density = district_data.iloc[0]['density_per_km2']
            if density >= 2.0:
                marker_color = 'red'
            elif density >= 1.0:
                marker_color = 'orange'
            elif density >= 0.5:
                marker_color = 'green'
            else:
                marker_color = 'blue'
        else:
            marker_color = 'gray'
        
        folium.CircleMarker(
            location=[lat, lon],
            radius=4,
            popup=folium.Popup(popup_text, max_width=200),
            tooltip=name,
            color='white',
            weight=1,
            fillColor=marker_color,
            fillOpacity=0.8
        ).add_to(m)
    
    # Add legend
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 200px; height: 180px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:12px; padding: 10px">
    <p><b>Winery Density (per km²)</b></p>
    <p><i class="fa fa-square" style="color:#7f1d1d"></i> 3.0+ Very High</p>
    <p><i class="fa fa-square" style="color:#dc2626"></i> 2.0-3.0 High</p>
    <p><i class="fa fa-square" style="color:#f59e0b"></i> 1.0-2.0 Medium</p>
    <p><i class="fa fa-square" style="color:#fbbf24"></i> 0.5-1.0 Low</p>
    <p><i class="fa fa-square" style="color:#fde68a"></i> 0.1-0.5 Very Low</p>
    <p><i class="fa fa-square" style="color:#f7f7f7"></i> 0 None</p>
    <p><b>Numbers show density values</b></p>
    </div>
    '''
    
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Save map
    try:
        output_file = '../outputs/berlin_winery_density_map.html'
        m.save(output_file)
    except FileNotFoundError:
        output_file = 'outputs/berlin_winery_density_map.html'
        m.save(output_file)
    
    print(f"Winery density map saved as {output_file}")
    return output_file

def create_density_analysis_charts(district_stats_df):
    """Create charts analyzing winery density across districts."""
    
    plt.style.use('default')
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Chart 1: Density by district
    top_districts = district_stats_df.head(10)
    
    bars1 = ax1.barh(range(len(top_districts)), top_districts['density_per_km2'], 
                    color='steelblue', alpha=0.7)
    ax1.set_xlabel('Wineries per km²')
    ax1.set_ylabel('District')
    ax1.set_title('Winery Density by District')
    ax1.set_yticks(range(len(top_districts)))
    ax1.set_yticklabels(top_districts['district'])
    
    # Add value labels
    for i, bar in enumerate(bars1):
        width = bar.get_width()
        ax1.text(width + 0.02, bar.get_y() + bar.get_height()/2.,
                f'{width:.2f}', ha='left', va='center')
    
    # Chart 2: Count vs Area scatter
    ax2.scatter(district_stats_df['area_km2'], district_stats_df['winery_count'], 
               s=district_stats_df['density_per_km2']*100, alpha=0.6, c='orange')
    ax2.set_xlabel('District Area (km²)')
    ax2.set_ylabel('Number of Wineries')
    ax2.set_title('Winery Count vs District Area\n(Bubble size = density)')
    
    # Add district labels
    for idx, row in district_stats_df.iterrows():
        if row['winery_count'] > 0:  # Only label districts with wineries
            ax2.annotate(row['district'], 
                        (row['area_km2'], row['winery_count']),
                        xytext=(5, 5), textcoords='offset points',
                        fontsize=8, alpha=0.8)
    
    # Chart 3: Wineries per population
    bars3 = ax3.bar(range(len(top_districts)), top_districts['wineries_per_100k_people'], 
                   color='green', alpha=0.7)
    ax3.set_xlabel('District')
    ax3.set_ylabel('Wineries per 100k People')
    ax3.set_title('Winery Accessibility by Population')
    ax3.set_xticks(range(len(top_districts)))
    ax3.set_xticklabels(top_districts['district'], rotation=45, ha='right')
    
    # Add value labels
    for i, bar in enumerate(bars3):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{height:.1f}', ha='center', va='bottom')
    
    # Chart 4: Efficiency comparison (density vs accessibility)
    ax4.scatter(district_stats_df['density_per_km2'], district_stats_df['wineries_per_100k_people'],
               s=district_stats_df['winery_count']*20, alpha=0.6, c='purple')
    ax4.set_xlabel('Density (wineries/km²)')
    ax4.set_ylabel('Accessibility (wineries/100k people)')
    ax4.set_title('District Efficiency: Density vs Accessibility\n(Bubble size = total wineries)')
    
    # Add district labels for interesting points
    for idx, row in district_stats_df.iterrows():
        if row['density_per_km2'] > 1 or row['wineries_per_100k_people'] > 10:
            ax4.annotate(row['district'], 
                        (row['density_per_km2'], row['wineries_per_100k_people']),
                        xytext=(5, 5), textcoords='offset points',
                        fontsize=8, alpha=0.8)
    
    plt.tight_layout()
    
    # Save chart
    try:
        output_file = '../outputs/berlin_winery_density_analysis.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
    except FileNotFoundError:
        output_file = 'outputs/berlin_winery_density_analysis.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
    
    plt.close()
    print(f"Density analysis charts saved as {output_file}")
    return output_file

def generate_density_report(district_stats_df):
    """Generate a detailed density analysis report."""
    
    report = f"""
# Berlin Winery Density Analysis Report

## Executive Summary
This analysis examines winery density across Berlin districts, accounting for both district size and population to provide insights into winery concentration and accessibility.

## Key Metrics

### Top Districts by Winery Density (wineries/km²):
"""
    
    top_5_density = district_stats_df.head(5)
    for i, (idx, district) in enumerate(top_5_density.iterrows(), 1):
        report += f"""
{i}. **{district['district']}**
   - Density: {district['density_per_km2']} wineries/km²
   - Total wineries: {district['winery_count']}
   - Area: {district['area_km2']} km²
   - Accessibility: {district['wineries_per_100k_people']} wineries per 100k people
   - {district['description']}
"""
    
    # Calculate summary statistics
    total_wineries = district_stats_df['winery_count'].sum()
    total_area = district_stats_df['area_km2'].sum()
    avg_density = total_wineries / total_area
    
    high_density_districts = len(district_stats_df[district_stats_df['density_per_km2'] >= 1.0])
    
    report += f"""
## Overall Statistics
- **Total wineries analyzed**: {total_wineries}
- **Total area covered**: {total_area:.1f} km²
- **Average density**: {avg_density:.3f} wineries/km²
- **Districts with high density (≥1.0/km²)**: {high_density_districts}

## District Categories

### High Density (≥2.0 wineries/km²):
"""
    
    high_density = district_stats_df[district_stats_df['density_per_km2'] >= 2.0]
    if len(high_density) > 0:
        for idx, district in high_density.iterrows():
            report += f"- **{district['district']}**: {district['density_per_km2']} wineries/km² ({district['winery_count']} wineries in {district['area_km2']} km²)\n"
    else:
        report += "- No districts with density ≥2.0 wineries/km²\n"
    
    report += "\n### Medium Density (1.0-2.0 wineries/km²):\n"
    medium_density = district_stats_df[
        (district_stats_df['density_per_km2'] >= 1.0) & 
        (district_stats_df['density_per_km2'] < 2.0)
    ]
    if len(medium_density) > 0:
        for idx, district in medium_density.iterrows():
            report += f"- **{district['district']}**: {district['density_per_km2']} wineries/km² ({district['winery_count']} wineries in {district['area_km2']} km²)\n"
    else:
        report += "- No districts with medium density\n"
    
    # Find most efficient districts (good balance of density and accessibility)
    district_stats_df['efficiency_score'] = (
        district_stats_df['density_per_km2'] * 0.6 + 
        district_stats_df['wineries_per_100k_people'] * 0.004  # Scale to similar range
    )
    
    top_efficient = district_stats_df.nlargest(3, 'efficiency_score')
    
    report += f"""
## Strategic Insights

### Most Efficient Districts (density + accessibility):
"""
    
    for i, (idx, district) in enumerate(top_efficient.iterrows(), 1):
        report += f"""
{i}. **{district['district']}**
   - Efficiency score: {district['efficiency_score']:.2f}
   - Density: {district['density_per_km2']}/km²
   - Accessibility: {district['wineries_per_100k_people']}/100k people
"""
    
    report += f"""
### Recommendations:
- **High opportunity areas**: Districts with low density but high population
- **Saturation concern**: Districts with very high density may be oversaturated
- **Underserved areas**: Large districts with low winery counts
- **Accessibility leaders**: Districts with high wineries-per-capita ratios

### Data Notes:
- Density calculations based on official district areas
- Population data used for accessibility metrics
- "Other" category includes peripheral Berlin areas
"""
    
    # Save report
    try:
        output_file = '../outputs/berlin_winery_density_report.md'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
    except FileNotFoundError:
        output_file = 'outputs/berlin_winery_density_report.md'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
    
    print(f"Density analysis report saved as {output_file}")
    return output_file

def analyze_density_patterns(district_stats_df):
    """Analyze and print density patterns."""
    
    print("\n" + "="*60)
    print("BERLIN WINERY DENSITY ANALYSIS")
    print("="*60)
    
    print(f"\n📊 District Rankings by Density (wineries/km²):")
    print("-" * 60)
    print(f"{'Rank':<5} {'District':<15} {'Density':<8} {'Count':<6} {'Area':<8} {'Pop/km²':<8}")
    print("-" * 60)
    
    for i, (idx, district) in enumerate(district_stats_df.iterrows(), 1):
        pop_density = district['population'] / district['area_km2'] if district['area_km2'] > 0 else 0
        print(f"{i:<5} {district['district']:<15} {district['density_per_km2']:<8.2f} "
              f"{district['winery_count']:<6} {district['area_km2']:<8.1f} {pop_density:<8.0f}")
    
    # Key insights
    highest_density = district_stats_df.iloc[0]
    most_wineries = district_stats_df.loc[district_stats_df['winery_count'].idxmax()]
    largest_area = district_stats_df.loc[district_stats_df['area_km2'].idxmax()]
    
    print(f"\n🏆 Key Insights:")
    print(f"   Highest density: {highest_density['district']} ({highest_density['density_per_km2']:.2f} wineries/km²)")
    print(f"   Most wineries: {most_wineries['district']} ({most_wineries['winery_count']} wineries)")
    print(f"   Largest district: {largest_area['district']} ({largest_area['area_km2']:.1f} km²)")
    
    # Efficiency analysis
    high_efficiency = district_stats_df[
        (district_stats_df['density_per_km2'] >= 1.0) & 
        (district_stats_df['wineries_per_100k_people'] >= 10)
    ]
    
    if len(high_efficiency) > 0:
        print(f"\n💎 High Efficiency Districts (density ≥1.0 + accessibility ≥10/100k):")
        for idx, district in high_efficiency.iterrows():
            print(f"   • {district['district']}: {district['density_per_km2']:.2f}/km², {district['wineries_per_100k_people']:.1f}/100k people")
    
def main():
    """Main function to create winery density analysis."""
    print("🍷 Berlin Winery Density Analyzer")
    print("=" * 50)
    
    # Load data
    df = load_winery_data()
    if df is None:
        return
    
    # Get district information
    districts = get_district_boundaries_and_areas()
    
    # Assign districts and calculate stats
    df_with_districts, district_stats_df = assign_districts_to_wineries(df, districts)
    
    # Analyze patterns
    analyze_density_patterns(district_stats_df)
    
    # Create visualizations
    map_file = create_density_interactive_map(df_with_districts, district_stats_df, districts)
    chart_file = create_density_analysis_charts(district_stats_df)
    report_file = generate_density_report(district_stats_df)
    
    print(f"\n🎉 Density analysis complete! Generated files:")
    print(f"📍 Interactive density map: {map_file}")
    print(f"📊 Analysis charts: {chart_file}")
    print(f"📋 Detailed report: {report_file}")
    
    print(f"\n💡 Key insight: {district_stats_df.iloc[0]['district']} has the highest winery density at {district_stats_df.iloc[0]['density_per_km2']:.2f} wineries/km²!")

if __name__ == "__main__":
    main() 