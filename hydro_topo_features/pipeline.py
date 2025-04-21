"""Main pipeline for processing hydro-topological features."""

import os
import logging
from pathlib import Path
from typing import Dict, Optional, Union, List

from . import config
from .processing import prepare_data, burn_dem, derive_products
from .visualization import static, interactive

logger = logging.getLogger(__name__)

def setup_directory_structure(output_path: Union[str, Path], site_id: str) -> Dict[str, Path]:
    """
    Set up the directory structure for outputs.
    
    Args:
        output_path: Base path for all outputs
        site_id: Unique identifier for the site
        
    Returns:
        Dictionary of paths for different output types
    """
    # Convert to Path object if string
    output_base = Path(output_path)
    
    # Create site directory
    site_dir = output_base / site_id
    
    # Create dictionary of directories
    dirs = {
        "root": site_dir,
        "raw": site_dir / config.DIRECTORY_STRUCTURE["RAW"],
        "interim": site_dir / config.DIRECTORY_STRUCTURE["INTERIM"],
        "processed": site_dir / config.DIRECTORY_STRUCTURE["PROCESSED"],
        "figures": site_dir / config.DIRECTORY_STRUCTURE["FIGURES"],
        "static_figures": site_dir / config.DIRECTORY_STRUCTURE["FIGURES"] / config.DIRECTORY_STRUCTURE["STATIC"],
        "interactive_figures": site_dir / config.DIRECTORY_STRUCTURE["FIGURES"] / config.DIRECTORY_STRUCTURE["INTERACTIVE"]
    }
    
    # Create all directories
    for dir_path in dirs.values():
        os.makedirs(dir_path, exist_ok=True)
        
    return dirs

def run_pipeline(
    site_id: str,
    aoi_path: str,
    dem_tile_folder_path: str,
    output_path: Optional[Union[str, Path]] = None,
    create_static_maps: bool = True,
    create_interactive_map: bool = True
) -> Dict[str, str]:
    """
    Run the complete pipeline for processing hydro-topological features.
    
    Args:
        site_id: Unique identifier for the site
        aoi_path: Path to AOI shapefile/geopackage
        dem_tile_folder_path: Path to folder containing DEM tiles
        output_path: Base path for all outputs (default: config.DEFAULT_OUTPUT_DIR)
        create_static_maps: Whether to create static maps of the features
        create_interactive_map: Whether to create an interactive map of all features
        
    Returns:
        Dictionary of output file paths
    """
    # Set up output path
    output_base = Path(output_path) if output_path else Path(config.DEFAULT_OUTPUT_DIR)
    
    # Setup directory structure
    dirs = setup_directory_structure(output_base, site_id)
    
    logger.info(f"Running pipeline for site: {site_id}")
    logger.info(f"Output directory: {dirs['root']}")
    
    # Dictionary to store output paths
    outputs = {}
    
    # Step 1: Prepare data (merge DEM tiles, extract OSM water)
    logger.info("Step 1: Preparing input data")
    prepare_outputs = prepare_data.prepare_input_data(
        site_id=site_id,
        aoi_path=aoi_path,
        dem_tile_folder_path=dem_tile_folder_path,
        output_dirs=dirs
    )
    outputs.update(prepare_outputs)
    
    # Step 2: Burn streams into DEM
    logger.info("Step 2: Burning streams into DEM")
    burned_dem_path = burn_dem.burn_streams(
        site_id=site_id,
        raw_dem=outputs["raw_dem"],
        osm_water_raster=outputs["osm_water_raster"],
        output_dirs=dirs
    )
    outputs["burned_dem"] = burned_dem_path
    
    # Step 3: Compute HAND
    logger.info("Step 3: Computing HAND")
    hand_path = derive_products.get_osm_hand(
        site_id=site_id,
        raw_dem=outputs["raw_dem"],
        osm_water_raster=outputs["osm_water_raster"],
        burned_dem=outputs["burned_dem"],
        output_dirs=dirs
    )
    outputs["hand"] = hand_path
    
    # Step 4: Compute slope
    logger.info("Step 4: Computing slope")
    slope_path = derive_products.get_slope(
        site_id=site_id,
        raw_dem=outputs["raw_dem"],
        output_dirs=dirs
    )
    outputs["slope"] = slope_path
    
    # Step 5: Compute EDTW
    logger.info("Step 5: Computing EDTW")
    edtw_path = derive_products.get_edtw(
        site_id=site_id,
        osm_water_raster=outputs["osm_water_raster"],
        output_dirs=dirs
    )
    outputs["edtw"] = edtw_path
    
    # Step 6: Create visualizations
    if create_static_maps:
        logger.info("Step 6a: Creating static maps")
        static_maps = create_static_visualizations(
            site_id=site_id,
            aoi_path=aoi_path,
            raster_outputs=outputs,
            output_dirs=dirs
        )
        outputs.update(static_maps)
    
    if create_interactive_map:
        logger.info("Step 6b: Creating interactive map")
        interactive_map = create_interactive_visualization(
            site_id=site_id,
            aoi_path=aoi_path,
            raster_outputs=outputs,
            output_dirs=dirs
        )
        outputs["interactive_map"] = interactive_map
    
    logger.info(f"Pipeline completed for site: {site_id}")
    return outputs

