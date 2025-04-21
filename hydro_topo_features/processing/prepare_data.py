"""Functions for preparing input data for hydro-topological feature computation."""

import os
import logging
from pathlib import Path
import rasterio
import geopandas as gpd
import pandas as pd
import osmnx as ox
from rasterio.merge import merge
from rasterio.warp import reproject, Resampling
from rasterio.features import rasterize
from rasterio.transform import array_bounds
import numpy as np
from shapely.geometry import box
from pysheds.grid import Grid
from .. import config

logger = logging.getLogger(__name__)

def prepare_data(site_id: str, aoi_path: str, dem_tile_folder_path: str) -> dict:
    """
    Prepare input data for hydro-topological feature computation.
    
    Args:
        site_id (str): Unique identifier for the site
        aoi_path (str): Path to the AOI shapefile/geopackage
        dem_tile_folder_path (str): Path to folder containing DEM tiles
        
    Returns:
        dict: Dictionary containing paths to prepared files
    """
    logger.info(f"Preparing data for site: {site_id}")
    
    # Create output directories
    site_dir = config.OUTPUT_DIR / site_id
    interim_dir = site_dir / config.INTERIM_DIR
    os.makedirs(interim_dir, exist_ok=True)
    
    # Output paths
    raw_dem_path = interim_dir / "raw_dem.tif"
    osm_water_vector_path = interim_dir / "osm_water_vector.gpkg"
    osm_water_raster_path = interim_dir / "osm_water_raster.tif"
    
    # Load and process AOI
    aoi = gpd.read_file(aoi_path)
    if aoi.crs != config.DEFAULT_CRS:
        aoi = aoi.to_crs(config.DEFAULT_CRS)
    
    # Merge DEM tiles if needed
    dem_tiles = list(Path(dem_tile_folder_path).glob("*.tif"))
    if len(dem_tiles) > 1:
        logger.info("Merging DEM tiles...")
        # Keep track of the first tile's metadata
        with rasterio.open(dem_tiles[0]) as first:
            first_meta = first.meta.copy()
        
        # Open all tiles and merge them
        sources = [rasterio.open(tile) for tile in dem_tiles]
        try:
            mosaic, transform = merge(sources)
            
            # Update metadata for the merged raster
            first_meta.update({
                "height": mosaic.shape[1],
                "width": mosaic.shape[2],
                "transform": transform
            })
            
            # Write merged DEM
            with rasterio.open(raw_dem_path, 'w', **first_meta) as dst:
                dst.write(mosaic)
        finally:
            # Make sure to close all source files
            for src in sources:
                src.close()
    else:
        # Just copy single DEM tile
        with rasterio.open(dem_tiles[0]) as src:
            with rasterio.open(raw_dem_path, 'w', **src.meta) as dst:
                dst.write(src.read())
    
    # Convert DEM from cm to meters if needed
    with rasterio.open(raw_dem_path, 'r+') as src:
        data = src.read(1)
        if np.mean(data) > 1000:  # Simple heuristic to detect cm units
            logger.info("Converting DEM from centimeters to meters")
            data = data / 100
            src.write(data, 1)
    
    # Initialize grid from DEM for proper extent
    logger.info("Initializing grid from DEM...")
    grid = Grid.from_raster(str(raw_dem_path))
    raw_dem = grid.read_raster(str(raw_dem_path))
    
    # Get bounding box from DEM
    height, width = raw_dem.shape
    bounds = array_bounds(height, width, raw_dem.affine)
    bbox = box(*bounds)
    
    # Extract water features using multiple OSM tags
    logger.info("Downloading OSM water features...")
    water_tags_list = [
        {"natural": "water"},
        {"waterway": ["river", "stream", "canal"]},
        {"landuse": "reservoir"}
    ]
    
    all_features = []
    for tags in water_tags_list:
        try:
            gdf = ox.features_from_polygon(bbox, tags)
            logger.info(f"Retrieved {len(gdf)} features for {tags}")
            gdf.set_crs(epsg=4326, inplace=True)
            all_features.append(gdf)
        except Exception as e:
            logger.warning(f"Failed to retrieve features for tags {tags}: {e}")
    
    # Combine all water features
    water_features = (
        gpd.GeoDataFrame(pd.concat(all_features, ignore_index=True), crs="EPSG:4326")
        if all_features else
        gpd.GeoDataFrame(columns=['geometry'], crs="EPSG:4326")
    )
    # Reproject to match DEM's CRS
    water_features = water_features.to_crs(raw_dem.crs)
    
    # Clip water features to DEM extent
    height, width = raw_dem.shape
    bounds = array_bounds(height, width, raw_dem.affine)
    clip_box = box(*bounds)

    water_clipped = gpd.clip(water_features, clip_box)
    
    # Filter to valid geometries and essential attributes
    valid_types = ['Polygon', 'MultiPolygon', 'LineString', 'MultiLineString']
    water_filtered = water_clipped[water_clipped.geometry.geom_type.isin(valid_types)]
    
    essential_cols = ['geometry', 'waterway', 'natural', 'landuse', 'name']
    cols_present = [col for col in essential_cols if col in water_filtered.columns]
    water_clean = water_filtered[cols_present]
    
    # Save cleaned water features vector
    water_clean.to_file(osm_water_vector_path, driver="GPKG")
    
    # Rasterize water features
    logger.info("Rasterizing water features...")

    target_crs = raw_dem.crs  # CRS of the DEM
    if water_clean.crs != target_crs:
        print(f"🔁 Reprojecting water geometries from {water_clean.crs} to {target_crs}")
        water_clean = water_clean.to_crs(target_crs)

    # Convert all water features to binary (1 for water, 0 for no water)
    geometry_list = [(geom, 1) for geom in water_clean.geometry if geom.is_valid]
    
    water_raster = rasterize(
        shapes=geometry_list,
        out_shape=raw_dem.shape,
        transform=raw_dem.affine,
        fill=0,
        dtype='uint8',
        all_touched=False
    )
    
    # Save water raster
    raster_meta = {
        'driver': 'GTiff',
        'height': height,
        'width': width,
        'count': 1,
        'dtype': 'uint8',
        'crs': raw_dem.crs,
        'transform': raw_dem.affine
    }

    with rasterio.open(osm_water_raster_path, 'w', **raster_meta) as dst:
        dst.write(water_raster, 1)
    
    logger.info("Data preparation completed")
    return {
        "raw_dem": str(raw_dem_path),
        "osm_water_vector": str(osm_water_vector_path),
        "osm_water_raster": str(osm_water_raster_path)
    } 