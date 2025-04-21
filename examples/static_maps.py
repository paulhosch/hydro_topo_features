#!/usr/bin/env python
"""
Example script for creating static maps of hydro-topo features.

This script demonstrates how to use the hydro_topo_features package to create
static maps of various hydro-topological features from pre-processed data.

Run this script after you have processed data using the pipeline.
"""

import os
from pathlib import Path
import hydro_topo_features
from hydro_topo_features.visualization.static import plot_static_map
from hydro_topo_features.config import Config

def main():
    """Create static maps from processed data."""
    # Set the site ID and paths
    site_id = "EMSR728_AOI04"
    output_dir = Path("data/output")
    aoi_path = "test_data/aoi/danube/EMSR728_AOI04_DEL_PRODUCT_areaOfInterestA_v1.shp"
    
    # Define the output directories based on site ID
    site_dir = output_dir / site_id
    interim_dir = site_dir / "interim"
    processed_dir = site_dir / "processed"
    
    # Check if the directories exist
    if not interim_dir.exists() or not processed_dir.exists():
        print(f"Error: Output directories not found for site {site_id}")
        print(f"Make sure to run the pipeline first to generate the data.")
        return
    
    # Define paths to raster layers and their properties
    raster_configs = [
        {
            "path": str(interim_dir / "raw_dem.tif"),
            "name": "Raw DEM",
            "unit": "m",
            "vmin": 0,
            "vmax": 1000,
            "cmap": "terrain"
        },
        {
            "path": str(interim_dir / "osm_water_raster.tif"),
            "name": "OSM Water",
            "unit": "",
            "vmin": 0,
            "vmax": 1,
            "cmap": "Blues"
        },
        {
            "path": str(processed_dir / "hand.tif"),
            "name": "HAND",
            "unit": "m",
            "vmin": 0,
            "vmax": 100,
            "cmap": "viridis"
        },
        {
            "path": str(processed_dir / "slope.tif"),
            "name": "Slope",
            "unit": "degrees",
            "vmin": 0,
            "vmax": 45,
            "cmap": "YlOrRd"
        },
        {
            "path": str(processed_dir / "edtw.tif"),
            "name": "EDTW",
            "unit": "m",
            "vmin": 0,
            "vmax": 1000,
            "cmap": "plasma"
        }
    ]
    
    # Define output directories
    output_dirs = {
        "root": site_dir,
        "figures": site_dir / "figures",
        "static_figures": site_dir / "figures" / "static"
    }
    
    # Create directories if they don't exist
    for dir_path in output_dirs.values():
        os.makedirs(dir_path, exist_ok=True)
    
    # Create static maps for each raster
    print(f"Creating static maps for site {site_id}...")
    
    map_paths = []
    for cfg in raster_configs:
        # Skip if the file doesn't exist
        if not os.path.exists(cfg["path"]):
            print(f"Warning: Raster file not found: {cfg['path']}")
            continue
        
        print(f"Processing {cfg['name']}...")
        
        # Create static map
        map_path = plot_static_map(
            site_id=site_id,
            raster_path=cfg["path"],
            aoi_path=aoi_path,
            Name=cfg["name"],
            Unit=cfg["unit"],
            vmin=cfg["vmin"],
            vmax=cfg["vmax"],
            cmap=cfg["cmap"],
            output_dirs=output_dirs
        )
        
        map_paths.append(map_path)
        print(f"  Map saved to: {map_path}")
    
    print(f"Static maps created successfully!")
    print(f"Maps saved to: {output_dirs['static_figures']}")

if __name__ == "__main__":
    main() 