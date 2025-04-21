"""Functions for preparing input data for hydro-topological feature extraction."""

import os
import logging
import numpy as np
import rasterio
from pathlib import Path
from rasterio.merge import merge
from typing import Dict, List, Tuple, Any
import geopandas as gpd
import osmnx as ox
from .. import config

logger = logging.getLogger(__name__)

def prepare_input_data(
    site_id: str,
    aoi_path: str,
    dem_tile_folder_path: str,
    output_dirs: Dict[str, Path]
) -> Dict[str, str]:
    """
    Prepare input data for hydro-topological feature extraction.
    
    This function performs the following steps:
    1. Merges DEM tiles into a single DEM
    2. Extracts water features from OpenStreetMap
    3. Rasterizes water features to match DEM resolution
    
    Args:
        site_id: Unique identifier for the site
        aoi_path: Path to AOI shapefile/geopackage
        dem_tile_folder_path: Path to folder containing DEM tiles
        output_dirs: Dictionary of output directories
        
    Returns:
        Dictionary of output paths (raw_dem, osm_water_vector, osm_water_raster)
    """
    logger.info(f"Preparing input data for site: {site_id}")
    
    # Define output file paths
    raw_dem_path = output_dirs["raw"] / "raw_dem.tif"
    
    interim_dir = output_dirs["interim"]
    osm_vector_path = interim_dir / "osm_water_vector.gpkg"
    osm_raster_path = interim_dir / "osm_water_raster.tif"
    
    # 1. Merge DEM tiles
    logger.info("Merging DEM tiles...")
    merge_dem_tiles(dem_tile_folder_path, raw_dem_path)
    
    # 2. Extract water features from OpenStreetMap
    logger.info("Extracting water features from OpenStreetMap...")
    extract_osm_water_features(aoi_path, osm_vector_path)
    
    # 3. Rasterize water features
    logger.info("Rasterizing water features...")
    rasterize_water_features(raw_dem_path, osm_vector_path, osm_raster_path)
    
    logger.info("Input data preparation completed")
    return {
        "raw_dem": str(raw_dem_path),
        "osm_water_vector": str(osm_vector_path),
        "osm_water_raster": str(osm_raster_path)
    }

def merge_dem_tiles(dem_tile_folder_path: str, output_path: Path) -> None:
    """
    Merge multiple DEM tiles into a single DEM.
    
    Args:
        dem_tile_folder_path: Path to folder containing DEM tiles
        output_path: Path to output merged DEM
    """
    # Create parent directory if it doesn't exist
    os.makedirs(output_path.parent, exist_ok=True)
    
    # Get list of DEM tiles
    dem_tile_folder = Path(dem_tile_folder_path)
    dem_tiles = list(dem_tile_folder.glob("*.tif"))
    
    if not dem_tiles:
        raise FileNotFoundError(f"No DEM tiles found in: {dem_tile_folder}")
    
    logger.info(f"Found {len(dem_tiles)} DEM tiles")
    
    # Open all DEM tiles
    sources = []
    for tile in dem_tiles:
        try:
            src = rasterio.open(tile)
            sources.append(src)
        except Exception as e:
            logger.error(f"Error opening DEM tile {tile}: {str(e)}")
    
    if not sources:
        raise ValueError("No valid DEM tiles could be opened")
    
    # Merge tiles
    try:
        mosaic, out_transform = merge(sources)
        
        # Get metadata from first tile
        out_meta = sources[0].meta.copy()
        
        # Update metadata
        out_meta.update({
            "driver": "GTiff",
            "height": mosaic.shape[1],
            "width": mosaic.shape[2],
            "transform": out_transform,
            "dtype": "float32",
            "nodata": config.DEM_PROCESSING["NODATA_VALUE"]
        })
        
        # Write merged DEM
        with rasterio.open(output_path, "w", **out_meta) as dest:
            dest.write(mosaic.astype('float32'))
        
        logger.info(f"Merged DEM saved to: {output_path}")
        
    except Exception as e:
        logger.error(f"Error merging DEM tiles: {str(e)}")
        raise
    
    finally:
        # Close all sources
        for src in sources:
            src.close()

