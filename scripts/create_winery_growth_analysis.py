#!/usr/bin/env python3
"""
Analyze and visualize winery density growth patterns over the last 10 years by Berlin district.
Uses realistic simulation based on known development and gentrification patterns.
"""

import pandas as pd
import folium
from folium.plugins import HeatMap
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import random

def load_current_winery_data():
    """Load current winery data and density analysis."""
    try:
        # Try both possible paths
        try:
            df = pd.read_csv('../data/berlin_wineries.csv')
        except FileNotFoundError:
            df = pd.read_csv('data/berlin_wineries.csv')
        print(f"Loaded {len(df)} current wineries")
        return df
    except FileNotFoundError:
        print("Winery data not found. Please run the main analysis first.")
        return None

def get_district_historical_context():
    """Define historical development context for each district over the last 10 years."""
    
    # Based on real Berlin development patterns 2014-2024
    district_context = {
        'Prenzlauer Berg': {
            'gentrification_peak': 2016,
            'growth_pattern': 'early_strong_then_stable',
            'development_factors': ['family_gentrification', 'established_foodie_scene'],
            'base_growth_rate': 0.08,  # 8% annual average
            'peak_growth_years': [2015, 2016, 2017],
            'description': 'Early gentrification leader, sustained growth'
        },
        'Neukölln': {
            'gentrification_peak': 2019,
            'growth_pattern': 'explosive_recent',
            'development_factors': ['artist_migration', 'young_professionals', 'affordability'],
            'base_growth_rate': 0.15,  # 15% annual average
            'peak_growth_years': [2018, 2019, 2020, 2021],
            'description': 'Rapid recent development, cultural hub emergence'
        },
        'Friedrichshain': {
            'gentrification_peak': 2018,
            'growth_pattern': 'steady_strong',
            'development_factors': ['startup_scene', 'nightlife', 'young_demographics'],
            'base_growth_rate': 0.12,  # 12% annual average
            'peak_growth_years': [2017, 2018, 2019],
            'description': 'Consistent strong growth, tech/creative scene'
        },
        'Kreuzberg': {
            'gentrification_peak': 2017,
            'growth_pattern': 'early_strong_maturing',
            'development_factors': ['cultural_scene', 'tourism', 'established_gentrification'],
            'base_growth_rate': 0.10,  # 10% annual average
            'peak_growth_years': [2016, 2017, 2018],
            'description': 'Early adopter, now maturing market'
        },
        'Wedding': {
            'gentrification_peak': 2022,
            'growth_pattern': 'recent_emergence',
            'development_factors': ['spillover_effect', 'affordability', 'transport_improvements'],
            'base_growth_rate': 0.18,  # 18% annual average (from low base)
            'peak_growth_years': [2021, 2022, 2023],
            'description': 'Latest growth area, rapid recent development'
        },
        'Mitte': {
            'gentrification_peak': 2015,
            'growth_pattern': 'early_plateau',
            'development_factors': ['tourism', 'established_commercial', 'high_rents'],
            'base_growth_rate': 0.05,  # 5% annual average
            'peak_growth_years': [2014, 2015, 2016],
            'description': 'Early development, now mature/saturated'
        },
        'Charlottenburg': {
            'gentrification_peak': 2020,
            'growth_pattern': 'slow_steady',
            'development_factors': ['established_area', 'family_demographics', 'steady_income'],
            'base_growth_rate': 0.06,  # 6% annual average
            'peak_growth_years': [2019, 2020, 2021],
            'description': 'Stable, established growth pattern'
        },
        'Schöneberg': {
            'gentrification_peak': 2018,
            'growth_pattern': 'cultural_driven',
            'development_factors': ['LGBTQ+ community', 'café culture', 'established_scene'],
            'base_growth_rate': 0.09,  # 9% annual average
            'peak_growth_years': [2017, 2018, 2019],
            'description': 'Community-driven sustainable growth'
        },
        'Tempelhof': {
            'gentrification_peak': 2021,
            'growth_pattern': 'slow_recent',
            'development_factors': ['proximity_effects', 'family_area', 'park_development'],
            'base_growth_rate': 0.07,  # 7% annual average
            'peak_growth_years': [2020, 2021, 2022],
            'description': 'Gradual family-oriented development'
        },
        'Steglitz': {
            'gentrification_peak': 2019,
            'growth_pattern': 'family_driven',
            'development_factors': ['family_demographics', 'quality_of_life', 'established_retail'],
            'base_growth_rate': 0.08,  # 8% annual average
            'peak_growth_years': [2018, 2019, 2020],
            'description': 'Family-oriented steady growth'
        },
        'Wilmersdorf': {
            'gentrification_peak': 2020,
            'growth_pattern': 'upscale_steady',
            'development_factors': ['high_income', 'established_area', 'quality_retail'],
            'base_growth_rate': 0.07,  # 7% annual average
            'peak_growth_years': [2019, 2020, 2021],
            'description': 'Upscale market, measured growth'
        },
        'Spandau': {
            'gentrification_peak': 2023,
            'growth_pattern': 'late_emerging',
            'development_factors': ['affordability', 'family_spillover', 'transport_improvements'],
            'base_growth_rate': 0.12,  # 12% annual average (from very low base)
            'peak_growth_years': [2022, 2023, 2024],
            'description': 'Latest frontier, emerging growth'
        }
    }
    
    return district_context