def create_static_visualizations(
    site_id: str,
    aoi_path: str,
    raster_outputs: Dict[str, str],
    output_dirs: Dict[str, Path]
) -> Dict[str, str]:
    """
    Create static visualizations for all raster outputs.
    
    Args:
        site_id: Unique identifier for the site
        aoi_path: Path to AOI shapefile/geopackage
        raster_outputs: Dictionary of raster output paths
        output_dirs: Dictionary of output directories
        
    Returns:
        Dictionary of static map paths
    """
    static_maps = {}
    
    # List of features to visualize
    features = ["raw_dem", "burned_dem", "osm_water_raster", "hand", "slope", "edtw"]
    
    for feature in features:
        if feature in raster_outputs:
            # Get visualization config for this feature
            feature_key = feature.replace("_raster", "")
            vis_config = config.RASTER_VIS.get(feature_key, {})
            
            # Create static map
            static_map_path = static.plot_static_map(
                site_id=site_id,
                raster_path=raster_outputs[feature],
                aoi_path=aoi_path,
                Name=vis_config.get("name", feature),
                Unit=vis_config.get("unit", ""),
                vmin=vis_config.get("vmin", None),
                vmax=vis_config.get("vmax", None),
                cmap=vis_config.get("cmap", "terrain"),
                output_dirs=output_dirs
            )
            
            static_maps[f"{feature}_static_map"] = static_map_path
    
    return static_maps

def create_interactive_visualization(
    site_id: str,
    aoi_path: str,
    raster_outputs: Dict[str, str],
    output_dirs: Dict[str, Path]
) -> str:
    """
    Create an interactive visualization with all raster outputs.
    
    Args:
        site_id: Unique identifier for the site
        aoi_path: Path to AOI shapefile/geopackage
        raster_outputs: Dictionary of raster output paths
        output_dirs: Dictionary of output directories
        
    Returns:
        Path to interactive map
    """
    # List of features to include in interactive map
    features = ["raw_dem", "osm_water_raster", "hand", "slope", "edtw"]
    
    # Collect paths, names, units, limits, and cmaps
    raster_paths = []
    names = []
    units = []
    vmins = []
    vmaxs = []
    cmaps = []
    
    for feature in features:
        if feature in raster_outputs:
            # Get visualization config for this feature
            feature_key = feature.replace("_raster", "")
            vis_config = config.RASTER_VIS.get(feature_key, {})
            
            raster_paths.append(raster_outputs[feature])
            names.append(vis_config.get("name", feature))
            units.append(vis_config.get("unit", ""))
            vmins.append(vis_config.get("vmin", None))
            vmaxs.append(vis_config.get("vmax", None))
            cmaps.append(vis_config.get("cmap", "terrain"))
    
    # Create interactive map
    interactive_map_path = interactive.plot_interactive_map(
        site_id=site_id,
        raster_paths=raster_paths,
        aoi_path=aoi_path,
        Name=names,
        Unit=units,
        vmin=vmins,
        vmax=vmaxs,
        cmap=cmaps,
        output_dirs=output_dirs
    )
    
    return interactive_map_path 