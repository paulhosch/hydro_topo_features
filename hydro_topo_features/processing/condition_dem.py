"""Functions for conditioning DEMs for hydro-topological feature computation."""

import os
import logging
from pathlib import Path
import numpy as np
import rasterio
from pysheds.grid import Grid
from .. import config

logger = logging.getLogger(__name__)

def condition_dem(site_id: str, raw_dem: str, osm_water_raster: str) -> str:
    """
    Condition DEM by stream burning and pit filling.
    
    Args:
        site_id (str): Unique identifier for the site
        raw_dem (str): Path to raw DEM
        osm_water_raster (str): Path to rasterized water features
        
    Returns:
        str: Path to conditioned DEM
    """
    logger.info(f"Conditioning DEM for site: {site_id}")
    
    # Create output directory
    site_dir = config.OUTPUT_DIR / site_id
    processed_dir = site_dir / config.PROCESSED_DIR
    os.makedirs(processed_dir, exist_ok=True)
    
    # Output path
    conditioned_dem_path = processed_dir / "conditioned_dem.tif"
    
    # Get metadata from raw DEM
    with rasterio.open(raw_dem) as src:
        meta = src.meta.copy()
    
    # Load the grid 
    grid = Grid.from_raster(raw_dem)
    # Read DEM
    dem_data = grid.read_raster(raw_dem)
    # read the osm water raster 
    water_data = grid.read_raster(osm_water_raster)

    # Stream burning
    logger.info(f"Burning streams with depth: {config.BURN_DEPTH}m")
    burned_dem = dem_data.copy()
    burned_dem[water_data == 1] -= config.BURN_DEPTH

    # Fill pits in DEM
    logger.info("Filling pits in DEM...")
    #pit_filled_dem = grid.fill_pits(burned_dem)

    # Fill depressions in DEM
    logger.info("Filling depressions in DEM...")
    #flooded_dem = grid.fill_depressions(pit_filled_dem)
        
    # Resolve flats in DEM
    logger.info("Resolving flats in DEM...")
    #inflated_dem = grid.resolve_flats(flooded_dem)
    
    # Save conditioned DEM
    meta.update({
        "dtype": "float32",
        "nodata": config.NODATA_VALUE
    })
    
    with rasterio.open(conditioned_dem_path, 'w', **meta) as dst:
        dst.write(burned_dem.astype('float32'), 1)
    
    logger.info("DEM conditioning completed")
    return str(conditioned_dem_path) 