"""Test script for visualizing hydro-topological features."""

import logging
from pathlib import Path
from hydro_topo_features.visualization.static import plot_static_map
from hydro_topo_features.visualization.interactive import plot_interactive_map
from hydro_topo_features import config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Run visualization tests."""
    # Set paths
    site_id = "EMSR728_AOI04"
    site_dir = config.OUTPUT_DIR / site_id
    interim_dir = site_dir / config.INTERIM_DIR
    processed_dir = site_dir / config.PROCESSED_DIR
    aoi_path = Path("example_data/aoi/danube/EMSR728_AOI04_DEL_PRODUCT_areaOfInterestA_v1.shp")
    
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

if __name__ == "__main__":
    main() 