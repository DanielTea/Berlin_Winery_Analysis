#!/usr/bin/env python3
"""
Create a map visualization highlighting Berlin districts with recently opened wineries
to identify areas with upcoming winery supply growth.
"""

import pandas as pd
import folium
from folium.plugins import HeatMap
import json
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

def load_recent_wineries_data():
    """Load the recent wineries data."""
    try:
        # Try both possible paths
        try:
            df = pd.read_csv('../data/berlin_wineries_recent.csv')
        except FileNotFoundError:
            df = pd.read_csv('data/berlin_wineries_recent.csv')
        print(f"Loaded {len(df)} wineries with temporal data")
        return df
    except FileNotFoundError:
        print("Recent wineries data not found. Please run download_recent_wineries.py first.")
        return None

def analyze_district_trends(df):
    """Analyze which districts have the most recent winery activity."""
    
    # Filter for recent wineries only
    recent_df = df[df['is_recent'] == True].copy()
    
    # Count by district
    district_counts = recent_df['district'].value_counts()
    
    # Calculate recency metrics by district
    district_stats = df.groupby('district').agg({
        'is_recent': 'sum',  # Count of recent wineries
        'recency_score': 'mean',  # Average recency score
        'name': 'count'  # Total wineries
    }).round(2)
    
    district_stats.columns = ['recent_count', 'avg_recency_score', 'total_count']
    district_stats['recent_percentage'] = (district_stats['recent_count'] / district_stats['total_count'] * 100).round(1)
    
    # Sort by recent count
    district_stats = district_stats.sort_values('recent_count', ascending=False)
    
    print("\n=== DISTRICT ANALYSIS ===")
    print("Districts ranked by recent winery activity (last 2 years):\n")
    print(f"{'District':<20} {'Recent':<8} {'Total':<8} {'Recent %':<10} {'Avg Score':<10}")
    print("-" * 70)
    
    for district, stats in district_stats.iterrows():
        print(f"{district:<20} {int(stats['recent_count']):<8} {int(stats['total_count']):<8} "
              f"{stats['recent_percentage']:<10}% {stats['avg_recency_score']:<10}")
    
    return district_stats, recent_df

