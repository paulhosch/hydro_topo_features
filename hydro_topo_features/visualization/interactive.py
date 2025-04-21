"""Functions for creating interactive maps of hydro-topological features."""

import os
import logging
from pathlib import Path
from io import BytesIO
import base64
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import rasterio
import geopandas as gpd
import folium
from folium import plugins
from .. import config

logger = logging.getLogger(__name__)

def plot_interactive_map(
    site_id: str,
    raster_paths: list,
    aoi_path: str = None,
    Name: list = None,
    Unit: list = None,
    vmin: list = None,
    vmax: list = None,
    cmap: list = None,
    opacity: float = None,
    zoom_start: int = None
) -> str:
    """
    Create an interactive map with multiple raster layers.
    
    Args:
        site_id (str): Unique identifier for the site
        raster_paths (list): List of paths to raster files
        aoi_path (str, optional): Path to AOI shapefile/geopackage
        Name (list, optional): List of names for each raster layer
        Unit (list, optional): List of units for each raster layer
        vmin (list, optional): List of minimum values for each raster
        vmax (list, optional): List of maximum values for each raster
        cmap (list, optional): List of colormaps for each raster
        opacity (float, optional): Opacity for raster layers
        zoom_start (int, optional): Initial zoom level
        
    Returns:
        str: Path to saved HTML map
    """
    logger.info(f"Creating interactive map for site: {site_id}")
    
    # Create output directory
    site_dir = config.OUTPUT_DIR / site_id
    figures_dir = site_dir / config.FIGURES_DIR / "interactive"
    os.makedirs(figures_dir, exist_ok=True)
    
    # Output path
    output_path = figures_dir / "interactive_map.html"
    
    # Set defaults
    opacity = opacity or config.INTERACTIVE_CONFIG['opacity']
    zoom_start = zoom_start or config.INTERACTIVE_CONFIG['zoom_start']
    
    # Get layer names from file paths
    layer_names = [Path(p).stem for p in raster_paths]
    
    # Initialize visualization parameters from config
    if Name is None:
        Name = []
        for layer in layer_names:
            for key, cfg in config.RASTER_VIS_CONFIG.items():
                if key in layer.lower():
                    Name.append(cfg['name'])
                    break
            else:
                Name.append(layer)
    
    if Unit is None:
        Unit = []
        for layer in layer_names:
            for key, cfg in config.RASTER_VIS_CONFIG.items():
                if key in layer.lower():
                    Unit.append(cfg['unit'])
                    break
            else:
                Unit.append('')
    
    if vmin is None:
        vmin = []
        for layer in layer_names:
            for key, cfg in config.RASTER_VIS_CONFIG.items():
                if key in layer.lower():
                    vmin.append(cfg['vmin'])
                    break
            else:
                vmin.append(None)
    
    if vmax is None:
        vmax = []
        for layer in layer_names:
            for key, cfg in config.RASTER_VIS_CONFIG.items():
                if key in layer.lower():
                    vmax.append(cfg['vmax'])
                    break
            else:
                vmax.append(None)
    
    if cmap is None:
        cmap = []
        for layer in layer_names:
            for key, cfg in config.RASTER_VIS_CONFIG.items():
                if key in layer.lower():
                    cmap.append(cfg['cmap'])
                    break
            else:
                cmap.append('terrain')
    
    # Get center coordinates from first raster
    with rasterio.open(raster_paths[0]) as src:
        bounds = src.bounds
        center_lat = (bounds.bottom + bounds.top) / 2
        center_lon = (bounds.left + bounds.right) / 2
    
    # Create base map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom_start,
        control_scale=True,
        crs='EPSG:4326'  # Use WGS84 for web mapping
    )
    
    # Add each raster layer
    for i, raster_path in enumerate(raster_paths):
        with rasterio.open(raster_path) as src:
            data = src.read(1)
            bounds = src.bounds
            
            # Handle nodata values
            data = np.ma.masked_equal(data, src.nodata if src.nodata is not None else config.NODATA_VALUE)
            
            # Get value range
            v_min = vmin[i] if vmin[i] is not None else float(np.nanmin(data))
            v_max = vmax[i] if vmax[i] is not None else float(np.nanmax(data))
            
            # Normalize data
            norm_data = np.clip((data - v_min) / (v_max - v_min), 0, 1)
            norm_data = np.ma.masked_invalid(norm_data)
            
            # Apply colormap
            colormap = plt.get_cmap(cmap[i])
            colored_data = colormap(norm_data, alpha=opacity)
            colored_data = (colored_data * 255).astype(np.uint8)
            
            # Add layer to map
            img = folium.raster_layers.ImageOverlay(
                colored_data,
                bounds=[[bounds.bottom, bounds.left], [bounds.top, bounds.right]],
                name=f"{Name[i]}",
                opacity=opacity,
                show=True if i == 0 else False  # Only show first layer by default
            )
            img.add_to(m)
            
            # Create colorbar
            fig, ax = plt.subplots(figsize=(1.5, 4))
            norm = mpl.colors.Normalize(vmin=v_min, vmax=v_max)
            cbar = fig.colorbar(
                plt.cm.ScalarMappable(norm=norm, cmap=cmap[i]),
                cax=ax
            )
            cbar.set_label(f"{Name[i]} ({Unit[i]})" if Unit[i] else Name[i])
            plt.tight_layout()
            
            # Save colorbar to BytesIO
            buf = BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
            plt.close()
            buf.seek(0)
            img_str = base64.b64encode(buf.read()).decode('utf-8')
            
            # Add colorbar to map
            colorbar_html = f'''
                <div style="
                    position: fixed; 
                    bottom: 50px; 
                    right: {50 + i*100}px; 
                    z-index: 9999; 
                    background-color: white;
                    padding: 10px;
                    border-radius: 5px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.5);">
                    <img src="data:image/png;base64,{img_str}" style="height:200px;">
                </div>
            '''
            m.get_root().html.add_child(folium.Element(colorbar_html))
    
    # Add AOI if provided
    if aoi_path:
        aoi = gpd.read_file(aoi_path)
        if aoi.crs != 'EPSG:4326':
            aoi = aoi.to_crs('EPSG:4326')
        
        folium.GeoJson(
            aoi,
            name='Area of Interest',
            style_function=lambda x: {
                'color': config.INTERACTIVE_CONFIG['aoi_color'],
                'weight': config.INTERACTIVE_CONFIG['aoi_weight'],
                'dashArray': config.INTERACTIVE_CONFIG['aoi_dash_array'],
                'fillOpacity': config.INTERACTIVE_CONFIG['aoi_fill_opacity']
            }
        ).add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Save map
    m.save(output_path)
    logger.info(f"Interactive map saved to: {output_path}")
    return str(output_path) 