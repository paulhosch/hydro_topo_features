#!/usr/bin/env python
"""
Example script for creating an interactive map with hydro-topo features.

This script demonstrates how to use the hydro_topo_features package to create
an interactive map with various hydro-topological features from pre-processed data.

Run this script after you have processed data using the pipeline.
"""

import os
from pathlib import Path
import hydro_topo_features
from hydro_topo_features.visualization.interactive import plot_interactive_map
from hydro_topo_features.config import Config

def main():
    """Create an interactive map from processed data."""
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
    
    # Define paths to raster layers
    raster_paths = [
        str(interim_dir / "raw_dem.tif"),
        str(interim_dir / "osm_water_raster.tif"),
        str(processed_dir / "hand.tif"),
        str(processed_dir / "slope.tif"),
        str(processed_dir / "edtw.tif")
    ]
    
    # Verify that all raster files exist
    missing_files = [path for path in raster_paths if not os.path.exists(path)]
    if missing_files:
        print(f"Error: The following raster files were not found:")
        for file in missing_files:
            print(f"  - {file}")
        return
    
    # Define output directories
    output_dirs = {
        "root": site_dir,
        "figures": site_dir / "figures",
        "interactive_figures": site_dir / "figures" / "interactive"
    }
    
    # Create directories if they don't exist
    for dir_path in output_dirs.values():
        os.makedirs(dir_path, exist_ok=True)
    
    # Create an interactive map
    print(f"Creating interactive map for site {site_id}...")
    
    # Customize visualization parameters
    names = ["Raw DEM", "OSM Water", "HAND", "Slope", "EDTW"]
    units = ["m", "", "m", "degrees", "m"]
    vmins = [0, 0, 0, 0, 0]
    vmaxs = [1000, 1, 100, 45, 1000]
    cmaps = ["terrain", "Blues", "viridis", "YlOrRd", "plasma"]
    
    # Plot interactive map
    map_path = plot_interactive_map(
        site_id=site_id,
        raster_paths=raster_paths,
        aoi_path=aoi_path,
        Name=names,
        Unit=units,
        vmin=vmins,
        vmax=vmaxs,
        cmap=cmaps,
        opacity=0.7,
        zoom_start=9,
        output_dirs=output_dirs
    )
    
    print(f"Interactive map created successfully!")
    print(f"Map saved to: {map_path}")
    print(f"Open this file in a web browser to view the interactive map.")

if __name__ == "__main__":
    main() 