def create_recent_wineries_interactive_map(df, district_stats):
    """Create an interactive map highlighting recent winery activity."""
    
    # Berlin center coordinates
    berlin_center = [52.520008, 13.404954]
    
    # Create base map
    m = folium.Map(
        location=berlin_center,
        zoom_start=11,
        tiles='cartodbpositron'
    )
    
    # Add title
    title_html = '''
    <h3 align="center" style="font-size:20px"><b>Berlin Recent Wineries Map (Last 2 Years)</b></h3>
    <p align="center" style="font-size:14px">Districts with Emerging Winery Supply</p>
    '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    # Color scheme for districts based on recent activity
    def get_district_color(district, recent_count):
        if recent_count >= 5:
            return '#d73027'  # Red - High activity
        elif recent_count >= 3:
            return '#fc8d59'  # Orange - Medium activity
        elif recent_count >= 1:
            return '#fee08b'  # Yellow - Some activity
        else:
            return '#e0e0e0'  # Gray - Low activity
    
    # Create district circles based on recent activity
    district_centers = {
        'Mitte': [52.525, 13.385],
        'Prenzlauer Berg': [52.540, 13.425],
        'Charlottenburg': [52.510, 13.315],
        'Kreuzberg': [52.505, 13.400],
        'Neukölln': [52.475, 13.435],
        'Friedrichshain': [52.515, 13.450],
        'Schöneberg': [52.480, 13.355],
        'Wedding': [52.550, 13.355],
        'Tempelhof': [52.470, 13.400],
        'Steglitz': [52.460, 13.335],
    }
    
    # Add district circles
    for district, center in district_centers.items():
        if district in district_stats.index:
            stats = district_stats.loc[district]
            recent_count = int(stats['recent_count'])
            total_count = int(stats['total_count'])
            avg_score = stats['avg_recency_score']
            recent_pct = stats['recent_percentage']
            
            color = get_district_color(district, recent_count)
            radius = max(500, recent_count * 200)  # Larger circles for more recent activity
            
            # Create popup text
            popup_text = f"""
            <b>{district}</b><br>
            Recent wineries: {recent_count}<br>
            Total wineries: {total_count}<br>
            Recent activity: {recent_pct}%<br>
            Avg recency score: {avg_score}
            """
            
            folium.CircleMarker(
                location=center,
                radius=radius/100,  # Scale down for display
                popup=folium.Popup(popup_text, max_width=200),
                color='white',
                weight=2,
                fillColor=color,
                fillOpacity=0.7,
                tooltip=f"{district}: {recent_count} recent wineries"
            ).add_to(m)
    
    # Add individual winery markers
    recent_wineries = df[df['is_recent'] == True]
    
    for idx, winery in recent_wineries.iterrows():
        lat = winery['latitude']
        lon = winery['longitude']
        name = winery['name']
        district = winery['district']
        recency_score = winery['recency_score']
        category = winery['recency_category']
        
        # Color based on recency category
        if category == 'very_recent':
            marker_color = 'red'
            icon = 'star'
        elif category == 'recent':
            marker_color = 'orange'
            icon = 'wine-bottle'
        elif category == 'likely_recent':
            marker_color = 'green'  # Changed from yellow (invalid) to green
            icon = 'wine-bottle'
        else:
            marker_color = 'lightblue'
            icon = 'wine-bottle'
        
        popup_text = f"""
        <b>{name}</b><br>
        District: {district}<br>
        Category: {category}<br>
        Recency score: {recency_score}<br>
        """
        
        if winery.get('start_date') and str(winery.get('start_date')) != 'nan':
            popup_text += f"Opening date: {winery['start_date']}<br>"
        if winery.get('osm_timestamp') and str(winery.get('osm_timestamp')) != 'nan':
            popup_text += f"OSM added: {str(winery['osm_timestamp'])[:10]}<br>"
        
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_text, max_width=250),
            tooltip=name,
            icon=folium.Icon(color=marker_color, icon=icon, prefix='fa')
        ).add_to(m)
    
    # Add heatmap layer for recent wineries
    recent_coordinates = [[row['latitude'], row['longitude'], row['recency_score']] 
                         for idx, row in recent_wineries.iterrows()]
    
    if recent_coordinates:
        HeatMap(
            recent_coordinates,
            name='Recent Activity Heatmap',
            radius=15,
            blur=10,
            max_zoom=1,
            gradient={0.2: 'blue', 0.4: 'lime', 0.6: 'orange', 1: 'red'}
        ).add_to(m)
    
    # Add legend
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 180px; height: 120px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px">
    <p><b>District Activity Level</b></p>
    <p><i class="fa fa-circle" style="color:#d73027"></i> High (5+ recent)</p>
    <p><i class="fa fa-circle" style="color:#fc8d59"></i> Medium (3-4 recent)</p>
    <p><i class="fa fa-circle" style="color:#fee08b"></i> Some (1-2 recent)</p>
    <p><i class="fa fa-circle" style="color:#e0e0e0"></i> Low activity</p>
    </div>
    '''
    
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Save the map (try different paths)
    try:
        output_file = '../outputs/berlin_recent_wineries_map.html'
        m.save(output_file)
    except FileNotFoundError:
        output_file = 'outputs/berlin_recent_wineries_map.html'
        m.save(output_file)
    print(f"Interactive map saved as {output_file}")
    
    return output_file

