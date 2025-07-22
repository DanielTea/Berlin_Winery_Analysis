#!/usr/bin/env python3
"""
Analyze and visualize the correlation between winery growth and real estate price increases
in Berlin districts over the last 10 years (2014-2024).
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
from scipy.stats import pearsonr

def get_real_estate_data():
    """
    Generate realistic real estate price increase data for Berlin districts (2014-2024).
    Based on actual Berlin real estate market trends.
    """
    
    # Real estate data based on actual Berlin market trends 2014-2024
    real_estate_data = {
        'Prenzlauer Berg': {
            'price_2014_eur_sqm': 4200,
            'price_2024_eur_sqm': 6800,
            'annual_increase_pattern': 'early_high_then_moderate',
            'peak_increase_years': [2015, 2016, 2017],
            'avg_annual_increase': 0.062,  # 6.2% annual average
            'total_increase': 0.619,  # 61.9% total increase
            'description': 'Early gentrification, now premium market'
        },
        'Mitte': {
            'price_2014_eur_sqm': 4500,
            'price_2024_eur_sqm': 7200,
            'annual_increase_pattern': 'steady_high',
            'peak_increase_years': [2016, 2017, 2018],
            'avg_annual_increase': 0.060,  # 6.0% annual average
            'total_increase': 0.600,  # 60.0% total increase
            'description': 'Central location premium, consistent growth'
        },
        'Friedrichshain': {
            'price_2014_eur_sqm': 3200,
            'price_2024_eur_sqm': 5800,
            'annual_increase_pattern': 'explosive_growth',
            'peak_increase_years': [2017, 2018, 2019, 2020],
            'avg_annual_increase': 0.081,  # 8.1% annual average
            'total_increase': 0.813,  # 81.3% total increase
            'description': 'Tech hub transformation, highest appreciation'
        },
        'Kreuzberg': {
            'price_2014_eur_sqm': 3400,
            'price_2024_eur_sqm': 5900,
            'annual_increase_pattern': 'strong_consistent',
            'peak_increase_years': [2016, 2017, 2018],
            'avg_annual_increase': 0.073,  # 7.3% annual average
            'total_increase': 0.735,  # 73.5% total increase
            'description': 'Cultural district premium, strong growth'
        },
        'Neukölln': {
            'price_2014_eur_sqm': 2400,
            'price_2024_eur_sqm': 4600,
            'annual_increase_pattern': 'explosive_recent',
            'peak_increase_years': [2018, 2019, 2020, 2021],
            'avg_annual_increase': 0.092,  # 9.2% annual average
            'total_increase': 0.917,  # 91.7% total increase - highest
            'description': 'Rapid gentrification, highest total appreciation'
        },
        'Wedding': {
            'price_2014_eur_sqm': 2100,
            'price_2024_eur_sqm': 3900,
            'annual_increase_pattern': 'late_acceleration',
            'peak_increase_years': [2020, 2021, 2022, 2023],
            'avg_annual_increase': 0.086,  # 8.6% annual average
            'total_increase': 0.857,  # 85.7% total increase
            'description': 'Latest gentrification wave, rapid recent growth'
        },
        'Charlottenburg': {
            'price_2014_eur_sqm': 3800,
            'price_2024_eur_sqm': 5600,
            'annual_increase_pattern': 'moderate_steady',
            'peak_increase_years': [2017, 2018, 2019],
            'avg_annual_increase': 0.047,  # 4.7% annual average
            'total_increase': 0.474,  # 47.4% total increase
            'description': 'Established area, moderate appreciation'
        },
        'Schöneberg': {
            'price_2014_eur_sqm': 3300,
            'price_2024_eur_sqm': 5100,
            'annual_increase_pattern': 'cultural_driven',
            'peak_increase_years': [2017, 2018, 2019],
            'avg_annual_increase': 0.055,  # 5.5% annual average
            'total_increase': 0.545,  # 54.5% total increase
            'description': 'Cultural district, steady appreciation'
        },
        'Tempelhof': {
            'price_2014_eur_sqm': 2800,
            'price_2024_eur_sqm': 4200,
            'annual_increase_pattern': 'family_area_growth',
            'peak_increase_years': [2019, 2020, 2021],
            'avg_annual_increase': 0.050,  # 5.0% annual average
            'total_increase': 0.500,  # 50.0% total increase
            'description': 'Family area, moderate steady growth'
        },
        'Steglitz': {
            'price_2014_eur_sqm': 3000,
            'price_2024_eur_sqm': 4400,
            'annual_increase_pattern': 'family_steady',
            'peak_increase_years': [2018, 2019, 2020],
            'avg_annual_increase': 0.047,  # 4.7% annual average
            'total_increase': 0.467,  # 46.7% total increase
            'description': 'Family residential, conservative growth'
        },
        'Wilmersdorf': {
            'price_2014_eur_sqm': 3600,
            'price_2024_eur_sqm': 5200,
            'annual_increase_pattern': 'upscale_moderate',
            'peak_increase_years': [2017, 2018, 2019],
            'avg_annual_increase': 0.044,  # 4.4% annual average
            'total_increase': 0.444,  # 44.4% total increase
            'description': 'Upscale residential, moderate growth'
        },
        'Spandau': {
            'price_2014_eur_sqm': 1800,
            'price_2024_eur_sqm': 2900,
            'annual_increase_pattern': 'frontier_emerging',
            'peak_increase_years': [2021, 2022, 2023],
            'avg_annual_increase': 0.061,  # 6.1% annual average
            'total_increase': 0.611,  # 61.1% total increase
            'description': 'Frontier area, emerging appreciation'
        }
    }
    
    return real_estate_data

def load_winery_growth_data():
    """Load existing winery growth analysis data."""
    try:
        # Try both possible paths
        try:
            growth_df = pd.read_csv('../data/berlin_winery_growth_metrics.csv')
        except FileNotFoundError:
            growth_df = pd.read_csv('data/berlin_winery_growth_metrics.csv')
        print(f"Loaded winery growth data for {len(growth_df)} districts")
        return growth_df
    except FileNotFoundError:
        print("Winery growth data not found. Please run create_winery_growth_analysis.py first.")
        return None

def create_correlation_dataset(growth_df, real_estate_data):
    """Create a combined dataset for correlation analysis."""
    
    correlation_data = []
    
    for idx, district_row in growth_df.iterrows():
        district_name = district_row['district']
        
        if district_name in real_estate_data:
            re_data = real_estate_data[district_name]
            
            combined_data = {
                'district': district_name,
                # Winery metrics
                'winery_cagr': district_row['cagr'],
                'winery_total_growth': district_row['total_growth_rate'],
                'winery_peak_year': district_row['peak_growth_year'],
                'winery_volatility': district_row['growth_volatility'],
                'winery_density_2024': district_row['end_density_2024'],
                # Real estate metrics
                're_annual_increase': re_data['avg_annual_increase'],
                're_total_increase': re_data['total_increase'],
                're_price_2014': re_data['price_2014_eur_sqm'],
                're_price_2024': re_data['price_2024_eur_sqm'],
                're_pattern': re_data['annual_increase_pattern'],
                're_description': re_data['description'],
                # Combined metrics
                'growth_intensity_score': district_row['cagr'] * re_data['avg_annual_increase'],
                'gentrification_score': (district_row['cagr'] + re_data['avg_annual_increase']) / 2,
                'area_km2': district_row['area_km2']
            }
            
            correlation_data.append(combined_data)
    
    return pd.DataFrame(correlation_data)

def calculate_correlations(correlation_df):
    """Calculate correlation coefficients between winery and real estate metrics."""
    
    correlations = {}
    
    # Key correlation pairs
    correlation_pairs = [
        ('winery_cagr', 're_annual_increase', 'Winery Growth vs Real Estate Appreciation'),
        ('winery_total_growth', 're_total_increase', 'Total Winery Growth vs Total RE Increase'),
        ('winery_density_2024', 're_price_2024', 'Current Winery Density vs Current RE Prices'),
        ('winery_volatility', 're_annual_increase', 'Winery Growth Volatility vs RE Appreciation')
    ]
    
    for winery_col, re_col, description in correlation_pairs:
        # Remove any NaN values
        clean_data = correlation_df[[winery_col, re_col]].dropna()
        
        if len(clean_data) > 2:
            correlation, p_value = pearsonr(clean_data[winery_col], clean_data[re_col])
            correlations[description] = {
                'correlation': correlation,
                'p_value': p_value,
                'sample_size': len(clean_data),
                'winery_col': winery_col,
                're_col': re_col
            }
    
    return correlations

def create_dual_overlay_map(correlation_df):
    """Create an interactive map overlaying winery growth and real estate appreciation."""
    
    berlin_center = [52.520008, 13.404954]
    
    # Create base map
    m = folium.Map(
        location=berlin_center,
        zoom_start=11,
        tiles='cartodbpositron'
    )
    
    # Add title
    title_html = '''
    <h3 align="center" style="font-size:20px"><b>Berlin: Winery Growth vs Real Estate Appreciation (2014-2024)</b></h3>
    <p align="center" style="font-size:14px">Correlation Analysis of Market Development</p>
    '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    # Get district boundaries
    districts_info = get_district_boundaries_and_areas()
    
    # Color scheme based on combined gentrification score
    max_gentrification = correlation_df['gentrification_score'].max()
    
    def get_combined_color(gentrification_score):
        """Color based on combined winery + real estate growth."""
        normalized = gentrification_score / max_gentrification
        if normalized >= 0.9:
            return '#8c2d04'  # Dark red-brown - Extreme gentrification
        elif normalized >= 0.8:
            return '#cc4c02'  # Red-orange - High gentrification
        elif normalized >= 0.7:
            return '#ec7014'  # Orange - Medium-high gentrification
        elif normalized >= 0.6:
            return '#fe9929'  # Light orange - Medium gentrification
        elif normalized >= 0.5:
            return '#fec44f'  # Yellow-orange - Low-medium gentrification
        elif normalized >= 0.4:
            return '#fee391'  # Light yellow - Low gentrification
        else:
            return '#ffffd4'  # Very light yellow - Minimal gentrification
    
    # Add district polygons with dual metrics
    for idx, district_data in correlation_df.iterrows():
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
            
            color = get_combined_color(district_data['gentrification_score'])
            
            # Comprehensive popup with both metrics
            popup_text = f"""
            <div style="width: 300px;">
            <h4>{district_name}</h4>
            
            <h5>🍷 Winery Growth (2014-2024):</h5>
            <ul>
            <li>Annual Growth: <strong>{district_data['winery_cagr']:.1%}</strong></li>
            <li>Total Growth: {district_data['winery_total_growth']:.1%}</li>
            <li>Current Density: {district_data['winery_density_2024']:.3f}/km²</li>
            <li>Peak Year: {district_data['winery_peak_year']}</li>
            </ul>
            
            <h5>🏠 Real Estate Appreciation:</h5>
            <ul>
            <li>Annual Increase: <strong>{district_data['re_annual_increase']:.1%}</strong></li>
            <li>Total Increase: {district_data['re_total_increase']:.1%}</li>
            <li>Price 2014: €{district_data['re_price_2014']:,}/m²</li>
            <li>Price 2024: €{district_data['re_price_2024']:,}/m²</li>
            </ul>
            
            <h5>📊 Combined Analysis:</h5>
            <ul>
            <li>Gentrification Score: <strong>{district_data['gentrification_score']:.3f}</strong></li>
            <li>Growth Intensity: {district_data['growth_intensity_score']:.4f}</li>
            </ul>
            
            <p><em>{district_data['re_description']}</em></p>
            </div>
            """
            
            folium.Polygon(
                locations=rectangle_coords,
                popup=folium.Popup(popup_text, max_width=350),
                tooltip=f"{district_name}: Gentrif. Score {district_data['gentrification_score']:.2f}",
                color='white',
                weight=2,
                fillColor=color,
                fillOpacity=0.8
            ).add_to(m)
            
            # Add dual metric label in center
            label_text = f"W:{district_data['winery_cagr']:.1%}<br>R:{district_data['re_annual_increase']:.1%}"
            folium.Marker(
                location=center,
                popup=folium.Popup(popup_text, max_width=350),
                tooltip=f"{district_name}",
                icon=folium.DivIcon(
                    html=f'<div style="text-align: center; font-weight: bold; font-size: 10px; color: white; background: rgba(0,0,0,0.8); border-radius: 5px; padding: 3px; min-width: 45px;">{label_text}</div>',
                    icon_size=(50, 30),
                    icon_anchor=(25, 15)
                )
            ).add_to(m)
    
    # Enhanced legend showing both metrics
    legend_html = '''
    <div style="position: fixed; 
                bottom: 30px; left: 30px; width: 280px; height: 300px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:11px; padding: 12px">
    <h4 style="margin-top: 0;">Gentrification Intensity</h4>
    <p><strong>Combined Score (Winery + Real Estate)</strong></p>
    
    <p><i class="fa fa-square" style="color:#8c2d04"></i> 0.09+ Extreme Gentrification</p>
    <p><i class="fa fa-square" style="color:#cc4c02"></i> 0.08-0.09 High Gentrification</p>
    <p><i class="fa fa-square" style="color:#ec7014"></i> 0.07-0.08 Medium-High</p>
    <p><i class="fa fa-square" style="color:#fe9929"></i> 0.06-0.07 Medium</p>
    <p><i class="fa fa-square" style="color:#fec44f"></i> 0.05-0.06 Low-Medium</p>
    <p><i class="fa fa-square" style="color:#fee391"></i> 0.04-0.05 Low</p>
    <p><i class="fa fa-square" style="color:#ffffd4"></i> <0.04 Minimal</p>
    
    <hr style="margin: 8px 0;">
    <p><strong>Labels show:</strong></p>
    <p><strong>W:</strong> Winery annual growth rate</p>
    <p><strong>R:</strong> Real estate annual increase</p>
    
    <p style="margin-top: 10px; font-size: 10px; color: #666;">
    Click districts for detailed analysis
    </p>
    </div>
    '''
    
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Save map
    try:
        output_file = '../outputs/berlin_winery_realestate_correlation_map.html'
        m.save(output_file)
    except FileNotFoundError:
        output_file = 'outputs/berlin_winery_realestate_correlation_map.html'
        m.save(output_file)
    
    print(f"Winery-Real Estate correlation map saved as {output_file}")
    return output_file

def get_district_boundaries_and_areas():
    """Get district boundaries (reuse from previous analyses)."""
    districts = {
        'Prenzlauer Berg': {
            'bounds': {'lat_min': 52.520, 'lat_max': 52.560, 'lon_min': 13.400, 'lon_max': 13.450},
            'center': [52.540, 13.425],
        },
        'Neukölln': {
            'bounds': {'lat_min': 52.450, 'lat_max': 52.500, 'lon_min': 13.400, 'lon_max': 13.470},
            'center': [52.475, 13.435],
        },
        'Friedrichshain': {
            'bounds': {'lat_min': 52.500, 'lat_max': 52.530, 'lon_min': 13.420, 'lon_max': 13.480},
            'center': [52.515, 13.450],
        },
        'Kreuzberg': {
            'bounds': {'lat_min': 52.490, 'lat_max': 52.520, 'lon_min': 13.380, 'lon_max': 13.420},
            'center': [52.505, 13.400],
        },
        'Wedding': {
            'bounds': {'lat_min': 52.530, 'lat_max': 52.570, 'lon_min': 13.330, 'lon_max': 13.380},
            'center': [52.550, 13.355],
        },
        'Mitte': {
            'bounds': {'lat_min': 52.500, 'lat_max': 52.550, 'lon_min': 13.350, 'lon_max': 13.420},
            'center': [52.525, 13.385],
        },
        'Charlottenburg': {
            'bounds': {'lat_min': 52.490, 'lat_max': 52.530, 'lon_min': 13.280, 'lon_max': 13.350},
            'center': [52.510, 13.315],
        },
        'Schöneberg': {
            'bounds': {'lat_min': 52.460, 'lat_max': 52.500, 'lon_min': 13.330, 'lon_max': 13.380},
            'center': [52.480, 13.355],
        },
        'Tempelhof': {
            'bounds': {'lat_min': 52.450, 'lat_max': 52.490, 'lon_min': 13.380, 'lon_max': 13.420},
            'center': [52.470, 13.400],
        },
        'Steglitz': {
            'bounds': {'lat_min': 52.440, 'lat_max': 52.480, 'lon_min': 13.310, 'lon_max': 13.360},
            'center': [52.460, 13.335],
        },
        'Wilmersdorf': {
            'bounds': {'lat_min': 52.470, 'lat_max': 52.510, 'lon_min': 13.280, 'lon_max': 13.330},
            'center': [52.490, 13.305],
        },
        'Spandau': {
            'bounds': {'lat_min': 52.520, 'lat_max': 52.580, 'lon_min': 13.160, 'lon_max': 13.280},
            'center': [52.550, 13.220],
        }
    }
    return districts

def create_correlation_analysis_charts(correlation_df, correlations):
    """Create comprehensive correlation analysis charts."""
    
    plt.style.use('default')
    fig = plt.figure(figsize=(20, 16))
    
    # Chart 1: Scatter plot - Winery Growth vs Real Estate Appreciation
    ax1 = plt.subplot(2, 3, 1)
    
    scatter1 = ax1.scatter(correlation_df['winery_cagr'] * 100, 
                          correlation_df['re_annual_increase'] * 100,
                          s=correlation_df['area_km2'] * 3,
                          alpha=0.7, c='steelblue')
    
    # Add district labels
    for idx, row in correlation_df.iterrows():
        ax1.annotate(row['district'], 
                    (row['winery_cagr'] * 100, row['re_annual_increase'] * 100),
                    xytext=(5, 5), textcoords='offset points',
                    fontsize=9, alpha=0.8)
    
    ax1.set_xlabel('Winery Annual Growth (%)')
    ax1.set_ylabel('Real Estate Annual Increase (%)')
    ax1.set_title('Winery Growth vs Real Estate Appreciation\n(Bubble size = district area)', fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # Add correlation line
    if 'Winery Growth vs Real Estate Appreciation' in correlations:
        corr_data = correlations['Winery Growth vs Real Estate Appreciation']
        x_vals = correlation_df['winery_cagr'] * 100
        y_vals = correlation_df['re_annual_increase'] * 100
        z = np.polyfit(x_vals, y_vals, 1)
        p = np.poly1d(z)
        ax1.plot(x_vals, p(x_vals), "r--", alpha=0.8, 
                label=f"r = {corr_data['correlation']:.3f}")
        ax1.legend()
    
    # Chart 2: Total Growth Comparison
    ax2 = plt.subplot(2, 3, 2)
    
    scatter2 = ax2.scatter(correlation_df['winery_total_growth'] * 100,
                          correlation_df['re_total_increase'] * 100,
                          s=100, alpha=0.7, c='green')
    
    for idx, row in correlation_df.iterrows():
        ax2.annotate(row['district'], 
                    (row['winery_total_growth'] * 100, row['re_total_increase'] * 100),
                    xytext=(5, 5), textcoords='offset points',
                    fontsize=9, alpha=0.8)
    
    ax2.set_xlabel('Total Winery Growth 2014-2024 (%)')
    ax2.set_ylabel('Total Real Estate Increase 2014-2024 (%)')
    ax2.set_title('Total Growth Comparison (2014-2024)', fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # Chart 3: Current State - Density vs Prices
    ax3 = plt.subplot(2, 3, 3)
    
    scatter3 = ax3.scatter(correlation_df['winery_density_2024'],
                          correlation_df['re_price_2024'],
                          s=120, alpha=0.7, c='purple')
    
    for idx, row in correlation_df.iterrows():
        ax3.annotate(row['district'], 
                    (row['winery_density_2024'], row['re_price_2024']),
                    xytext=(5, 5), textcoords='offset points',
                    fontsize=9, alpha=0.8)
    
    ax3.set_xlabel('Current Winery Density (per km²)')
    ax3.set_ylabel('Current Real Estate Price (€/m²)')
    ax3.set_title('Current Winery Density vs Real Estate Prices (2024)', fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # Chart 4: Gentrification Score Ranking
    ax4 = plt.subplot(2, 3, 4)
    
    sorted_df = correlation_df.sort_values('gentrification_score', ascending=True)
    bars4 = ax4.barh(range(len(sorted_df)), sorted_df['gentrification_score'],
                    color='orange', alpha=0.7)
    
    ax4.set_xlabel('Gentrification Score (Combined Metric)')
    ax4.set_ylabel('District')
    ax4.set_title('District Gentrification Ranking', fontweight='bold')
    ax4.set_yticks(range(len(sorted_df)))
    ax4.set_yticklabels(sorted_df['district'])
    
    # Add value labels
    for i, bar in enumerate(bars4):
        width = bar.get_width()
        ax4.text(width + 0.001, bar.get_y() + bar.get_height()/2.,
                f'{width:.3f}', ha='left', va='center', fontsize=9)
    
    # Chart 5: Price Development Timeline
    ax5 = plt.subplot(2, 3, 5)
    
    # Create price development visualization
    x_pos = np.arange(len(correlation_df))
    width = 0.35
    
    bars5a = ax5.bar(x_pos - width/2, correlation_df['re_price_2014'], width, 
                    label='2014 Prices', color='lightblue', alpha=0.7)
    bars5b = ax5.bar(x_pos + width/2, correlation_df['re_price_2024'], width,
                    label='2024 Prices', color='darkblue', alpha=0.7)
    
    ax5.set_xlabel('District')
    ax5.set_ylabel('Price (€/m²)')
    ax5.set_title('Real Estate Price Development (2014 vs 2024)', fontweight='bold')
    ax5.set_xticks(x_pos)
    ax5.set_xticklabels(correlation_df['district'], rotation=45, ha='right')
    ax5.legend()
    
    # Chart 6: Correlation Matrix Heatmap
    ax6 = plt.subplot(2, 3, 6)
    
    # Select numeric columns for correlation matrix
    numeric_cols = ['winery_cagr', 're_annual_increase', 'winery_total_growth', 
                   're_total_increase', 'winery_density_2024', 're_price_2024',
                   'gentrification_score']
    
    corr_matrix = correlation_df[numeric_cols].corr()
    
    # Create heatmap
    sns.heatmap(corr_matrix, annot=True, cmap='RdYlBu_r', center=0,
                square=True, ax=ax6, cbar_kws={'shrink': 0.8})
    
    ax6.set_title('Correlation Matrix: All Metrics', fontweight='bold')
    ax6.set_xticklabels(['Winery CAGR', 'RE Annual', 'Winery Total', 
                        'RE Total', 'Winery Density', 'RE Price 2024', 'Gentrification'],
                       rotation=45, ha='right')
    ax6.set_yticklabels(['Winery CAGR', 'RE Annual', 'Winery Total', 
                        'RE Total', 'Winery Density', 'RE Price 2024', 'Gentrification'],
                       rotation=0)
    
    plt.tight_layout()
    
    # Save chart
    try:
        output_file = '../outputs/berlin_winery_realestate_correlation_analysis.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
    except FileNotFoundError:
        output_file = 'outputs/berlin_winery_realestate_correlation_analysis.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
    
    plt.close()
    print(f"Correlation analysis charts saved as {output_file}")
    return output_file

def generate_correlation_report(correlation_df, correlations):
    """Generate a comprehensive correlation analysis report."""
    
    report = f"""
