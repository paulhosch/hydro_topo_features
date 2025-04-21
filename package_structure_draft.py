# Directory: hydro_topo_features
# Pipeline to compute the hydro-topological features (hand, slope, edtw) from FathomDEM and OSM water

# ------------------
# File: config.py
# ------------------
BURN_DEPTH = 20  # meters
OUTPUT_DIR = "outputs"  # base directory for saving outputs
INTERIM_DIR = "interim"   # directory for intermediate results
PROCESSED_DIR = "processed"  # directory for final products
FIGURES_DIR = "figures"  # directory for visualizations

# Static plot defaults
PLOT_CONFIG = {
    "font": "Arial",
    "fontsize_title": 14,
    "fontsize_axes": 12,
    "fontsize_legend": 10,
    ...
}
#TODO: similar config for interactive plot

#TODO: very important there is a version conflict between pyhseds and numpy ensure numpy 1.26 is installed and in the requirements.txt

# ------------------
# File: logger.py
# ------------------
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("pipeline.log")
    ]
)

logger = logging.getLogger("hydrotools")

# ------------------
# File: processing/prepare_data.py
# ------------------
from logger import logger
from pathlib import Path

def prepare_data(site_id, aoi_path, dem_tile_folder_path):
    """
    - Merge DEM tiles into one raster if needed
    - Convert DEM from cm to meters
    - Get OSM water features using osmnx with tags:
        * natural=water
        * waterway=*
        * landuse=reservoir
    - Rasterize water features at 30m resolution
    - Save outputs to:
        * outputs/{site_id}/interim/raw_dem.tif
        * outputs/{site_id}/interim/osm_water_vector.gpkg
        * outputs/{site_id}/interim/osm_water_raster.tif
    - Log all steps and paths
    """
    logger.info(f"Preparing data for site: {site_id}")
    pass

# ------------------
# File: processing/condition_dem.py
# ------------------
from logger import logger

def condition_dem(site_id, raw_dem, osm_water_raster):
    """
    - Accept either in-memory objects or file paths for raw_dem and osm_water_raster
    - Stream burn the DEM by -20m where osm_water_raster is 1
    - Apply pit filling, depression filling, and flat resolving using pysheds
    - Save to: outputs/{site_id}/processed/conditioned_dem.tif
    - Log steps and file path
    """
    logger.info(f"Conditioning DEM for: {site_id}")
    pass

# ------------------
# File: processing/derive_products.py
# ------------------
from logger import logger

def get_osm_hand(site_id, raw_dem, osm_water_raster, conditioned_dem):
    """
    - Accepts either file paths or in-memory rasters
    - Compute flow direction on conditioned_dem
    - Compute HAND using raw_dem and osm_water_raster
    - Save to: outputs/{site_id}/processed/osm_hand.tif
    - Log steps and outputs
    """
    logger.info(f"Computing HAND for site: {site_id}")
    pass

def get_slope(site_id, raw_dem):
    """
    - Compute slope from DEM
    # Initialize the grid object with the DEM file path as a string
grid = Grid.from_raster(str(dem_path))
dem = grid.read_raster(dem_path)

# Compute the slope using gradient
dy, dx = np.gradient(dem)
slope = np.arctan(np.sqrt(dy**2 + dx**2)) * (180 / np.pi)  # Convert to degrees
    - Save to: outputs/{site_id}/processed/slope.tif
    - Log progress
    """
    logger.info(f"Computing slope for site: {site_id}")
    pass

def get_edtw(site_id, osm_water_raster):
    """
    - Compute Euclidean Distance to Water (EDTW)
    - Save to: outputs/{site_id}/processed/edtw.tif
    - Log progress
    """
    logger.info(f"Computing EDTW for site: {site_id}")
    pass

# ------------------
# File: visualization/interactive.py
# ------------------
from logger import logger

def plot_interactive_map(site_id, aoi_path, aoi_color,
                          raster_paths, vmin, vmax, cbar, zorder, Name, Unit,
                          vector_paths, polygon_color, line_color,
                          polygon_legend_name, line_legend_name):
    """
    - Plot interactive map using folium
    - Save to: outputs/{site_id}/figures/interactive_map.html
    - Log included layers and save confirmation
    """
    logger.info(f"Creating interactive map for site: {site_id}")
    pass

# ------------------
# File: visualization/static.py
# ------------------
from logger import logger
from config import PLOT_CONFIG

def plot_static_map(site_id, aoi_path, aoi_color,
                    raster_path, vmin, vmax, cbar,
                    Name, Unit,
                    vector_path, polygon_color, line_color,
                    polygon_legend_name, line_legend_name,
                    lon_lat_labels=True, colorbar=True, legend=True):
    """
    - Plot static map using matplotlib
    - Uses default configurations from config.py if not specified
    - Save to: outputs/{site_id}/figures/static_map.svg
    - Log parameters and save result
    """
    logger.info(f"Creating static map for site: {site_id}")
    pass
