import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.plot import plotting_extent
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.ticker as mticker
from geemap import cartoee


def plot_raster_map(
    raster_path,
    aoi_path=None,
    cmap='terrain',
    vmin=None,
    vmax=None,
    cmap_orientation='standard',
    colorbar_orientation='vertical',
    colorbar_label=None,
    colorbar_label_fontsize=None,
    colorbar_width=0.05,  # Fraction for vertical or absolute for horizontal
    colorbar_height=0.9,  # Fraction for horizontal or absolute for vertical
    colorbar_tick_fontsize=None,
    aoi_color='#797979',
    aoi_linestyle='--',
    aoi_linewidth=4,
    font_family='Arial',
    font_size=16,
    bold_text=False,
    show_grid=True,
    show_lon_lat=True,
    show_scale_bar=True,
    scale_bar_length=10,
    scale_bar_xy=(0.9, 0.05),
    scale_bar_color='black',
    scale_bar_unit='km',
    bbox_buffer=0.05,
    output_path=None,
    title=None,
    figsize=(12, 12),
    dpi=300
):
    """
    Plot a raster map with optional Area of Interest (AOI) overlay.

    Parameters:
    -----------
    raster_path : str
        Path to the raster file.
    aoi_path : str, optional
        Path to the AOI shapefile.
    cmap : str, optional
        Colormap for the raster. Default is 'terrain'.
    vmin : float, optional
        Minimum value for colormap. If None, will use data minimum.
    vmax : float, optional
        Maximum value for colormap. If None, will use data maximum.
    cmap_orientation : str, optional
        Orientation of colormap ('standard' or 'reversed'). Default is 'standard'.
    colorbar_orientation : str, optional
        Orientation of colorbar ('horizontal', 'vertical', or None). Default is 'vertical'.
        Set to None to hide the colorbar.
    aoi_color : str, optional
        Color for the AOI boundary. Default is '#797979'.
    aoi_linestyle : str, optional
        Line style for the AOI boundary. Default is '--'.
    aoi_linewidth : int, optional
        Line width for the AOI boundary. Default is 4.
    font_family : str, optional
        Font family for all text. Default is 'Arial'.
    font_size : int, optional
        Font size for all text. Default is 16.
    bold_text : bool, optional
        Whether to use bold text. Default is False.
    show_grid : bool, optional
        Whether to show grid lines. Default is True.
    show_lon_lat : bool, optional
        Whether to show longitude and latitude labels. Default is True.
    show_scale_bar : bool, optional
        Whether to show a scale bar. Default is True.
    scale_bar_length : int, optional
        Length of the scale bar in specified units. Default is 10.
    scale_bar_xy : tuple, optional
        Position of the scale bar (x, y) in axes coordinates. Default is (0.9, 0.05).
    scale_bar_color : str, optional
        Color of the scale bar. Default is 'black'.
    scale_bar_unit : str, optional
        Unit for the scale bar. Default is 'km'. #TODO add more scalebar parameters height and font size 
    bbox_buffer : float, optional
        Buffer around the AOI for the map extent. Default is 0.05 degrees.
    output_path : str, optional
        Path to save the output map. If None, map will not be saved.
    title : str, optional
        Title for the map. If None, no title will be displayed.
    figsize : tuple, optional
        Figure size in inches. Default is (12, 12).
    dpi : int, optional
        Resolution for saved figure. Default is 300.

    Returns:
    --------
    fig, ax : matplotlib figure and axis objects
    """

    # Set global font settings
    plt.rcParams['font.family'] = font_family
    weight = 'bold' if bold_text else 'normal'
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=figsize, subplot_kw={'projection': ccrs.PlateCarree()})
    
    # Load raster
    with rasterio.open(raster_path) as src:
        raster_data = src.read(1)
        raster_extent = plotting_extent(src)
        raster_crs = src.crs
        raster_nodata = src.nodata
        
        # Handle no-data values
        if raster_nodata is not None:
            raster_data = np.where(raster_data == raster_nodata, np.nan, raster_data)
    
    # Set default vmin and vmax if not provided
    if vmin is None:
        vmin = np.nanmin(raster_data)
    if vmax is None:
        vmax = np.nanmax(raster_data)

    # Apply colormap orientation
    if cmap_orientation.lower() == 'reversed':
        cmap = plt.get_cmap(cmap).reversed()
    else:
        cmap = plt.get_cmap(cmap)

    # Plot raster
    im = ax.imshow(
        raster_data,
        extent=raster_extent,
        origin='upper',
        cmap=cmap,
        zorder=1,
        vmin=vmin,
        vmax=vmax
    )
    
    # Process AOI if provided
    if aoi_path:
        # Load AOI
        aoi = gpd.read_file(aoi_path)
        if aoi.crs != raster_crs:
            aoi = aoi.to_crs(raster_crs)
        
        # Plot AOI
        aoi.boundary.plot(
            ax=ax,
            color=aoi_color,
            linestyle=aoi_linestyle,
            linewidth=aoi_linewidth,
            zorder=4,
            label='AOI'
        )
        
        # Set map extent based on AOI with buffer
        minx, miny, maxx, maxy = aoi.total_bounds
        ax.set_extent(
            [minx - bbox_buffer, maxx + bbox_buffer, miny - bbox_buffer, maxy + bbox_buffer],
            crs=ccrs.PlateCarree()
        )
    else:
        # If no AOI, use raster extent
        minx, maxx, miny, maxy = raster_extent
        ax.set_extent(
            [minx - bbox_buffer, maxx + bbox_buffer, miny - bbox_buffer, maxy + bbox_buffer],
            crs=ccrs.PlateCarree()
        )

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
            gl.top_labels = True
            gl.right_labels = False
            gl.left_labels = True
            gl.bottom_labels = False
            gl.xlocator = mticker.MaxNLocator(nbins=3)
            gl.ylocator = mticker.MaxNLocator(nbins=3)
            gl.xlabel_style = {'size': font_size, 'weight': weight}
            gl.ylabel_style = {'size': font_size, 'weight': weight}
            gl.xformatter = LONGITUDE_FORMATTER
            gl.yformatter = LATITUDE_FORMATTER
    
    # Remove all spines
    for spine in ax.spines.values():
        spine.set_visible(False)
        
    # Add title if provided
    if title:
        ax.set_title(title, fontsize=font_size, fontweight=weight)
    
    # Add colorbar if requested
    if colorbar_orientation is not None:
        # Set default font sizes if not specified
        if colorbar_tick_fontsize is None:
            colorbar_tick_fontsize = font_size
        if colorbar_label_fontsize is None:
            colorbar_label_fontsize = font_size
            
        # Create colorbar with a simpler, more reliable approach
        if colorbar_orientation == 'vertical':
            # Simple vertical colorbar with custom width
            cbar = fig.colorbar(
                im, 
                ax=ax,
                orientation='vertical',
                pad=0.02,
                fraction=colorbar_width,  # Controls width
                shrink=colorbar_height    # Controls height as fraction of axes height
            )
        else:  # horizontal colorbar
            # Simple horizontal colorbar with custom height
            cbar = fig.colorbar(
                im, 
                ax=ax,
                orientation='horizontal',
                pad=0.02, 
                fraction=colorbar_width,  # Controls height
                shrink=colorbar_height    # Controls width as fraction of axes width
            )
            
        # Style the colorbar
        cbar.ax.tick_params(labelsize=colorbar_tick_fontsize)
        
        # Add colorbar label if provided
        if colorbar_label:
            if colorbar_orientation == 'vertical':
                cbar.ax.set_ylabel(colorbar_label, fontsize=colorbar_label_fontsize, fontweight=weight)
            else:
                cbar.ax.set_xlabel(colorbar_label, fontsize=colorbar_label_fontsize, fontweight=weight)
        
        # Add colorbar label if provided
        if colorbar_label:
            if colorbar_orientation == 'vertical':
                cbar.ax.set_ylabel(colorbar_label, fontsize=colorbar_label_fontsize, fontweight=weight)
            else:
                cbar.ax.set_xlabel(colorbar_label, fontsize=colorbar_label_fontsize, fontweight=weight)

        # Method 2: Use MaxNLocator to specify approximate number of ticks
        from matplotlib.ticker import MaxNLocator
        #cbar.update_ticks()
        cbar.set_ticks(np.linspace(vmin, vmax, 5))

    # Add scale bar if requested
    if show_scale_bar:
        cartoee.add_scale_bar_lite(
            ax, 
            length=scale_bar_length, 
            xy=scale_bar_xy, 
            fontsize=font_size,
            linewidth=8,
            color=scale_bar_color, 
            unit=scale_bar_unit
        )
    
    # Make figure background transparent
    fig.patch.set_alpha(0)
    # Make axes background transparent
    ax.patch.set_alpha(0)

    # Save the figure if output path is provided
    if output_path:
        fig.savefig(output_path, bbox_inches='tight', transparent=True, dpi=dpi)
    
    return fig, ax

