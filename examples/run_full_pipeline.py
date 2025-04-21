#!/usr/bin/env python
"""
Example script for running the complete hydro-topo features extraction pipeline.

This script demonstrates how to use the hydro_topo_features package to:
1. Merge DEM tiles
2. Extract water features from OpenStreetMap
3. Generate hydro-topological features (HAND, Slope, EDTW)
4. Create visualizations

This is the most complete example of using the package.
"""

import os
from pathlib import Path
import hydro_topo_features
from hydro_topo_features.pipeline import run_pipeline
from hydro_topo_features.config import Config

def main():
    """Run the full hydro-topo features extraction pipeline."""
    print("Starting hydro-topo features extraction pipeline...")
    
    # Set the site ID and paths
    site_id = "EMSR728_AOI04"
    aoi_path = "test_data/aoi/danube/EMSR728_AOI04_DEL_PRODUCT_areaOfInterestA_v1.shp"
    dem_dir = "test_data/dem_tiles/danube"
    output_dir = "data/output"
    
    # Check if the input files exist
    if not os.path.exists(aoi_path):
        print(f"Error: AOI file not found: {aoi_path}")
        return
        
    if not os.path.exists(dem_dir):
        print(f"Error: DEM directory not found: {dem_dir}")
        return
    
    dem_files = [f for f in os.listdir(dem_dir) if f.endswith('.tif')]
    if not dem_files:
        print(f"Error: No DEM tiles found in {dem_dir}")
        return
    
    print(f"Found {len(dem_files)} DEM tiles in {dem_dir}:")
    for dem_file in dem_files:
        print(f"  - {dem_file}")
        
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Load default configuration
    config = Config()
    
    # Customize configuration if needed
    config.raster_vis['raw_dem']['vmin'] = 0
    config.raster_vis['raw_dem']['vmax'] = 1000
    
    # Print important configuration settings
    print("\nConfiguration:")
    print(f"  DEM no-data value: {config.dem_processing['NODATA_VALUE']}")
    print(f"  HAND minimum slope: {config.feature_params['HAND']['min_slope']}")
    print(f"  HAND routing method: {config.feature_params['HAND']['routing']}")
    
    # Run the pipeline
    print("\nRunning pipeline...")
    outputs = run_pipeline(
        site_id=site_id,
        aoi_path=aoi_path,
        dem_tile_folder_path=dem_dir,
        output_path=output_dir,
        create_static_maps=True,
        create_interactive_map=True
    )
    
    # Print the outputs
    print("\nPipeline completed successfully!")
    print("\nOutput files:")
    for key, path in outputs.items():
        print(f"  {key}: {path}")
    
    # Print instructions for viewing the outputs
    print("\nYou can view the static maps in the following directory:")
    print(f"  {os.path.join(output_dir, site_id, 'figures', 'static')}")
    
    print("\nYou can view the interactive map by opening the following file in a web browser:")
    if "interactive_map" in outputs:
        print(f"  {outputs['interactive_map']}")
    else:
        print("  No interactive map was generated.")
    
    print("\nYou can use the examples/interactive_map.py and examples/static_maps.py scripts")
    print("to create additional visualizations from the generated data.")

if __name__ == "__main__":
    main() 