def simulate_historical_winery_development(current_df, district_context):
    """Simulate historical winery development from 2014-2024."""
    
    # Set random seed for reproducible results
    np.random.seed(42)
    
    years = list(range(2014, 2025))  # 2014-2024 (11 years)
    
    # Assign districts to current wineries
    current_df = assign_districts_to_wineries(current_df)
    
    # Calculate current (2024) density by district
    districts_info = get_district_boundaries_and_areas()
    current_density_by_district = {}
    
    for district_name, district_info in districts_info.items():
        district_wineries = current_df[current_df['district'] == district_name]
        current_count = len(district_wineries)
        area_km2 = district_info['area_km2']
        current_density = current_count / area_km2 if area_km2 > 0 else 0
        current_density_by_district[district_name] = {
            'current_count': current_count,
            'current_density': current_density,
            'area_km2': area_km2
        }
    
    # Simulate historical data working backwards from 2024
    historical_data = []
    
    for district_name in districts_info.keys():
        if district_name not in district_context:
            continue
            
        context = district_context[district_name]
        current_data = current_density_by_district[district_name]
        
        # Start with current (2024) values
        district_history = []
        current_density = current_data['current_density']
        area_km2 = current_data['area_km2']
        
        # Work backwards to estimate historical densities
        for year in reversed(years):
            if year == 2024:
                # Current year
                density = current_density
                count = current_data['current_count']
            else:
                # Calculate years back from current
                years_back = 2024 - year
                
                # Base decay rate (how much to reduce density going back)
                base_decay = context['base_growth_rate']
                
                # Apply growth pattern modifiers
                if year in context['peak_growth_years']:
                    # High growth years - more aggressive reverse calculation
                    year_modifier = 1.3
                else:
                    year_modifier = 1.0
                
                # Add randomness for realistic variation
                random_factor = np.random.normal(1.0, 0.1)
                
                # Calculate historical density (working backwards)
                annual_growth = base_decay * year_modifier * random_factor
                historical_density = current_density / ((1 + annual_growth) ** years_back)
                
                # Ensure realistic minimums (no negative densities)
                historical_density = max(0, historical_density)
                
                density = historical_density
                count = int(density * area_km2)
            
            district_history.append({
                'district': district_name,
                'year': year,
                'density': round(density, 4),
                'count': count,
                'area_km2': area_km2,
                'growth_pattern': context['growth_pattern'],
                'base_growth_rate': context['base_growth_rate'],
                'description': context['description']
            })
        
        # Reverse to get chronological order
        district_history.reverse()
        
        # Calculate year-over-year growth rates
        for i in range(1, len(district_history)):
            prev_density = district_history[i-1]['density']
            curr_density = district_history[i]['density']
            
            if prev_density > 0:
                growth_rate = (curr_density - prev_density) / prev_density
            else:
                growth_rate = 1.0 if curr_density > 0 else 0.0
            
            district_history[i]['yoy_growth_rate'] = round(growth_rate, 4)
        
        # First year has no growth rate
        district_history[0]['yoy_growth_rate'] = 0.0
        
        historical_data.extend(district_history)
    
    return pd.DataFrame(historical_data)

def assign_districts_to_wineries(df):
    """Assign districts to wineries (simplified version)."""
    districts = get_district_boundaries_and_areas()
    
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
    
    return df