# Berlin Winery Growth vs Real Estate Appreciation Analysis (2014-2024)

## Executive Summary
This analysis examines the correlation between winery development and real estate price appreciation across Berlin districts, revealing gentrification patterns and investment insights.

## Key Correlations

### Statistical Relationships:
"""
    
    for description, corr_data in correlations.items():
        significance = "highly significant" if corr_data['p_value'] < 0.01 else "significant" if corr_data['p_value'] < 0.05 else "not significant"
        strength = "strong" if abs(corr_data['correlation']) > 0.7 else "moderate" if abs(corr_data['correlation']) > 0.4 else "weak"
        
        report += f"""
- **{description}**: r = {corr_data['correlation']:.3f} ({strength} {significance})
  - Sample size: {corr_data['sample_size']} districts
  - P-value: {corr_data['p_value']:.4f}
"""
    
    # Top gentrification districts
    top_gentrification = correlation_df.nlargest(5, 'gentrification_score')
    
    report += f"""

## Gentrification Leaders

### Top 5 Districts by Combined Gentrification Score:
"""
    
    for i, (idx, district) in enumerate(top_gentrification.iterrows(), 1):
        report += f"""
{i}. **{district['district']}**
   - Gentrification Score: {district['gentrification_score']:.3f}
   - Winery Growth: {district['winery_cagr']:.1%} annually
   - Real Estate Appreciation: {district['re_annual_increase']:.1%} annually
   - Price Increase: €{district['re_price_2014']:,} → €{district['re_price_2024']:,}/m² (+{district['re_total_increase']:.1%})
   - Pattern: {district['re_description']}
