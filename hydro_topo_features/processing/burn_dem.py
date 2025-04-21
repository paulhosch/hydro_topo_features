"""Functions for burning streams into DEMs."""

import os
import logging
import numpy as np
import rasterio
from typing import Dict
from pathlib import Path
from .. import config

logger = logging.getLogger(__name__)

def burn_streams(
    site_id: str,
    raw_dem: str,
    osm_water_raster: str,
    output_dirs: Dict[str, Path]
) -> str:
    """
    Burn streams into the DEM for improved hydrological modeling.
    
    Args:
        site_id: Unique identifier for the site
        raw_dem: Path to raw DEM
        osm_water_raster: Path to rasterized water features
        output_dirs: Dictionary of output directories
        
    Returns:
        Path to burned DEM
    """
    logger.info(f"Burning streams into DEM for site: {site_id}")
    
    # Output path
    burned_dem_path = output_dirs["processed"] / "burned_dem.tif"
    
    # Read raw DEM
    with rasterio.open(raw_dem) as src:
        dem_data = src.read(1)
        meta = src.meta.copy()
        
        # Handle NoData values
        if src.nodata is not None:
            mask = dem_data == src.nodata
            dem_data = np.ma.masked_array(dem_data, mask=mask)
    
    # Read water raster
    with rasterio.open(osm_water_raster) as src:
        water_data = src.read(1)
        
        # Handle NoData values
        if src.nodata is not None:
            water_mask = water_data == src.nodata
            water_data = np.ma.masked_array(water_data, mask=water_mask)
    
    # Burn streams by lowering elevation at water pixels
    burn_depth = config.DEM_PROCESSING["BURN_DEPTH"]
    burned_dem = dem_data.copy()
    burned_dem[water_data > 0] -= burn_depth
    
    # Convert back to array for writing
    if isinstance(burned_dem, np.ma.MaskedArray):
        burned_dem = burned_dem.filled(meta.get('nodata', config.DEM_PROCESSING["NODATA_VALUE"]))
    
    # Write burned DEM
    meta.update({
        "dtype": "float32",
        "nodata": config.DEM_PROCESSING["NODATA_VALUE"]
    })
    
    with rasterio.open(burned_dem_path, 'w', **meta) as dst:
        dst.write(burned_dem.astype('float32'), 1)
    
    logger.info(f"Stream burning completed. Result saved to: {burned_dem_path}")
    return str(burned_dem_path) 