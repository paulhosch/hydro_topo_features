"""Configuration settings for the hydro-topological features package."""

from pathlib import Path
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union

# --------------------------
# General settings
# --------------------------
# Project name and version
PROJECT_NAME = "Hydro-Topo Features"
PROJECT_VERSION = "0.1.4"

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
    "fontsize_title": 16,
    "fontsize_axes": 16,
    "fontsize_legend": 16,
    "fontsize_colorbar": 16,
    "colorbar_width": 0.1,
    "colorbar_height": 1,
    "aoi_color": "#d45e00",
    "aoi_linestyle": "--",
    "aoi_linewidth": 3,
    "show_grid": True,
    "show_lon_lat": True,
    "show_scale_bar": True,
    "scale_bar_length": 20,
    "scale_bar_color": "black",
    "scale_bar_unit": "km",
    "dpi": 300,
    "bbox_buffer": 0.05
}

# Interactive plot configuration
INTERACTIVE_VIS = {
    "zoom_start": 9,
    "opacity": 1,
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
        "vmax": 200,
        "cmap": "terrain"
    },
    "slope": {
        "name": "Slope",
        "unit": "°",
        "vmin": 0,
        "vmax": 90,
        "cmap": "viridis"
    },
    "edtw": {
        "name": "EDTW",
        "unit": "m",
        "vmin": 0,
        "vmax": 2000,
        "cmap": "viridis"
    }
}

@dataclass
class Paths:
    """Configuration class for file paths"""
    dem: str = None
    aoi: str = None
    output_dir: str = DEFAULT_OUTPUT_DIR

@dataclass
class Config:
    """Main configuration class for hydro-topographical feature extraction"""
    # Project information
    project_name: str = PROJECT_NAME
    project_version: str = PROJECT_VERSION
    
    # Paths and directory structure
    paths: Paths = field(default_factory=Paths)
    output_dir: Path = Path(DEFAULT_OUTPUT_DIR)
    directory_structure: Dict[str, str] = field(default_factory=lambda: DIRECTORY_STRUCTURE)
    
    # Processing parameters
    dem_processing: Dict[str, Any] = field(default_factory=lambda: DEM_PROCESSING)
    osm_water_tags: Dict[str, List[str]] = field(default_factory=lambda: OSM_WATER_TAGS)
    feature_params: Dict[str, Dict[str, Any]] = field(default_factory=lambda: FEATURE_PARAMS)
    
    # Visualization parameters
    static_vis: Dict[str, Any] = field(default_factory=lambda: STATIC_VIS)
    interactive_vis: Dict[str, Any] = field(default_factory=lambda: INTERACTIVE_VIS)
    raster_vis: Dict[str, Dict[str, Any]] = field(default_factory=lambda: RASTER_VIS)

    def __post_init__(self):
        """Initialize the output directory structure"""
        self.OUTPUT_DIR = self.output_dir
        self.PROJECT_NAME = self.project_name
        self.PROJECT_VERSION = self.project_version
        
        # Create other properties for easy access
        self.DEM_PROCESSING = self.dem_processing
        self.OSM_WATER_TAGS = self.osm_water_tags
        self.FEATURE_PARAMS = self.feature_params
        self.STATIC_VIS = self.static_vis
        self.INTERACTIVE_VIS = self.interactive_vis
        self.RASTER_VIS = self.raster_vis
        self.DIRECTORY_STRUCTURE = self.directory_structure 