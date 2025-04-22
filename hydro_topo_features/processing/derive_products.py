"""Functions for computing hydro-topological features."""

import os
import logging
from pathlib import Path
import numpy as np
import rasterio
from pysheds.grid import Grid
from scipy.ndimage import distance_transform_edt
from geopy.distance import geodesic
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
    
    try:
        # Read water raster
        with rasterio.open(osm_water_raster) as src:
            transform = src.transform
            crs = src.crs
            water = src.read(1)
            nodata = src.nodata

            # Handle nodata values if present
            if nodata is not None:
                water = np.ma.masked_equal(water, nodata)
                water = np.ma.filled(water, 0)  # Fill nodata with 0 (non-water)

            # Get pixel width and height in degrees
            pixel_width_deg = abs(transform.a)
            pixel_height_deg = abs(transform.e)

            # Center of the raster to estimate latitude
            center_lat = src.bounds.top - (src.height // 2) * pixel_height_deg
            center_lon = src.bounds.left + (src.width // 2) * pixel_width_deg

            # Approximate meters per pixel using geodesic distance
            pixel_width_m = geodesic(
                (center_lat, center_lon),
                (center_lat, center_lon + pixel_width_deg)
            ).meters

            pixel_height_m = geodesic(
                (center_lat, center_lon),
                (center_lat + pixel_height_deg, center_lon)
            ).meters

            # Use average for sampling parameter
            pixel_size = (pixel_height_m + pixel_width_m) / 2
            logger.info(f"Pixel size: approximately {pixel_size:.2f} meters")

        # Create water mask (1 for water, 0 for non-water)
        # OSM water raster has value 1 for water, 0 for non-water
        water_mask = (water == 1).astype(np.uint8)
        
        # Compute EDTW (distance from each non-water pixel to nearest water pixel)
        logger.info("Computing distance transform")
        # Note: distance_transform_edt computes distance from 0s to nearest 1s
        # So we need to invert the mask (1 - water_mask)
        edtw = distance_transform_edt(1 - water_mask) * pixel_size
        
        # Get max value for informational purposes
        max_dist = np.max(edtw)
        logger.info(f"Maximum distance to water: {max_dist:.2f} meters")
        
        # Save distance raster to file
        with rasterio.open(
            edtw_path,
            'w',
            driver='GTiff',
            height=edtw.shape[0],
            width=edtw.shape[1],
            count=1,
            dtype='float32',
            crs=crs,
            transform=transform,
            nodata=np.finfo('float32').max
        ) as dst:
            dst.write(edtw.astype(np.float32), 1)
        
        logger.info("EDTW computation completed")
        return str(edtw_path)
        
    except Exception as e:
        logger.error(f"Error computing EDTW: {str(e)}")
        raise 