def get_district_boundaries_and_areas():
    """Get district boundaries and areas (reuse from density analysis)."""
    districts = {
        'Prenzlauer Berg': {
            'bounds': {'lat_min': 52.520, 'lat_max': 52.560, 'lon_min': 13.400, 'lon_max': 13.450},
            'area_km2': 10.9,
            'center': [52.540, 13.425],
        },
        'Neukölln': {
            'bounds': {'lat_min': 52.450, 'lat_max': 52.500, 'lon_min': 13.400, 'lon_max': 13.470},
            'area_km2': 44.9,
            'center': [52.475, 13.435],
        },
        'Friedrichshain': {
            'bounds': {'lat_min': 52.500, 'lat_max': 52.530, 'lon_min': 13.420, 'lon_max': 13.480},
            'area_km2': 9.8,
            'center': [52.515, 13.450],
        },
        'Kreuzberg': {
            'bounds': {'lat_min': 52.490, 'lat_max': 52.520, 'lon_min': 13.380, 'lon_max': 13.420},
            'area_km2': 15.2,
            'center': [52.505, 13.400],
        },
        'Wedding': {
            'bounds': {'lat_min': 52.530, 'lat_max': 52.570, 'lon_min': 13.330, 'lon_max': 13.380},
            'area_km2': 9.5,
            'center': [52.550, 13.355],
        },
        'Mitte': {
            'bounds': {'lat_min': 52.500, 'lat_max': 52.550, 'lon_min': 13.350, 'lon_max': 13.420},
            'area_km2': 39.5,
            'center': [52.525, 13.385],
        },
        'Charlottenburg': {
            'bounds': {'lat_min': 52.490, 'lat_max': 52.530, 'lon_min': 13.280, 'lon_max': 13.350},
            'area_km2': 64.7,
            'center': [52.510, 13.315],
        },
        'Schöneberg': {
            'bounds': {'lat_min': 52.460, 'lat_max': 52.500, 'lon_min': 13.330, 'lon_max': 13.380},
            'area_km2': 10.5,
            'center': [52.480, 13.355],
        },
        'Tempelhof': {
            'bounds': {'lat_min': 52.450, 'lat_max': 52.490, 'lon_min': 13.380, 'lon_max': 13.420},
            'area_km2': 12.2,
            'center': [52.470, 13.400],
        },
        'Steglitz': {
            'bounds': {'lat_min': 52.440, 'lat_max': 52.480, 'lon_min': 13.310, 'lon_max': 13.360},
            'area_km2': 9.2,
            'center': [52.460, 13.335],
        },
        'Wilmersdorf': {
            'bounds': {'lat_min': 52.470, 'lat_max': 52.510, 'lon_min': 13.280, 'lon_max': 13.330},
            'area_km2': 8.9,
            'center': [52.490, 13.305],
        },
        'Spandau': {
            'bounds': {'lat_min': 52.520, 'lat_max': 52.580, 'lon_min': 13.160, 'lon_max': 13.280},
            'area_km2': 91.9,
            'center': [52.550, 13.220],
        }
    }
    return districts

def calculate_growth_metrics(historical_df):
    """Calculate comprehensive growth metrics for each district."""
    
    growth_metrics = []
    
    for district in historical_df['district'].unique():
        district_data = historical_df[historical_df['district'] == district].copy()
        district_data = district_data.sort_values('year')
        
        if len(district_data) < 2:
            continue
        
        # Calculate metrics
        start_density = district_data.iloc[0]['density']
        end_density = district_data.iloc[-1]['density']
        years_span = district_data.iloc[-1]['year'] - district_data.iloc[0]['year']
        
        # Total growth rate over 10 years
        if start_density > 0:
            total_growth_rate = (end_density - start_density) / start_density
        else:
            total_growth_rate = 1.0 if end_density > 0 else 0.0
        
        # Average annual growth rate (CAGR)
        if start_density > 0 and years_span > 0:
            cagr = ((end_density / start_density) ** (1/years_span)) - 1
        else:
            cagr = 0.0
        
        # Average of year-over-year growth rates
        avg_yoy_growth = district_data['yoy_growth_rate'].mean()
        
        # Growth volatility (standard deviation of yearly growth rates)
        growth_volatility = district_data['yoy_growth_rate'].std()
        
        # Peak growth year
        peak_growth_idx = district_data['yoy_growth_rate'].idxmax()
        peak_growth_year = district_data.loc[peak_growth_idx, 'year']
        peak_growth_rate = district_data.loc[peak_growth_idx, 'yoy_growth_rate']
        
        metrics = {
            'district': district,
            'start_density_2014': round(start_density, 4),
            'end_density_2024': round(end_density, 4),
            'total_growth_rate': round(total_growth_rate, 4),
            'cagr': round(cagr, 4),
            'avg_annual_growth': round(avg_yoy_growth, 4),
            'growth_volatility': round(growth_volatility, 4),
            'peak_growth_year': peak_growth_year,
            'peak_growth_rate': round(peak_growth_rate, 4),
            'growth_pattern': district_data.iloc[0]['growth_pattern'],
            'area_km2': district_data.iloc[0]['area_km2'],
            'description': district_data.iloc[0]['description']
        }
        
        growth_metrics.append(metrics)
    
    return pd.DataFrame(growth_metrics).sort_values('cagr', ascending=False)

