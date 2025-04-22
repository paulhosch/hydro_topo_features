"""Functions for creating static maps of hydro-topological features."""

import os
import logging
from pathlib import Path
from typing import Dict, Optional, Union
import numpy as np
import matplotlib.pyplot as plt
import rasterio
import geopandas as gpd
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.ticker as mticker
from geemap import cartoee
from .. import config

logger = logging.getLogger(__name__)

def plot_static_map(
    site_id: str,
    raster_path: str,
    aoi_path: str = None,
    cmap: str = 'terrain',
    vmin: float = None,
    vmax: float = None,
    Name: str = None,
    Unit: str = None,
    aoi_color: str = None,
    aoi_linestyle: str = None,
    aoi_linewidth: int = None,
    show_grid: bool = None,
    show_lon_lat: bool = None,
    show_scale_bar: bool = None,
    scale_bar_length: int = None,
    scale_bar_color: str = None,
    scale_bar_unit: str = None,
    bbox_buffer: float = None,
    figsize: tuple = (18, 6),
    dpi: int = None,
    output_dirs: Optional[Dict[str, Path]] = None
) -> str:
    """
    Create a static map visualization of a raster dataset.
    
    Args:
        site_id: Unique identifier for the site
        raster_path: Path to the raster file to plot
        aoi_path: Path to the AOI shapefile/geopackage
        cmap: Matplotlib colormap name
        vmin: Minimum value for colormap
        vmax: Maximum value for colormap
        Name: Name of the feature for the title
        Unit: Unit for the colorbar label
        aoi_color: Color for AOI boundary
        aoi_linestyle: Line style for AOI boundary
        aoi_linewidth: Line width for AOI boundary
        show_grid: Whether to show grid lines
        show_lon_lat: Whether to show lon/lat labels
        show_scale_bar: Whether to show scale bar
        scale_bar_length: Length of scale bar
        scale_bar_color: Color of scale bar
        scale_bar_unit: Unit for scale bar
        bbox_buffer: Buffer around data extent
        figsize: Figure size in inches
        dpi: Resolution for saved figure
        output_dirs: Dictionary of output directories
        
    Returns:
        Path to saved figure
    """
    logger.info(f"Creating static map for {Name if Name else 'raster'}")
    
    # Set default output directories if not provided
    if output_dirs is None:
        site_dir = Path(config.DEFAULT_OUTPUT_DIR) / site_id
        figures_dir = site_dir / config.DIRECTORY_STRUCTURE["FIGURES"] / config.DIRECTORY_STRUCTURE["STATIC"]
        os.makedirs(figures_dir, exist_ok=True)
    else:
        figures_dir = output_dirs["static_figures"]
    
    # Output path
    feature_name = Name.lower() if Name else Path(raster_path).stem
    output_path = figures_dir / f"{feature_name}_map.svg"
    
    # Set defaults from config if not provided
    vis_config = config.STATIC_VIS
    aoi_color = aoi_color or vis_config['aoi_color']
    aoi_linestyle = aoi_linestyle or vis_config['aoi_linestyle']
    aoi_linewidth = aoi_linewidth or vis_config['aoi_linewidth']
    show_grid = show_grid if show_grid is not None else vis_config['show_grid']
    show_lon_lat = show_lon_lat if show_lon_lat is not None else vis_config['show_lon_lat']
    show_scale_bar = show_scale_bar if show_scale_bar is not None else vis_config['show_scale_bar']
    scale_bar_length = scale_bar_length or vis_config['scale_bar_length']
    scale_bar_color = scale_bar_color or vis_config['scale_bar_color']
    scale_bar_unit = scale_bar_unit or vis_config['scale_bar_unit']
    bbox_buffer = bbox_buffer or vis_config['bbox_buffer']
    dpi = dpi or vis_config['dpi']
    
    # Set font properties
    plt.rcParams['font.family'] = vis_config['font']
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=figsize, subplot_kw={'projection': ccrs.PlateCarree()})
    
    # Read and plot raster
    with rasterio.open(raster_path) as src:
        data = src.read(1)
        extent = [src.bounds.left, src.bounds.right, src.bounds.bottom, src.bounds.top]
        
        if vmin is None:
            vmin = np.nanmin(data)
        if vmax is None:
            vmax = np.nanmax(data)
        
        im = ax.imshow(
            data,
            extent=extent,
            origin='upper',
            cmap=cmap,
            vmin=vmin,
            vmax=vmax
        )
    
    # Add AOI if provided
    if aoi_path:
        aoi = gpd.read_file(aoi_path)
        if aoi.crs != 'EPSG:4326':
            aoi = aoi.to_crs('EPSG:4326')
        aoi.boundary.plot(
            ax=ax,
            color=aoi_color,
            linestyle=aoi_linestyle,
            linewidth=aoi_linewidth,
            label='AOI'
        )
        
        # Set extent from AOI
        bounds = aoi.total_bounds
        ax.set_extent([
            bounds[0] - bbox_buffer,
            bounds[2] + bbox_buffer,
            bounds[1] - bbox_buffer,
            bounds[3] + bbox_buffer
        ])
    
    # Add gridlines if requested
    if show_grid:
        gl = ax.gridlines(
            draw_labels=show_lon_lat,
            linewidth=0.5,
            color='gray',
            alpha=0.5,
            linestyle='--'
        )
        
        if show_lon_lat:
            gl.top_labels = False
            gl.right_labels = False
            gl.xformatter = LONGITUDE_FORMATTER
            gl.yformatter = LATITUDE_FORMATTER
            gl.xlabel_style = {'size': vis_config['fontsize_axes']}
            gl.ylabel_style = {'size': vis_config['fontsize_axes']}
            gl.xlocator = mticker.MaxNLocator(nbins=3)
            gl.ylocator = mticker.MaxNLocator(nbins=3)
    
    # Add colorbar
    cbar = fig.colorbar(
        im,
        ax=ax,
        orientation='vertical',
        pad=0.02,
        fraction=vis_config['colorbar_width'],
        shrink=vis_config['colorbar_height']    )
    # Ensure a tick at the max value
    if vmin is not None and vmax is not None:
        # Create tick locations with first tick at vmin and last tick at vmax
        tick_count = 5  
        ticks = np.linspace(vmin, vmax, tick_count)
        cbar.set_ticks(ticks)
        
        # Optional: Format tick labels if needed
        # cbar.set_ticklabels([f"{t:.2f}" for t in ticks])
    
    if Unit:
        cbar.set_label(
            f"{Name} ({Unit})" if Name else Unit,
            size=vis_config['fontsize_colorbar']
        )
    
    cbar.ax.tick_params(labelsize=vis_config['fontsize_colorbar'])
    
    # Add scale bar if requested
    if show_scale_bar:
        cartoee.add_scale_bar_lite(
            ax,
            length=scale_bar_length,
            xy=(0.8, 0.05),
            linewidth=2,
            fontsize=vis_config['fontsize_axes'],
            color=scale_bar_color,
            unit=scale_bar_unit
        )
    
    # Add title if provided
    if Name:
        ax.set_title(Name, fontsize=vis_config['fontsize_title'])
    
    # Remove spines
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    # Save figure
    fig.savefig(output_path, bbox_inches='tight', dpi=dpi, transparent=True)
    plt.close()
    
    logger.info(f"Static map saved to: {output_path}")
    return str(output_path) 