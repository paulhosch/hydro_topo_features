"""Functions for computing hydro-topological features."""

import os
import logging
from pathlib import Path
import numpy as np
import rasterio
from pysheds.grid import Grid
from scipy.ndimage import distance_transform_edt
from typing import Dict
from .. import config

logger = logging.getLogger(__name__)

def get_osm_hand(
    site_id: str,
    raw_dem: str,
    osm_water_raster: str,
    burned_dem: str,
    output_dirs: Dict[str, Path]
) -> str:
    """
    Compute Height Above Nearest Drainage (HAND) using OSM water features.
    
    Args:
        site_id: Unique identifier for the site
        raw_dem: Path to raw DEM
        osm_water_raster: Path to rasterized water features
        burned_dem: Path to burned DEM
        output_dirs: Dictionary of output directories
        
    Returns:
        Path to HAND raster
    """
    logger.info(f"Computing HAND for site: {site_id}")
    
    # Output path
    hand_path = output_dirs["processed"] / "hand.tif"
    
    # Initialize grid
    grid = Grid.from_raster(raw_dem)
    
    # Read raster data
    raw_dem_data = grid.read_raster(raw_dem)
    burned_dem_data = grid.read_raster(burned_dem)
    osm_water = grid.read_raster(osm_water_raster)
    osm_water = grid.view(osm_water, nodata_out=0)

    # Fill pits in DEM
    pit_filled_dem = grid.fill_pits(burned_dem_data)

    # Fill depressions in DEM
    logger.info("Filling depressions in DEM...")
    flooded_dem = grid.fill_depressions(pit_filled_dem)
        
    # Resolve flats in DEM
    logger.info("Resolving flats in DEM...")
    inflated_dem = grid.resolve_flats(flooded_dem)

    # Compute flow direction
    logger.info("Computing flow direction")
    dirmap = (64, 128, 1, 2, 4, 8, 16, 32)
    fdir = grid.flowdir(inflated_dem, dirmap=dirmap, flats=-1, pits=-2, nodata_out=0)
    
    # Compute flow accumulation
    flow_accumulation = grid.accumulation(fdir)

    # Compute HAND
    logger.info("Computing HAND values")
    hand = grid.compute_hand(fdir, raw_dem_data, osm_water > 0)
    
    # Save HAND raster
    output_raster = grid.view(hand)
    # Get original DEM metadata
    with rasterio.open(raw_dem) as src:
        dem_meta = src.meta.copy()

    # Update metadata for writing
    dem_meta.update({
        'dtype': 'float32',
        'nodata': np.nan,
        'count': 1
    })

    # Write DEM to GeoTIFF
    with rasterio.open(hand_path, 'w', **dem_meta) as dst:
        dst.write(output_raster.astype(np.float32), 1)
        logger.info("HAND computation completed")
    
    return str(hand_path)

def get_slope(
    site_id: str,
    raw_dem: str,
    output_dirs: Dict[str, Path]
) -> str:
    """
    Compute slope from DEM.
    
    Args:
        site_id: Unique identifier for the site
        raw_dem: Path to raw DEM
        output_dirs: Dictionary of output directories
        
    Returns:
        Path to slope raster
    """
    logger.info(f"Computing slope for site: {site_id}")
    
    # Output path
    slope_path = output_dirs["processed"] / "slope.tif"
    
    # Initialize grid and read DEM
    grid = Grid()
    dem = grid.read_raster(raw_dem)
    
    # Compute slope
    logger.info("Computing slope values")
    slope_params = config.FEATURE_PARAMS["SLOPE"]
    if slope_params["algorithm"] == 'horn':
        dy, dx = np.gradient(dem)
        slope = np.arctan(np.sqrt(dy**2 + dx**2))
        if slope_params["units"] == 'degrees':
            slope = np.degrees(slope)
        elif slope_params["units"] == 'percent':
            slope = np.tan(slope) * 100
    
    # Save slope raster
    with rasterio.open(raw_dem) as src:
        meta = src.meta.copy()
    
    meta.update({
        "dtype": "float32",
        "nodata": config.DEM_PROCESSING["NODATA_VALUE"]
    })
    
    with rasterio.open(slope_path, 'w', **meta) as dst:
        dst.write(slope.astype('float32'), 1)
    
    logger.info("Slope computation completed")
    return str(slope_path)

def get_edtw(
    site_id: str,
    osm_water_raster: str,
    output_dirs: Dict[str, Path]
) -> str:
    """
    Compute Euclidean Distance to Water (EDTW).
    
    Args:
        site_id: Unique identifier for the site
        osm_water_raster: Path to rasterized water features
        output_dirs: Dictionary of output directories
        
    Returns:
        Path to EDTW raster
    """
    logger.info(f"Computing EDTW for site: {site_id}")
    
    # Output path
    edtw_path = output_dirs["processed"] / "edtw.tif"
    
    # Read water raster
    with rasterio.open(osm_water_raster) as src:
        water = src.read(1)
        meta = src.meta.copy()
        pixel_size = src.res[0]  # assuming square pixels
    
    # Compute EDTW
    logger.info("Computing distance transform")
    edtw_params = config.FEATURE_PARAMS["EDTW"]
    edtw = distance_transform_edt(water == 0) * pixel_size
    
    if edtw_params["max_distance"] is not None:
        edtw = np.minimum(edtw, edtw_params["max_distance"])
    
    # Save EDTW raster
    meta.update({
        "dtype": "float32",
        "nodata": config.DEM_PROCESSING["NODATA_VALUE"]
    })
    
    with rasterio.open(edtw_path, 'w', **meta) as dst:
        dst.write(edtw.astype('float32'), 1)
    
    logger.info("EDTW computation completed")
    return str(edtw_path) 