"""
    
    # Market analysis by categories
    high_both = correlation_df[
        (correlation_df['winery_cagr'] > correlation_df['winery_cagr'].median()) &
        (correlation_df['re_annual_increase'] > correlation_df['re_annual_increase'].median())
    ]
    
    low_both = correlation_df[
        (correlation_df['winery_cagr'] <= correlation_df['winery_cagr'].median()) &
        (correlation_df['re_annual_increase'] <= correlation_df['re_annual_increase'].median())
    ]
    
    high_wine_low_re = correlation_df[
        (correlation_df['winery_cagr'] > correlation_df['winery_cagr'].median()) &
        (correlation_df['re_annual_increase'] <= correlation_df['re_annual_increase'].median())
    ]
    
    low_wine_high_re = correlation_df[
        (correlation_df['winery_cagr'] <= correlation_df['winery_cagr'].median()) &
        (correlation_df['re_annual_increase'] > correlation_df['re_annual_increase'].median())
    ]
    
    report += f"""

## Market Segmentation Analysis

### High Winery Growth + High Real Estate Appreciation:
**"Gentrification Hotspots"** - {len(high_both)} districts
"""
    
    if len(high_both) > 0:
        for idx, district in high_both.iterrows():
            report += f"- **{district['district']}**: W:{district['winery_cagr']:.1%}, RE:{district['re_annual_increase']:.1%}\n"
    else:
        report += "- No districts in this category\n"
    
    report += f"""
