#!/usr/bin/env python3
"""
Berlin Winery Analysis - Main Entrypoint

This script orchestrates the complete Berlin winery analysis pipeline:
1. Downloads winery data from external sources
2. Creates interactive map visualizations
3. Generates heatmap visualizations

Usage:
    python main.py [options]
    
Options:
    --download-only    Only download data, skip visualizations
    --viz-only        Only create visualizations (requires existing data)
    --skip-download   Skip data download, create visualizations only
    --help           Show this help message
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

def run_script(script_path: str, description: str) -> bool:
    """Run a script and handle errors gracefully."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"{'='*60}")
    
    try:
        # Change to scripts directory to run the script
        original_dir = os.getcwd()
        scripts_dir = Path(__file__).parent / "scripts"
        os.chdir(scripts_dir)
        
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=False, 
                              text=True)
        
        # Change back to original directory
        os.chdir(original_dir)
        
        if result.returncode == 0:
            print(f"✅ {description} completed successfully!")
            return True
        else:
            print(f"❌ {description} failed with return code {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        os.chdir(original_dir)  # Ensure we change back even on error
        return False

def check_data_exists() -> bool:
    """Check if the required data files exist."""
    data_dir = Path(__file__).parent / "data"
    csv_file = data_dir / "berlin_wineries.csv"
    json_file = data_dir / "berlin_wineries.json"
    
    return csv_file.exists() and json_file.exists()

def create_directories():
    """Create necessary directories if they don't exist."""
    base_dir = Path(__file__).parent
    for dir_name in ["data", "outputs", "scripts"]:
        dir_path = base_dir / dir_name
        dir_path.mkdir(exist_ok=True)
        print(f"📁 Directory '{dir_name}' ready")

def main():
    """Main function to orchestrate the Berlin winery analysis."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Berlin Winery Analysis Pipeline")
    parser.add_argument("--download-only", action="store_true", 
                       help="Only download data, skip visualizations")
    parser.add_argument("--viz-only", action="store_true", 
                       help="Only create visualizations (requires existing data)")
    parser.add_argument("--skip-download", action="store_true", 
                       help="Skip data download, create visualizations only")
    
    args = parser.parse_args()
    
    print("🍷 Berlin Winery Analysis Pipeline")
    print("=" * 50)
    
    # Create necessary directories
    create_directories()
    
    # Check for conflicting arguments
    if args.download_only and args.viz_only:
        print("❌ Error: Cannot use --download-only and --viz-only together")
        return 1
    
    # Step 1: Download data (unless skipped)
    download_success = True
    if not args.viz_only and not args.skip_download:
        print("\n📥 Phase 1: Data Collection")
        download_success = run_script("download_berlin_wineries.py", 
                                    "Downloading Berlin winery data")
        
        if not download_success:
            print("❌ Data download failed. Cannot proceed with visualizations.")
            return 1
    
    # Check if data exists before proceeding with visualizations
    if not args.download_only:
        if not check_data_exists():
            print("❌ Error: Winery data not found. Please run with data download first.")
            print("   Try: python main.py (without --viz-only)")
            return 1
        
        print("\n📊 Phase 2: Creating Visualizations")
        
        # Step 2: Create interactive map
        map_success = run_script("create_real_map_visualization.py", 
                                "Creating interactive winery map")
        
        # Step 3: Create basic heatmap
        heatmap_success = run_script("create_winery_heatmap.py", 
                                   "Creating basic winery heatmap")
        
        # Step 4: Create improved heatmap
        improved_heatmap_success = run_script("create_winery_heatmap_improved.py", 
                                            "Creating improved winery heatmap")
        
        # Step 5: Download recent wineries data (with temporal analysis)
        recent_data_success = run_script("download_recent_wineries.py",
                                        "Downloading recent wineries data with temporal analysis")
        
        # Step 6: Create recent wineries map
        recent_map_success = True
        if recent_data_success:
            recent_map_success = run_script("create_recent_wineries_map.py",
                                           "Creating recent wineries districts map")
        
        # Step 7: Create winery density analysis
        density_success = run_script("create_winery_density_map.py",
                                    "Creating winery density analysis by district area")
        
        # Step 8: Create winery growth analysis
        growth_success = run_script("create_winery_growth_analysis.py",
                                   "Creating 10-year winery growth analysis")
        
        # Step 9: Create winery-real estate correlation analysis
        correlation_success = True
        if growth_success:
            correlation_success = run_script("create_winery_realestate_correlation.py",
                                            "Creating winery growth vs real estate correlation analysis")
        
        # Step 10: Create temporal leading indicator analysis
        temporal_success = True
        if correlation_success:
            temporal_success = run_script("create_temporal_leading_indicator_analysis.py",
                                         "Creating temporal analysis: winery growth as leading indicator")
        
        # Summary
        print("\n" + "="*60)
        print("📋 ANALYSIS SUMMARY")
        print("="*60)
        
        if not args.skip_download and not args.viz_only:
            print(f"📥 Data Download: {'✅ Success' if download_success else '❌ Failed'}")
        
        print(f"🗺️  Interactive Map: {'✅ Success' if map_success else '❌ Failed'}")
        print(f"📊 Basic Heatmap: {'✅ Success' if heatmap_success else '❌ Failed'}")
        print(f"📊 Improved Heatmap: {'✅ Success' if improved_heatmap_success else '❌ Failed'}")
        print(f"📥 Recent Data Analysis: {'✅ Success' if recent_data_success else '❌ Failed'}")
        print(f"🏙️  Recent Districts Map: {'✅ Success' if recent_map_success else '❌ Failed'}")
        print(f"📏 Density Analysis: {'✅ Success' if density_success else '❌ Failed'}")
        print(f"📈 Growth Analysis: {'✅ Success' if growth_success else '❌ Failed'}")
        print(f"🏠 Correlation Analysis: {'✅ Success' if correlation_success else '❌ Failed'}")
        print(f"⏰ Temporal Analysis: {'✅ Success' if temporal_success else '❌ Failed'}")
        
        # Show output files
        print("\n📁 Generated Files:")
        outputs_dir = Path(__file__).parent / "outputs"
        if outputs_dir.exists():
            for file in outputs_dir.iterdir():
                if file.is_file():
                    print(f"   📄 {file.name}")
        
        data_dir = Path(__file__).parent / "data" 
        if data_dir.exists():
            print("\n📁 Data Files:")
            for file in data_dir.iterdir():
                if file.is_file():
                    print(f"   📄 {file.name}")
        
        # Check overall success
        all_viz_success = (map_success and heatmap_success and improved_heatmap_success and 
                          recent_data_success and recent_map_success and density_success and 
                          growth_success and correlation_success and temporal_success)
        if all_viz_success:
            print("\n🎉 All visualizations created successfully!")
            print("\n💡 Next steps:")
            print("   • Open outputs/berlin_wineries_real_map.html in your browser")
            print("   • Open outputs/berlin_recent_wineries_map.html to see emerging districts")
            print("   • Open outputs/berlin_winery_density_map.html to see density by district area")
            print("   • Open outputs/berlin_winery_growth_map.html to see 10-year growth patterns")
            print("   • Open outputs/berlin_winery_realestate_correlation_map.html for gentrification analysis")
            print("   • View the generated heatmap PNG files in the outputs/ folder")
            print("   • Check outputs/berlin_winery_supply_insights.md for market insights")
            print("   • Review outputs/berlin_winery_density_report.md for density analysis")
            print("   • Study outputs/berlin_winery_growth_report.md for growth trends")
            print("   • Analyze outputs/berlin_winery_realestate_correlation_report.md for investment insights")
            print("   • Study outputs/berlin_leading_indicator_analysis_report.md for timing insights")
        else:
            print("\n⚠️  Some visualizations failed. Check the error messages above.")
            return 1
    
    else:
        print("\n✅ Data download completed successfully!")
        print("💡 To create visualizations, run: python main.py --viz-only")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 