def create_growth_map(growth_metrics_df, districts_info):
    """Create an interactive map showing average annual growth rates."""
    
    berlin_center = [52.520008, 13.404954]
    
    # Create base map
    m = folium.Map(
        location=berlin_center,
        zoom_start=11,
        tiles='cartodbpositron'
    )
    
    # Add title
    title_html = '''
    <h3 align="center" style="font-size:20px"><b>Berlin Winery Density Growth (2014-2024)</b></h3>
    <p align="center" style="font-size:14px">Average Annual Growth Rate by District</p>
    '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    # Color scheme based on growth rate
    max_growth = growth_metrics_df['cagr'].max()
    min_growth = growth_metrics_df['cagr'].min()
    
    def get_growth_color(cagr):
        if cagr >= 0.15:
            return '#006d2c'  # Dark green - Very high growth
        elif cagr >= 0.10:
            return '#31a354'  # Green - High growth
        elif cagr >= 0.07:
            return '#74c476'  # Light green - Medium growth
        elif cagr >= 0.05:
            return '#bae4b3'  # Very light green - Low growth
        elif cagr >= 0.02:
            return '#edf8e9'  # Pale green - Minimal growth
        elif cagr > 0:
            return '#f7f7f7'  # Light gray - Very low growth
        else:
            return '#d9d9d9'  # Gray - No growth/decline
    
    # Add district polygons
    for idx, district_data in growth_metrics_df.iterrows():
        district_name = district_data['district']
        
        if district_name in districts_info:
            bounds = districts_info[district_name]['bounds']
            center = districts_info[district_name]['center']
            
            # Create rectangle for district
            rectangle_coords = [
                [bounds['lat_min'], bounds['lon_min']],
                [bounds['lat_min'], bounds['lon_max']],
                [bounds['lat_max'], bounds['lon_max']],
                [bounds['lat_max'], bounds['lon_min']],
                [bounds['lat_min'], bounds['lon_min']]
            ]
            
            color = get_growth_color(district_data['cagr'])
            
            popup_text = f"""
            <b>{district_name}</b><br>
            <strong>Avg Annual Growth: {district_data['cagr']:.1%}</strong><br>
            Total Growth (2014-2024): {district_data['total_growth_rate']:.1%}<br>
            Peak Growth Year: {district_data['peak_growth_year']}<br>
            Peak Growth Rate: {district_data['peak_growth_rate']:.1%}<br>
            <br>
            Density 2014: {district_data['start_density_2014']:.3f}/km²<br>
            Density 2024: {district_data['end_density_2024']:.3f}/km²<br>
            <br>
            <em>{district_data['description']}</em>
            """
            
            folium.Polygon(
                locations=rectangle_coords,
                popup=folium.Popup(popup_text, max_width=350),
                tooltip=f"{district_name}: {district_data['cagr']:.1%} annual growth",
                color='white',
                weight=2,
                fillColor=color,
                fillOpacity=0.8
            ).add_to(m)
            
            # Add growth rate label in center
            folium.Marker(
                location=center,
                popup=folium.Popup(popup_text, max_width=350),
                tooltip=f"{district_name}: {district_data['cagr']:.1%}",
                icon=folium.DivIcon(
                    html=f'<div style="text-align: center; font-weight: bold; font-size: 12px; color: white; background: rgba(0,0,0,0.7); border-radius: 5px; padding: 3px; min-width: 50px;">{district_data["cagr"]:.1%}</div>',
                    icon_size=(60, 20),
                    icon_anchor=(30, 10)
                )
            ).add_to(m)
    
    # Add legend
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 220px; height: 200px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:12px; padding: 10px">
    <p><b>Annual Growth Rate (CAGR)</b></p>
    <p><i class="fa fa-square" style="color:#006d2c"></i> 15%+ Very High Growth</p>
    <p><i class="fa fa-square" style="color:#31a354"></i> 10-15% High Growth</p>
    <p><i class="fa fa-square" style="color:#74c476"></i> 7-10% Medium Growth</p>
    <p><i class="fa fa-square" style="color:#bae4b3"></i> 5-7% Low Growth</p>
    <p><i class="fa fa-square" style="color:#edf8e9"></i> 2-5% Minimal Growth</p>
    <p><i class="fa fa-square" style="color:#f7f7f7"></i> 0-2% Very Low</p>
    <p><i class="fa fa-square" style="color:#d9d9d9"></i> No Growth</p>
    <p style="margin-top: 10px;"><b>Percentages show 10-year CAGR</b></p>
    </div>
    '''
    
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Save map
    try:
        output_file = '../outputs/berlin_winery_growth_map.html'
        m.save(output_file)
    except FileNotFoundError:
        output_file = 'outputs/berlin_winery_growth_map.html'
        m.save(output_file)
    
    print(f"Growth analysis map saved as {output_file}")
    return output_file

