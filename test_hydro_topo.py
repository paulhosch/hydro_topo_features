#!/usr/bin/env python3
"""Test script for the hydro-topological features extraction package."""

import os
import argparse
import logging
from pathlib import Path

from hydro_topo_features.pipeline import run_pipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Run the hydro-topological features extraction pipeline."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Extract hydro-topological features from DEM and OSM data"
    )
    parser.add_argument(
        "--site-id", 
        type=str, 
        required=True, 
        help="Unique identifier for the site (e.g., 'danube')"
    )
    parser.add_argument(
        "--aoi-path", 
        type=str, 
        required=True, 
        help="Path to AOI shapefile"
    )
    parser.add_argument(
        "--dem-dir", 
        type=str, 
        required=True, 
        help="Path to directory containing DEM tiles"
    )
    parser.add_argument(
        "--output-dir", 
        type=str, 
        default="outputs", 
        help="Path for output files (default: 'outputs')"
    )
    parser.add_argument(
        "--static-maps", 
        action="store_true",
        help="Create static maps"
    )
    parser.add_argument(
        "--interactive-map", 
        action="store_true",
        help="Create interactive map"
    )
    args = parser.parse_args()

    # Check if required files exist
    aoi_path = Path(args.aoi_path)
    dem_dir = Path(args.dem_dir)
    output_dir = Path(args.output_dir)
    
    if not aoi_path.exists():
        logger.error(f"AOI file not found: {aoi_path}")
        return 1
    
    if not dem_dir.exists() or not any(dem_dir.glob("*.tif")):
        logger.error(f"No DEM tiles found in: {dem_dir}")
        return 1
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Run the pipeline
        outputs = run_pipeline(
            site_id=args.site_id,
            aoi_path=str(aoi_path),
            dem_tile_folder_path=str(dem_dir),
            output_path=str(output_dir),
            create_static_maps=args.static_maps,
            create_interactive_map=args.interactive_map
        )
        
        # Print output paths
        logger.info("Pipeline completed successfully")
        logger.info("Output files:")
        for key, path in outputs.items():
            logger.info(f"  {key}: {path}")
            
        return 0
            
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    exit(main()) 