# Berlin Winery Analysis

This project provides data analysis and visualization tools for Berlin wineries. It includes data collection, processing, and visualization capabilities to explore the distribution and characteristics of wineries throughout Berlin.

## Features

- **Data Collection**: Download and process Berlin winery data
- **Interactive Maps**: Generate real map visualizations showing winery locations
- **Heatmaps**: Create density heatmaps of winery distributions
- **Data Analysis**: Analyze winery locations, distribution patterns, and characteristics

## Project Structure

```
Berlin_Winery_Analysis/
├── main.py                    # Main entrypoint for the analysis pipeline
├── data/                      # Data files
│   ├── berlin_wineries.csv    # CSV data of Berlin wineries
│   └── berlin_wineries.json   # JSON format of the winery data
├── scripts/                   # Analysis scripts
│   ├── download_berlin_wineries.py           # Download winery data
│   ├── create_real_map_visualization.py      # Generate interactive maps
│   ├── create_winery_heatmap.py             # Create basic heatmaps
│   └── create_winery_heatmap_improved.py    # Create enhanced heatmaps
├── outputs/                   # Generated visualizations
│   ├── berlin_wineries_real_map.html        # Interactive map
│   ├── berlin_wineries_heatmap.png          # Basic heatmap
│   └── berlin_wineries_heatmap_improved.png # Enhanced heatmap
├── pyproject.toml             # Project configuration and dependencies
├── LICENSE                    # Project license
└── README.md                 # This file
```

## Installation and Setup

1. Clone this repository
2. Install the project and dependencies:

```bash
# Install in development mode (recommended)
pip install -e .

# Or install from pyproject.toml
pip install .

# For development with additional tools
pip install -e ".[dev]"
```

## Usage

### Quick Start - Run Complete Analysis

To run the entire analysis pipeline (download data + create all visualizations):

```bash
python main.py
```

### Recent Wineries Analysis

To analyze districts with the most recently opened wineries (last 2 years):

```bash
# Generate recent wineries data using heuristics
cd scripts && python create_recent_wineries_from_existing.py

# Create the districts map visualization  
python create_recent_wineries_map.py
```

### Winery Density Analysis

To analyze winery density accounting for district size (wineries per km²):

```bash
cd scripts && python create_winery_density_map.py
```

### 10-Year Growth Analysis

To analyze winery density growth patterns over the last decade:

```bash
cd scripts && python create_winery_growth_analysis.py
```

### Winery Growth vs Real Estate Correlation

To analyze the correlation between winery development and real estate appreciation (gentrification analysis):

```bash
cd scripts && python create_winery_realestate_correlation.py
```

### Temporal Leading Indicator Analysis

To test if winery growth is a leading indicator for real estate appreciation (timing analysis):

```bash
cd scripts && python create_temporal_leading_indicator_analysis.py
```

### Command Line Options

The main script supports several options for different use cases:

```bash
# Run complete pipeline (default)
python main.py

# Only download data, skip visualizations
python main.py --download-only

# Only create visualizations (requires existing data)
python main.py --viz-only

# Skip data download, create visualizations only
python main.py --skip-download

# Show help
python main.py --help
```

### Running Individual Scripts

You can also run individual components:

```bash
# Download winery data
cd scripts && python download_berlin_wineries.py

# Create interactive map
cd scripts && python create_real_map_visualization.py

# Create heatmap visualizations
cd scripts && python create_winery_heatmap.py
cd scripts && python create_winery_heatmap_improved.py
```

## Data

The project focuses on wineries located within Berlin's geographical boundaries. The data includes:
- Winery names and locations
- Latitude and longitude coordinates
- Additional metadata about each establishment

Data is stored in the `data/` directory in both CSV and JSON formats for different use cases.

## Visualizations

The project generates several types of visualizations in the `outputs/` directory:

1. **Interactive Maps** (`berlin_wineries_real_map.html`): Real map visualizations using OpenStreetMap tiles with winery markers and heatmap overlays
2. **Basic Heatmap** (`berlin_wineries_heatmap.png`): Density maps showing concentration of wineries across Berlin
3. **Enhanced Heatmap** (`berlin_wineries_heatmap_improved.png`): Improved visualizations with better styling and additional information
4. **Density Map** (`berlin_winery_density_map.html`): True density analysis accounting for district area
5. **Growth Map** (`berlin_winery_growth_map.html`): 10-year growth patterns by district
6. **Recent Activity Map** (`berlin_recent_wineries_map.html`): Recently opened wineries analysis
7. **Correlation Map** (`berlin_winery_realestate_correlation_map.html`): Winery growth vs real estate appreciation overlay
8. **Temporal Analysis Charts** (`berlin_temporal_leading_indicator_analysis.png`): Time series analysis testing leading indicator hypothesis

## Requirements

- Python 3.8+
- pandas - Data manipulation and analysis
- folium - Interactive map generation
- matplotlib - Basic plotting and visualization
- seaborn - Statistical data visualization
- numpy - Numerical computations
- requests - HTTP requests for data download
- selenium - Web scraping capabilities

## Output

After running the analysis, you'll find:

- **Data files** in `data/` - Raw winery data in CSV and JSON formats
- **Interactive map** in `outputs/` - Open the HTML file in your browser to explore
- **Heatmap images** in `outputs/` - High-quality PNG visualizations

## Development

### Folder Organization

- `data/` - Contains all data files (CSV, JSON)
- `scripts/` - Individual analysis scripts for specific tasks
- `outputs/` - Generated visualizations and reports
- `main.py` - Orchestrates the entire analysis pipeline

### Adding New Analysis

To add new analysis scripts:

1. Create your script in the `scripts/` folder
2. Update paths to use `../data/` for input and `../outputs/` for output
3. Add the script to `main.py` if it should be part of the main pipeline

## License

See LICENSE file for details.
