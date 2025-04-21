"""Test script for the hydro-topological features pipeline."""

import os
from pathlib import Path
import logging

from hydro_topo_features.pipeline import run_pipeline
from hydro_topo_features.visualization.static import plot_static_map
from hydro_topo_features.visualization.interactive import plot_interactive_map
from hydro_topo_features import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_visualizations(site_id: str, aoi_path: Path):
    """Create static and interactive visualizations."""
    # Set paths
    site_dir = config.OUTPUT_DIR / site_id
    interim_dir = site_dir / config.INTERIM_DIR
    processed_dir = site_dir / config.PROCESSED_DIR
    
    # Paths to raster files
    osm_water_raster = interim_dir / "osm_water_raster.tif"
    raw_dem = interim_dir / "raw_dem.tif"
    hand = processed_dir / "osm_hand.tif"
    slope = processed_dir / "slope.tif"
    edtw = processed_dir / "edtw.tif"
    
    # Create static map for OSM water
    logger.info("Creating static map for OSM water raster")
    cfg = config.RASTER_VIS_CONFIG['osm_water']
    plot_static_map(
        site_id=site_id,
        raster_path=str(osm_water_raster),
        aoi_path=str(aoi_path),
        Name=cfg['name'],
        Unit=cfg['unit'],
        vmin=cfg['vmin'],
        vmax=cfg['vmax'],
        cmap=cfg['cmap']
    )
    
    # Create interactive map with all layers
    logger.info("Creating interactive map with all layers")
    raster_paths = [
        str(raw_dem),
        str(osm_water_raster),
        str(hand),
        str(slope),
        str(edtw)
    ]
    plot_interactive_map(
        site_id=site_id,
        raster_paths=raster_paths,
        aoi_path=str(aoi_path)
    )

def main():
    # Input paths
    data_dir = Path("./example_data")
    aoi_path = data_dir / 'aoi/danube/EMSR728_AOI04_DEL_PRODUCT_areaOfInterestA_v1.shp'
    dem_dir = data_dir / 'dem_tiles/danube'
    
    # Set output directory in config
    config.OUTPUT_DIR = Path("./example_output_dir")
    
    # Create necessary directories
    os.makedirs(aoi_path.parent, exist_ok=True)
    os.makedirs(dem_dir, exist_ok=True)
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    
    # Check if data files exist
    if not aoi_path.exists():
        logger.error(f"Please copy your AOI shapefile to: {aoi_path}")
        raise FileNotFoundError(f"AOI file not found at: {aoi_path}")
    if not any(dem_dir.glob("*.tif")):
        logger.error(f"Please copy your DEM tiles to: {dem_dir}")
        raise FileNotFoundError(f"No DEM tiles found in: {dem_dir}")
    
    site_id = "EMSR728_AOI04"
    try:
        # Run the pipeline
        outputs = run_pipeline(
            site_id=site_id,
            aoi_path=str(aoi_path),
            dem_tile_folder_path=str(dem_dir),
            create_static_maps=True,
            create_interactive_map=True
        )
        
        # Print output paths
        logger.info("Pipeline completed successfully. Output files:")
        for key, path in outputs.items():
            logger.info(f"{key}: {path}")
        
        # Create additional visualizations
        logger.info("Creating additional visualizations")
        create_visualizations(site_id, aoi_path)
            
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main() 