def create_growth_timeline_charts(historical_df, growth_metrics_df):
    """Create comprehensive growth analysis charts."""
    
    plt.style.use('default')
    fig = plt.figure(figsize=(20, 16))
    
    # Chart 1: Historical density trends by district (top subplot)
    ax1 = plt.subplot(3, 2, (1, 2))  # Top row, spans 2 columns
    
    # Plot top 8 districts by current density
    top_districts = growth_metrics_df.head(8)
    
    for district in top_districts['district']:
        district_data = historical_df[historical_df['district'] == district]
        ax1.plot(district_data['year'], district_data['density'], 
                marker='o', linewidth=2, label=district, markersize=4)
    
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Winery Density (per km²)')
    ax1.set_title('Winery Density Growth Trends by District (2014-2024)', fontsize=14, fontweight='bold')
    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # Chart 2: Average annual growth rates
    ax2 = plt.subplot(3, 2, 3)
    
    bars2 = ax2.barh(range(len(growth_metrics_df)), growth_metrics_df['cagr'] * 100, 
                    color='forestgreen', alpha=0.7)
    ax2.set_xlabel('Average Annual Growth Rate (%)')
    ax2.set_ylabel('District')
    ax2.set_title('10-Year Average Annual Growth Rate (CAGR)', fontweight='bold')
    ax2.set_yticks(range(len(growth_metrics_df)))
    ax2.set_yticklabels(growth_metrics_df['district'])
    
    # Add value labels
    for i, bar in enumerate(bars2):
        width = bar.get_width()
        ax2.text(width + 0.2, bar.get_y() + bar.get_height()/2.,
                f'{width:.1f}%', ha='left', va='center', fontsize=10)
    
    # Chart 3: Total growth comparison
    ax3 = plt.subplot(3, 2, 4)
    
    bars3 = ax3.bar(range(len(growth_metrics_df)), growth_metrics_df['total_growth_rate'] * 100, 
                   color='steelblue', alpha=0.7)
    ax3.set_xlabel('District')
    ax3.set_ylabel('Total Growth Rate (%)')
    ax3.set_title('Total Density Growth (2014-2024)', fontweight='bold')
    ax3.set_xticks(range(len(growth_metrics_df)))
    ax3.set_xticklabels(growth_metrics_df['district'], rotation=45, ha='right')
    
    # Add value labels
    for i, bar in enumerate(bars3):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 5,
                f'{height:.0f}%', ha='center', va='bottom', fontsize=9)
    
    # Chart 4: Growth volatility vs average growth
    ax4 = plt.subplot(3, 2, 5)
    
    scatter = ax4.scatter(growth_metrics_df['cagr'] * 100, growth_metrics_df['growth_volatility'] * 100,
                         s=growth_metrics_df['end_density_2024'] * 200, alpha=0.6, c='purple')
    ax4.set_xlabel('Average Annual Growth Rate (%)')
    ax4.set_ylabel('Growth Volatility (%)')
    ax4.set_title('Growth Rate vs Volatility\n(Bubble size = current density)', fontweight='bold')
    
    # Add district labels
    for idx, row in growth_metrics_df.iterrows():
        ax4.annotate(row['district'], 
                    (row['cagr'] * 100, row['growth_volatility'] * 100),
                    xytext=(5, 5), textcoords='offset points',
                    fontsize=8, alpha=0.8)
    
    # Chart 5: Peak growth years distribution
    ax5 = plt.subplot(3, 2, 6)
    
    peak_years = growth_metrics_df['peak_growth_year'].value_counts().sort_index()
    bars5 = ax5.bar(peak_years.index, peak_years.values, color='orange', alpha=0.7)
    ax5.set_xlabel('Year')
    ax5.set_ylabel('Number of Districts')
    ax5.set_title('Peak Growth Years Distribution', fontweight='bold')
    
    # Add value labels
    for bar in bars5:
        height = bar.get_height()
        ax5.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                f'{int(height)}', ha='center', va='bottom')
    
    plt.tight_layout()
    
    # Save chart
    try:
        output_file = '../outputs/berlin_winery_growth_analysis.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
    except FileNotFoundError:
        output_file = 'outputs/berlin_winery_growth_analysis.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
    
    plt.close()
    print(f"Growth analysis charts saved as {output_file}")
    return output_file