def extract_osm_water_features(aoi_path: str, output_path: Path) -> None:
    """
    Extract water features from OpenStreetMap within the AOI.
    
    Args:
        aoi_path: Path to AOI shapefile/geopackage
        output_path: Path to output water features
    """
    # Create parent directory if it doesn't exist
    os.makedirs(output_path.parent, exist_ok=True)
    
    # Read AOI
    aoi = gpd.read_file(aoi_path)
    
    # Convert to GeoDataFrame if needed
    if not isinstance(aoi, gpd.GeoDataFrame):
        raise ValueError(f"AOI file is not a valid GeoDataFrame: {aoi_path}")
    
    # Convert to WGS84 if not already
    if aoi.crs != "EPSG:4326":
        aoi = aoi.to_crs("EPSG:4326")
    
    # Get bounding box
    bounds = aoi.total_bounds
    
    # Extract water features from OSM
    tags = config.OSM_WATER_TAGS
    
    try:
        polygons = ox.features.features_from_bbox(
            north=bounds[3], south=bounds[1],
            east=bounds[2], west=bounds[0],
            tags=tags
        )
        
        # Check if any features were found
        if polygons is None or polygons.empty:
            logger.warning("No water features found in AOI")
            # Create empty GeoDataFrame
            polygons = gpd.GeoDataFrame(geometry=[], crs="EPSG:4326")
        
        # Clip to AOI
        water_features = gpd.clip(polygons, aoi)
        
        # Save to file
        water_features.to_file(output_path, driver="GPKG")
        logger.info(f"Water features saved to: {output_path}")
        
    except Exception as e:
        logger.error(f"Error extracting water features: {str(e)}")
        raise

def rasterize_water_features(dem_path: str, water_path: str, output_path: Path) -> None:
    """
    Rasterize water features to match DEM resolution.
    
    Args:
        dem_path: Path to DEM
        water_path: Path to water features
        output_path: Path to output rasterized water features
    """
    # Create parent directory if it doesn't exist
    os.makedirs(output_path.parent, exist_ok=True)
    
    try:
        # Read water features
        water_features = gpd.read_file(water_path)
        
        if water_features.empty:
            logger.warning("No water features to rasterize")
            # Create empty raster with DEM metadata
            with rasterio.open(dem_path) as src:
                meta = src.meta.copy()
                meta.update({
                    "dtype": "uint8",
                    "nodata": 0
                })
                
                with rasterio.open(output_path, "w", **meta) as dest:
                    dest.write(np.zeros((1, meta["height"], meta["width"]), dtype=np.uint8))
                    
            logger.info(f"Empty water raster saved to: {output_path}")
            return
        
        # Read DEM metadata
        with rasterio.open(dem_path) as src:
            meta = src.meta.copy()
            transform = src.transform
            height = src.height
            width = src.width
        
        # Convert water features to DEM CRS if needed
        if water_features.crs != meta["crs"]:
            water_features = water_features.to_crs(meta["crs"])
        
        # Rasterize water features
        from rasterio.features import geometry_mask
        
        # Create mask from water features
        geoms = water_features.geometry.values
        mask = geometry_mask(geoms, out_shape=(height, width), transform=transform, invert=True)
        
        # Convert mask to uint8
        water_raster = mask.astype(np.uint8)
        
        # Update metadata
        meta.update({
            "dtype": "uint8",
            "nodata": 0,
            "count": 1
        })
        
        # Write rasterized water features
        with rasterio.open(output_path, "w", **meta) as dest:
            dest.write(water_raster[np.newaxis, :, :])
        
        logger.info(f"Rasterized water features saved to: {output_path}")
        
    except Exception as e:
        logger.error(f"Error rasterizing water features: {str(e)}")
        raise 