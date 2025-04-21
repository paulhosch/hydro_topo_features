"""Functions for creating static maps of hydro-topological features."""

import os
import logging
from pathlib import Path
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
    figsize: tuple = (12, 12),
    dpi: int = None
) -> str:
    """
    Create a static map visualization of a raster dataset.
    
    Args:
        site_id (str): Unique identifier for the site
        raster_path (str): Path to the raster file to plot
        aoi_path (str, optional): Path to the AOI shapefile/geopackage
        cmap (str, optional): Matplotlib colormap name
        vmin (float, optional): Minimum value for colormap
        vmax (float, optional): Maximum value for colormap
        Name (str, optional): Name of the feature for the title
        Unit (str, optional): Unit for the colorbar label
        aoi_color (str, optional): Color for AOI boundary
        aoi_linestyle (str, optional): Line style for AOI boundary
        aoi_linewidth (int, optional): Line width for AOI boundary
        show_grid (bool, optional): Whether to show grid lines
        show_lon_lat (bool, optional): Whether to show lon/lat labels
        show_scale_bar (bool, optional): Whether to show scale bar
        scale_bar_length (int, optional): Length of scale bar
        scale_bar_color (str, optional): Color of scale bar
        scale_bar_unit (str, optional): Unit for scale bar
        bbox_buffer (float, optional): Buffer around data extent
        figsize (tuple, optional): Figure size in inches
        dpi (int, optional): Resolution for saved figure
        
    Returns:
        str: Path to saved figure
    """
    logger.info(f"Creating static map for {Name if Name else 'raster'}")
    
    # Create output directory
    site_dir = config.OUTPUT_DIR / site_id
    figures_dir = site_dir / config.FIGURES_DIR / "static"
    os.makedirs(figures_dir, exist_ok=True)
    
    # Output path
    feature_name = Name.lower() if Name else Path(raster_path).stem
    output_path = figures_dir / f"{feature_name}_map.svg"
    
    # Set defaults from config if not provided
    aoi_color = aoi_color or config.PLOT_CONFIG['aoi_color']
    aoi_linestyle = aoi_linestyle or config.PLOT_CONFIG['aoi_linestyle']
    aoi_linewidth = aoi_linewidth or config.PLOT_CONFIG['aoi_linewidth']
    show_grid = show_grid if show_grid is not None else config.PLOT_CONFIG['show_grid']
    show_lon_lat = show_lon_lat if show_lon_lat is not None else config.PLOT_CONFIG['show_lon_lat']
    show_scale_bar = show_scale_bar if show_scale_bar is not None else config.PLOT_CONFIG['show_scale_bar']
    scale_bar_length = scale_bar_length or config.PLOT_CONFIG['scale_bar_length']
    scale_bar_color = scale_bar_color or config.PLOT_CONFIG['scale_bar_color']
    scale_bar_unit = scale_bar_unit or config.PLOT_CONFIG['scale_bar_unit']
    bbox_buffer = bbox_buffer or config.PLOT_CONFIG['bbox_buffer']
    dpi = dpi or config.PLOT_CONFIG['dpi']
    
    # Set font properties
    plt.rcParams['font.family'] = config.PLOT_CONFIG['font']
    
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
            gl.xlabel_style = {'size': config.PLOT_CONFIG['fontsize_axes']}
            gl.ylabel_style = {'size': config.PLOT_CONFIG['fontsize_axes']}
    
    # Add colorbar
    cbar = fig.colorbar(
        im,
        ax=ax,
        orientation='vertical',
        pad=0.02,
        fraction=config.PLOT_CONFIG['colorbar_width'],
        shrink=config.PLOT_CONFIG['colorbar_height']
    )
    
    if Unit:
        cbar.set_label(
            f"{Name} ({Unit})" if Name else Unit,
            size=config.PLOT_CONFIG['fontsize_colorbar']
        )
    
    cbar.ax.tick_params(labelsize=config.PLOT_CONFIG['fontsize_colorbar'])
    
    # Add scale bar if requested
    if show_scale_bar:
        cartoee.add_scale_bar_lite(
            ax,
            length=scale_bar_length,
            xy=(0.8, 0.05),
            fontsize=config.PLOT_CONFIG['fontsize_axes'],
            color=scale_bar_color,
            unit=scale_bar_unit
        )
    
    # Add title if provided
    if Name:
        ax.set_title(Name, fontsize=config.PLOT_CONFIG['fontsize_title'])
    
    # Remove spines
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    # Save figure
    fig.savefig(output_path, bbox_inches='tight', dpi=dpi, transparent=True)
    plt.close()
    
    logger.info(f"Static map saved to: {output_path}")
    return str(output_path) 