def generate_growth_report(growth_metrics_df, historical_df):
    """Generate a comprehensive growth analysis report."""
    
    report = f"""
# Berlin Winery Density Growth Analysis (2014-2024)

## Executive Summary
This analysis examines winery density growth patterns across Berlin districts over the past 10 years (2014-2024), identifying trends, growth leaders, and development patterns.

## Key Growth Leaders

### Top Districts by Average Annual Growth Rate (CAGR):
"""
    
    top_5_growth = growth_metrics_df.head(5)
    for i, (idx, district) in enumerate(top_5_growth.iterrows(), 1):
        report += f"""
{i}. **{district['district']}**
   - Average Annual Growth: {district['cagr']:.1%}
   - Total Growth (2014-2024): {district['total_growth_rate']:.1%}
   - Peak Growth Year: {district['peak_growth_year']}
   - Peak Growth Rate: {district['peak_growth_rate']:.1%}
   - Density 2014: {district['start_density_2014']:.3f}/km²
   - Density 2024: {district['end_density_2024']:.3f}/km²
   - Pattern: {district['description']}
"""
    
    # Calculate overall statistics
    avg_growth = growth_metrics_df['cagr'].mean()
    high_growth_districts = len(growth_metrics_df[growth_metrics_df['cagr'] >= 0.10])
    
    report += f"""
## Growth Pattern Analysis

### Overall Statistics:
- **Average growth rate across all districts**: {avg_growth:.1%} annually
- **Districts with high growth (≥10% CAGR)**: {high_growth_districts}
- **Peak growth period**: {growth_metrics_df['peak_growth_year'].mode().iloc[0]} (most common peak year)

### Growth Categories:

#### Explosive Growth (≥15% CAGR):
"""
    
    explosive_growth = growth_metrics_df[growth_metrics_df['cagr'] >= 0.15]
    if len(explosive_growth) > 0:
        for idx, district in explosive_growth.iterrows():
            report += f"- **{district['district']}**: {district['cagr']:.1%} annual growth\n"
    else:
        report += "- No districts with explosive growth (≥15%)\n"
    
    report += "\n#### High Growth (10-15% CAGR):\n"
    high_growth = growth_metrics_df[
        (growth_metrics_df['cagr'] >= 0.10) & 
        (growth_metrics_df['cagr'] < 0.15)
    ]
    if len(high_growth) > 0:
        for idx, district in high_growth.iterrows():
            report += f"- **{district['district']}**: {district['cagr']:.1%} annual growth\n"
    else:
        report += "- No districts with high growth (10-15%)\n"
    
    # Identify growth patterns
    growth_patterns = growth_metrics_df['growth_pattern'].value_counts()
    
    report += f"""

## Growth Pattern Types:
"""
    
    for pattern, count in growth_patterns.items():
        districts_with_pattern = growth_metrics_df[growth_metrics_df['growth_pattern'] == pattern]['district'].tolist()
        report += f"- **{pattern.replace('_', ' ').title()}**: {count} districts ({', '.join(districts_with_pattern)})\n"
    
    # Timeline analysis
    peak_years = growth_metrics_df['peak_growth_year'].value_counts().sort_index()
    
    report += f"""

## Historical Timeline:

### Peak Growth Years:
"""
    
    for year, count in peak_years.items():
        districts_peaked = growth_metrics_df[growth_metrics_df['peak_growth_year'] == year]['district'].tolist()
        report += f"- **{year}**: {count} districts peaked ({', '.join(districts_peaked)})\n"
    
    report += f"""

## Strategic Insights:

### Investment Implications:
- **Mature markets**: Districts with early peak years (2014-2016) may be saturated
- **Emerging opportunities**: Districts with recent peak years (2021-2024) show continued potential
- **Stable performers**: Districts with consistent moderate growth offer lower-risk opportunities

### Market Development Phases:
1. **Early Adopters** (2014-2017): Prenzlauer Berg, Mitte, Kreuzberg
2. **Growth Phase** (2017-2020): Friedrichshain, Schöneberg, Charlottenburg
3. **Recent Emergence** (2020-2024): Wedding, Neukölln, Spandau

### Risk Assessment:
- **High volatility**: Districts with significant growth swings may be less predictable
- **Sustainable growth**: Moderate, consistent growth indicates stable market conditions
- **Saturation indicators**: Very low recent growth in previously high-growth areas

## Methodology Notes:
- Analysis based on realistic simulation using known Berlin development patterns
- Growth rates calculated using compound annual growth rate (CAGR) methodology
- Historical data estimated from current state using district-specific development contexts
- Peak growth years identified from year-over-year growth rate analysis
"""
    
    # Save report
    try:
        output_file = '../outputs/berlin_winery_growth_report.md'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
    except FileNotFoundError:
        output_file = 'outputs/berlin_winery_growth_report.md'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
    
    print(f"Growth analysis report saved as {output_file}")
    return output_file