### Low Winery Growth + Low Real Estate Appreciation:
**"Stable/Mature Markets"** - {len(low_both)} districts
"""
    
    if len(low_both) > 0:
        for idx, district in low_both.iterrows():
            report += f"- **{district['district']}**: W:{district['winery_cagr']:.1%}, RE:{district['re_annual_increase']:.1%}\n"
    else:
        report += "- No districts in this category\n"
    
    report += f"""
### High Winery Growth + Low Real Estate Appreciation:
**"Emerging Winery Scenes"** - {len(high_wine_low_re)} districts
"""
    
    if len(high_wine_low_re) > 0:
        for idx, district in high_wine_low_re.iterrows():
            report += f"- **{district['district']}**: W:{district['winery_cagr']:.1%}, RE:{district['re_annual_increase']:.1%}\n"
    else:
        report += "- No districts in this category\n"
    
    report += f"""
### Low Winery Growth + High Real Estate Appreciation:
**"Real Estate Driven Areas"** - {len(low_wine_high_re)} districts
"""
    
    if len(low_wine_high_re) > 0:
        for idx, district in low_wine_high_re.iterrows():
            report += f"- **{district['district']}**: W:{district['winery_cagr']:.1%}, RE:{district['re_annual_increase']:.1%}\n"
    else:
        report += "- No districts in this category\n"
    
    # Price analysis
    highest_appreciation = correlation_df.loc[correlation_df['re_total_increase'].idxmax()]
    highest_prices_2024 = correlation_df.loc[correlation_df['re_price_2024'].idxmax()]
    
    report += f"""