def create_district_trend_chart(district_stats):
    """Create a bar chart showing district trends."""
    
    plt.style.use('default')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Chart 1: Recent wineries by district
    top_districts = district_stats.head(8)
    
    bars1 = ax1.bar(range(len(top_districts)), top_districts['recent_count'], 
                   color='steelblue', alpha=0.7)
    ax1.set_xlabel('District')
    ax1.set_ylabel('Number of Recent Wineries')
    ax1.set_title('Recent Wineries by District (Last 2 Years)')
    ax1.set_xticks(range(len(top_districts)))
    ax1.set_xticklabels(top_districts.index, rotation=45, ha='right')
    
    # Add value labels on bars
    for i, bar in enumerate(bars1):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{int(height)}', ha='center', va='bottom')
    
    # Chart 2: Recent percentage by district
    bars2 = ax2.bar(range(len(top_districts)), top_districts['recent_percentage'], 
                   color='orange', alpha=0.7)
    ax2.set_xlabel('District')
    ax2.set_ylabel('Percentage of Recent Wineries (%)')
    ax2.set_title('Recent Activity Rate by District')
    ax2.set_xticks(range(len(top_districts)))
    ax2.set_xticklabels(top_districts.index, rotation=45, ha='right')
    
    # Add value labels on bars
    for i, bar in enumerate(bars2):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{height:.1f}%', ha='center', va='bottom')
    
    plt.tight_layout()
    
    # Save chart (try different paths)
    try:
        output_file = '../outputs/berlin_district_trends.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
    except FileNotFoundError:
        output_file = 'outputs/berlin_district_trends.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"District trends chart saved as {output_file}")
    return output_file

def generate_insights_report(district_stats, recent_df):
    """Generate a text report with insights about emerging winery districts."""
    
    report = """
# Berlin Winery Supply Analysis - Emerging Districts Report

## Executive Summary
This analysis identifies Berlin districts with the highest concentration of recently opened wineries (last 2 years), 
indicating areas with emerging winery supply and potential growth opportunities.

## Key Findings

### Top Districts for Recent Winery Activity:
"""
    
    top_3 = district_stats.head(3)
    for i, (district, stats) in enumerate(top_3.iterrows(), 1):
        report += f"""
{i}. **{district}**
   - Recent wineries: {int(stats['recent_count'])}
   - Total wineries: {int(stats['total_count'])}
   - Recent activity rate: {stats['recent_percentage']}%
   - Average recency score: {stats['avg_recency_score']}
"""
    
    report += f"""
### Market Insights:
- **Total recent wineries identified**: {len(recent_df)}
- **Most active district**: {district_stats.index[0]} ({int(district_stats.iloc[0]['recent_count'])} recent openings)
- **Emerging hotspot**: Districts with high recent activity percentage indicate rapid growth
- **Supply concentration**: {district_stats['recent_count'].sum()} recent wineries across {len(district_stats[district_stats['recent_count'] > 0])} active districts

### Recommended Focus Areas:
Districts with both high absolute numbers AND high percentage of recent activity represent 
the strongest emerging winery supply markets:

"""
    
    # Find districts with both good absolute and relative performance
    high_performers = district_stats[
        (district_stats['recent_count'] >= 2) & 
        (district_stats['recent_percentage'] >= 15)
    ]
    
    for district, stats in high_performers.iterrows():
        report += f"- **{district}**: {int(stats['recent_count'])} recent wineries ({stats['recent_percentage']}% of total)\n"
    
    # Save report (try different paths)
    try:
        output_file = '../outputs/berlin_winery_supply_insights.md'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
    except FileNotFoundError:
        output_file = 'outputs/berlin_winery_supply_insights.md'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
    print(f"Insights report saved as {output_file}")
    return output_file

def main():
    """Main function to create recent wineries visualization."""
    print("🍷 Berlin Recent Wineries Map Generator")
    print("=" * 50)
    
    # Load data
    df = load_recent_wineries_data()
    if df is None:
        return
    
    # Analyze district trends
    district_stats, recent_df = analyze_district_trends(df)
    
    # Create visualizations
    map_file = create_recent_wineries_interactive_map(df, district_stats)
    chart_file = create_district_trend_chart(district_stats)
    report_file = generate_insights_report(district_stats, recent_df)
    
    print(f"\n🎉 Analysis complete! Generated files:")
    print(f"📍 Interactive map: {map_file}")
    print(f"📊 Trends chart: {chart_file}")
    print(f"📋 Insights report: {report_file}")
    
    print(f"\n💡 Key insight: {district_stats.index[0]} leads with {int(district_stats.iloc[0]['recent_count'])} recent wineries!")
    print(f"💡 Open the map to explore emerging winery districts in Berlin.")

if __name__ == "__main__":
    main() 