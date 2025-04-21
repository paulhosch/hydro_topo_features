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
from pysheds.grid import Grid
from shapely.geometry import box
import rasterio
from rasterio.features import rasterize
from rasterio.transform import array_bounds
import pandas as pd

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
    raw_dem_path = output_dirs["interim"] / "raw_dem.tif"
    
    interim_dir = output_dirs["interim"]
    osm_vector_path = interim_dir / "osm_water_vector.gpkg"
    osm_raster_path = interim_dir / "osm_water_raster.tif"
    
    # 1. Merge DEM tiles
    logger.info("Merging DEM tiles...")
    merge_dem_tiles(dem_tile_folder_path, raw_dem_path)
    
    # 2. Extract water features from OpenStreetMap
    logger.info("Extracting water features from OpenStreetMap...")
    extract_osm_water_features(aoi_path, osm_vector_path, str(raw_dem_path))
    
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
            "crs": sources[0].crs,
            "nodata": config.DEM_PROCESSING["NODATA_VALUE"]
        })
        
        mosaic = mosaic / 100.0

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

def extract_osm_water_features(aoi_path: str, output_path: Path, dem_path: str) -> None:
    """
    Extract water features from OpenStreetMap within the AOI.
    
    Args:
        aoi_path: Path to AOI shapefile/geopackage
        output_path: Path to output water features
        dem_path: Path to DEM for grid initialization
    """
    # Create parent directory if it doesn't exist
    os.makedirs(output_path.parent, exist_ok=True)
    
    grid = Grid.from_raster(dem_path)

    # Read DEM
    raw_dem = grid.read_raster(dem_path)
    bbox = box(*raw_dem.bbox)
    
    all_features = []

    # Properly iterate through OSM_WATER_TAGS dictionary
    for category, tags in config.OSM_WATER_TAGS.items():
        for tag in tags:
            tag_dict = {category: tag}
            try:
                gdf = ox.features.features_from_polygon(bbox, tag_dict)
                print(f" Retrieved {len(gdf)} features for {tag_dict}")
                gdf.set_crs(epsg=4326, inplace=True)
                all_features.append(gdf)
            except Exception as e:
                print(f"⚠️  Failed for tags {tag_dict}: {e}")

    water_features = (
        gpd.GeoDataFrame(pd.concat(all_features, ignore_index=True), crs="EPSG:4326")
        if all_features else
        gpd.GeoDataFrame(columns=['geometry'], crs="EPSG:4326")
    )
    # Reproject to match DEM's CRS
    water_features = water_features.to_crs(raw_dem.crs)

    # === ✂️ Clip water features to DEM grid extent ===
    # Get the exact bounds from the raw_dem grid
    height, width = raw_dem.shape
    bounds = array_bounds(height, width, raw_dem.affine)
    clip_box = box(*bounds)

    water_clipped = gpd.clip(water_features, clip_box)

    # === 🧹 Filter to valid geometries and essential attributes ===
    valid_types = ['Polygon', 'MultiPolygon', 'LineString', 'MultiLineString']
    water_filtered = water_clipped[water_clipped.geometry.geom_type.isin(valid_types)]

    essential_cols = ['geometry', 'waterway', 'natural', 'landuse', 'name']
    cols_present = [col for col in essential_cols if col in water_filtered.columns]
    water_clean = water_filtered[cols_present]

    # Save to file
    water_clean.to_file(output_path, driver="GPKG")
    logger.info(f"Water features saved to: {output_path}")


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