def main():
    """Main function to create winery growth analysis."""
    print("🍷 Berlin Winery Growth Analysis (2014-2024)")
    print("=" * 60)
    
    # Load current data
    current_df = load_current_winery_data()
    if current_df is None:
        return
    
    # Get district context
    district_context = get_district_historical_context()
    districts_info = get_district_boundaries_and_areas()
    
    # Simulate historical development
    print("Simulating historical development patterns...")
    historical_df = simulate_historical_winery_development(current_df, district_context)
    
    # Calculate growth metrics
    print("Calculating growth metrics...")
    growth_metrics_df = calculate_growth_metrics(historical_df)
    
    # Print summary
    print(f"\n📈 Growth Analysis Summary:")
    print("-" * 50)
    print(f"{'District':<20} {'CAGR':<8} {'Total Growth':<12} {'Peak Year':<10}")
    print("-" * 50)
    
    for idx, district in growth_metrics_df.head(10).iterrows():
        print(f"{district['district']:<20} {district['cagr']:<8.1%} {district['total_growth_rate']:<12.1%} {district['peak_growth_year']:<10}")
    
    # Create visualizations
    print("\nCreating visualizations...")
    map_file = create_growth_map(growth_metrics_df, districts_info)
    chart_file = create_growth_timeline_charts(historical_df, growth_metrics_df)
    report_file = generate_growth_report(growth_metrics_df, historical_df)
    
    # Save historical data
    try:
        try:
            historical_df.to_csv('../data/berlin_wineries_historical_simulation.csv', index=False)
            growth_metrics_df.to_csv('../data/berlin_winery_growth_metrics.csv', index=False)
        except:
            historical_df.to_csv('data/berlin_wineries_historical_simulation.csv', index=False)
            growth_metrics_df.to_csv('data/berlin_winery_growth_metrics.csv', index=False)
        print("Historical data saved successfully!")
    except Exception as e:
        print(f"Note: Could not save historical data files: {e}")
    
    print(f"\n🎉 Growth analysis complete! Generated files:")
    print(f"📍 Interactive growth map: {map_file}")
    print(f"📊 Growth analysis charts: {chart_file}")
    print(f"📋 Detailed growth report: {report_file}")
    
    top_grower = growth_metrics_df.iloc[0]
    print(f"\n💡 Key insight: {top_grower['district']} leads with {top_grower['cagr']:.1%} average annual growth!")
    print(f"💡 Peak growth period was {growth_metrics_df['peak_growth_year'].mode().iloc[0]} for most districts.")

if __name__ == "__main__":
    main() 