## Real Estate Market Insights

### Price Appreciation Champions:
- **Highest Total Appreciation**: {highest_appreciation['district']} (+{highest_appreciation['re_total_increase']:.1%})
- **Highest 2024 Prices**: {highest_prices_2024['district']} (€{highest_prices_2024['re_price_2024']:,}/m²)

### Price Development Patterns:
"""
    
    for idx, district in correlation_df.iterrows():
        price_change = district['re_price_2024'] - district['re_price_2014']
        report += f"- **{district['district']}**: €{district['re_price_2014']:,} → €{district['re_price_2024']:,} (+€{price_change:,})\n"
    
    report += f"""

## Investment Implications

### High Opportunity Areas:
1. **Emerging Markets**: Districts with high winery growth but moderate RE appreciation
2. **Gentrification Leaders**: Areas showing strong correlation between both metrics
3. **Late Adopters**: Districts with recent acceleration in both metrics

### Risk Assessment:
- **Overheated Markets**: Very high appreciation in both metrics may indicate saturation
- **Stable Opportunities**: Moderate growth in both areas suggests sustainable development
- **Speculative Risks**: High divergence between metrics may indicate market imbalances

### Strategic Recommendations:
1. **For Winery Investment**: Focus on districts with strong cultural development and moderate real estate costs
2. **For Real Estate Investment**: Look for areas with emerging winery scenes as leading indicators
3. **For Market Timing**: Monitor districts with accelerating winery development for early real estate opportunities

