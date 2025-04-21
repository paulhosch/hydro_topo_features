"""Configuration settings for the hydro-topological features package."""

from pathlib import Path

# --------------------------
# Path configurations
# --------------------------
# Default output directory structure
DEFAULT_OUTPUT_DIR = "outputs"  # Default output directory
DIRECTORY_STRUCTURE = {
    "RAW": "raw",         # Original data without processing
    "INTERIM": "interim", # Intermediate processing results
    "PROCESSED": "processed", # Final data products
    "FIGURES": "figures", # Visualizations
    "STATIC": "static",   # Static visualizations
    "INTERACTIVE": "interactive" # Interactive visualizations
}

# --------------------------
# Data processing parameters
# --------------------------
DEM_PROCESSING = {
    "BURN_DEPTH": 20,  # meters to burn streams into DEM
    "NODATA_VALUE": 0, # Value for no data
    "DEFAULT_CRS": "EPSG:4326", # WGS84
    "RASTERIZE_RESOLUTION": 30, # meters
}

# OSM water feature tags to extract
OSM_WATER_TAGS = {
    "natural": ["water"],
    "waterway": ["river", "stream", "canal"],
    "landuse": ["reservoir"]
}

# Feature computation parameters
FEATURE_PARAMS = {
    "HAND": {
        "min_slope": 0.00001,  # minimum slope for flow direction
        "routing": "d8"  # flow routing algorithm
    },
    "SLOPE": {
        "units": "degrees",  # or 'percent'
        "algorithm": "horn"  # Horn's method for slope calculation
    },
    "EDTW": {
        "max_distance": None,  # None for unlimited
        "units": "meters"
    }
}

# --------------------------
# Visualization parameters
# --------------------------
# Static plot configuration
STATIC_VIS = {
    "font": "Arial",
    "fontsize_title": 14,
    "fontsize_axes": 12,
    "fontsize_legend": 10,
    "fontsize_colorbar": 10,
    "colorbar_width": 0.05,
    "colorbar_height": 0.9,
    "aoi_color": "#797979",
    "aoi_linestyle": "--",
    "aoi_linewidth": 4,
    "show_grid": True,
    "show_lon_lat": True,
    "show_scale_bar": True,
    "scale_bar_length": 10,
    "scale_bar_color": "black",
    "scale_bar_unit": "km",
    "dpi": 300,
    "bbox_buffer": 0.05
}

# Interactive plot configuration
INTERACTIVE_VIS = {
    "zoom_start": 9,
    "opacity": 0.6,
    "colorbar_position": "bottomright",
    "aoi_color": "red",
    "aoi_weight": 2,
    "aoi_dash_array": "5, 5",
    "aoi_fill_opacity": 0.0,
    "layer_control": True
}

# Raster layer visualization settings
RASTER_VIS = {
    "raw_dem": {
        "name": "Raw DEM",
        "unit": "m",
        "vmin": 0,
        "vmax": 1000,
        "cmap": "terrain"
    },
    "burned_dem": {
        "name": "Burned DEM",
        "unit": "m",
        "vmin": 0,
        "vmax": 1000,
        "cmap": "terrain"
    },
    "osm_water": {
        "name": "OSM Water",
        "unit": "binary",
        "vmin": 0,
        "vmax": 1,
        "cmap": "Blues"
    },
    "hand": {
        "name": "HAND",
        "unit": "m",
        "vmin": 0,
        "vmax": 100,
        "cmap": "viridis"
    },
    "slope": {
        "name": "Slope",
        "unit": "degrees",
        "vmin": 0,
        "vmax": 45,
        "cmap": "YlOrRd"
    },
    "edtw": {
        "name": "EDTW",
        "unit": "m",
        "vmin": 0,
        "vmax": 1000,
        "cmap": "plasma"
    }
} 