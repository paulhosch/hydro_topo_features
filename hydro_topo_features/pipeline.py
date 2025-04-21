"""Main pipeline for computing and visualizing hydro-topological features."""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

from .processing import prepare_data, condition_dem, derive_products
from .visualization import plot_static_map, plot_interactive_map
from . import config

logger = logging.getLogger(__name__)

def run_pipeline(
    site_id: str,
    aoi_path: str,
    dem_tile_folder_path: str,
    create_static_maps: bool = True,
    create_interactive_map: bool = True,
    feature_configs: Optional[Dict] = None
) -> Dict[str, str]:
    """
    Run the complete hydro-topological feature computation pipeline.
    
    Args:
        site_id (str): Unique identifier for the site
        aoi_path (str): Path to AOI shapefile/geopackage
        dem_tile_folder_path (str): Path to folder containing DEM tiles
        create_static_maps (bool): Whether to create static maps
        create_interactive_map (bool): Whether to create interactive map
        feature_configs (dict, optional): Configuration overrides for features
            Example:
            {
                'raw_dem': {'vmin': 0, 'vmax': 1000},
                'osm_water': {'cmap': 'Blues'},
                'hand': {'vmin': 0, 'vmax': 100},
                'slope': {'vmin': 0, 'vmax': 45},
                'edtw': {'vmin': 0, 'vmax': 1000}
            }
    
    Returns:
        dict: Dictionary containing paths to all outputs
    """
    logger.info(f"Starting pipeline for site: {site_id}")
    outputs = {}
    
    # 1. Prepare input data
    logger.info("Step 1: Preparing input data")
    data_paths = prepare_data(
        site_id=site_id,
        aoi_path=aoi_path,
        dem_tile_folder_path=dem_tile_folder_path
    )
    outputs.update(data_paths)
    
    # 2. Condition DEM
    logger.info("Step 2: Conditioning DEM")
    conditioned_dem_path = condition_dem(
        site_id=site_id,
        raw_dem=data_paths['raw_dem'],
        osm_water_raster=data_paths['osm_water_raster']
    )
    outputs['conditioned_dem'] = conditioned_dem_path
    
    # 3. Compute features
    logger.info("Step 3: Computing features")
    
    # HAND
    hand_path = derive_products.get_osm_hand(
        site_id=site_id,
        raw_dem=data_paths['raw_dem'],
        osm_water_raster=data_paths['osm_water_raster'],
        conditioned_dem=conditioned_dem_path
    )
    outputs['hand'] = hand_path
    
    # Slope
    slope_path = derive_products.get_slope(
        site_id=site_id,
        raw_dem=data_paths['raw_dem']
    )
    outputs['slope'] = slope_path
    
    # EDTW
    edtw_path = derive_products.get_edtw(
        site_id=site_id,
        osm_water_raster=data_paths['osm_water_raster']
    )
    outputs['edtw'] = edtw_path
    
    # 4. Create visualizations
    if create_static_maps:
        logger.info("Step 4a: Creating static maps")
        
        # Default configurations for each feature
        default_configs = {
            'raw_dem': {
                'Name': 'Digital Elevation Model',
                'Unit': 'meters',
                'cmap': 'terrain'
            },
            'osm_water': {
                'Name': 'OSM Water Features',
                'Unit': None,
                'cmap': 'Blues'
            },
            'hand': {
                'Name': 'Height Above Nearest Drainage',
                'Unit': 'meters',
                'cmap': 'terrain'
            },
            'slope': {
                'Name': 'Slope',
                'Unit': config.SLOPE_PARAMS['units'],
                'cmap': 'YlOrRd'
            },
            'edtw': {
                'Name': 'Euclidean Distance to Water',
                'Unit': config.EDTW_PARAMS['units'],
                'cmap': 'YlGnBu'
            }
        }
        
        # Update with user configurations
        if feature_configs:
            for feature, cfg in feature_configs.items():
                if feature in default_configs:
                    default_configs[feature].update(cfg)
        
        # Create static maps
        static_maps = {}
        for feature, cfg in default_configs.items():
            if feature in outputs:
                map_path = plot_static_map(
                    site_id=site_id,
                    raster_path=outputs[feature],
                    aoi_path=aoi_path,
                    **cfg
                )
                static_maps[f"{feature}_static_map"] = map_path
        outputs.update(static_maps)
    
    if create_interactive_map:
        logger.info("Step 4b: Creating interactive map")
        
        # Prepare feature configurations for interactive map
        raster_paths = [outputs[f] for f in ['raw_dem', 'osm_water_raster', 'hand', 'slope', 'edtw']]
        names = ['Digital Elevation Model', 'OSM Water Features', 'Height Above Nearest Drainage', 'Slope', 'Euclidean Distance to Water']
        units = ['meters', None, 'meters', config.SLOPE_PARAMS['units'], config.EDTW_PARAMS['units']]
        cmaps = ['terrain', 'Blues', 'terrain', 'YlOrRd', 'YlGnBu']
        
        # Get value ranges from feature configs if provided
        vmin = []
        vmax = []
        if feature_configs:
            for feature in ['raw_dem', 'osm_water', 'hand', 'slope', 'edtw']:
                if feature in feature_configs and 'vmin' in feature_configs[feature]:
                    vmin.append(feature_configs[feature]['vmin'])
                    vmax.append(feature_configs[feature]['vmax'])
                else:
                    vmin.append(None)
                    vmax.append(None)
        
        interactive_map = plot_interactive_map(
            site_id=site_id,
            raster_paths=raster_paths,
            aoi_path=aoi_path,
            Name=names,
            Unit=units,
            cmap=cmaps,
            vmin=vmin if vmin else None,
            vmax=vmax if vmax else None
        )
        outputs['interactive_map'] = interactive_map
    
    logger.info("Pipeline completed successfully")
    return outputs 