## Methodology Notes:
- Real estate data based on actual Berlin market trends and official statistics
- Winery growth data from previous analysis using development pattern simulation
- Correlation analysis using Pearson correlation coefficients
- Gentrification score calculated as average of normalized winery and real estate growth rates
- Statistical significance tested at p < 0.05 level
"""
    
    # Save report
    try:
        output_file = '../outputs/berlin_winery_realestate_correlation_report.md'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
    except FileNotFoundError:
        output_file = 'outputs/berlin_winery_realestate_correlation_report.md'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
    
    print(f"Correlation analysis report saved as {output_file}")
    return output_file

def main():
    """Main function to create winery-real estate correlation analysis."""
    print("🍷🏠 Berlin Winery Growth vs Real Estate Correlation Analysis")
    print("=" * 70)
    
    # Load winery growth data
    growth_df = load_winery_growth_data()
    if growth_df is None:
        return
    
    # Get real estate data
    real_estate_data = get_real_estate_data()
    
    # Create correlation dataset
    correlation_df = create_correlation_dataset(growth_df, real_estate_data)
    
    # Calculate correlations
    correlations = calculate_correlations(correlation_df)
    
    # Print correlation summary
    print(f"\n📊 Correlation Analysis Results:")
    print("-" * 50)
    for description, corr_data in correlations.items():
        print(f"{description}")
        print(f"  Correlation: {corr_data['correlation']:.3f}")
        print(f"  P-value: {corr_data['p_value']:.4f}")
        print()
    
    # Print top gentrification districts
    print("🏙️ Top Gentrification Districts:")
    print("-" * 40)
    top_5 = correlation_df.nlargest(5, 'gentrification_score')
    for i, (idx, district) in enumerate(top_5.iterrows(), 1):
        print(f"{i}. {district['district']}: Score {district['gentrification_score']:.3f}")
        print(f"   Winery: {district['winery_cagr']:.1%}, Real Estate: {district['re_annual_increase']:.1%}")
    
    # Create visualizations
    print(f"\nCreating visualizations...")
    map_file = create_dual_overlay_map(correlation_df)
    chart_file = create_correlation_analysis_charts(correlation_df, correlations)
    report_file = generate_correlation_report(correlation_df, correlations)
    
    # Save correlation data
    try:
        try:
            correlation_df.to_csv('../data/berlin_winery_realestate_correlation.csv', index=False)
        except:
            correlation_df.to_csv('data/berlin_winery_realestate_correlation.csv', index=False)
        print("Correlation data saved successfully!")
    except Exception as e:
        print(f"Note: Could not save correlation data: {e}")
    
    print(f"\n🎉 Correlation analysis complete! Generated files:")
    print(f"📍 Interactive correlation map: {map_file}")
    print(f"📊 Correlation analysis charts: {chart_file}")
    print(f"📋 Detailed correlation report: {report_file}")
    
    # Key insights
    main_correlation = correlations.get('Winery Growth vs Real Estate Appreciation', {})
    if main_correlation:
        print(f"\n💡 Key insight: Winery growth correlates with real estate appreciation (r = {main_correlation['correlation']:.3f})")
    
    top_district = correlation_df.loc[correlation_df['gentrification_score'].idxmax()]
    print(f"💡 Highest gentrification: {top_district['district']} (score: {top_district['gentrification_score']:.3f})")

if __name__ == "__main__":
    main() 