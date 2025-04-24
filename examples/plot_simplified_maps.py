#!/usr/bin/env python
"""
Script for creating simplified maps of all raster files.

This script automatically detects all raster files in the data directories
and creates simplified maps without titles, longitude/latitude labels, or scale bars.
"""

import os
import glob
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.colors as mcolors
import cartopy.crs as ccrs
import rasterio
import geopandas as gpd
from hydro_topo_features.visualization.static import plot_static_map

def plot_custom_map(
    site_id,
    raster_path,
    aoi_path,
    cmap='viridis',
    vmin=0,
    vmax=None,
    output_dirs=None,
    figsize=(18, 6),
    bbox_buffer=0.05
):
    """Create a custom map with white colorbar text and AOI."""
    # Output directory setup
    if output_dirs is None:
        base_dir = Path("data/output") / site_id
        output_dirs = {
            "root": base_dir,
            "figures": base_dir / "figures",
            "static_figures": base_dir / "figures" / "simplified_maps"
        }
    
    # Create output directories
    for dir_path in output_dirs.values():
        os.makedirs(dir_path, exist_ok=True)
    
    # Create output path
    feature_name = Path(raster_path).stem
    output_path = output_dirs["static_figures"] / f"{feature_name}_map.svg"
    
    # Set font to Palatino
    plt.rcParams['font.family'] = 'Arial'
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=figsize, subplot_kw={'projection': ccrs.PlateCarree()})
    
    # Read AOI
    aoi = gpd.read_file(aoi_path)
    if aoi.crs != 'EPSG:4326':
        aoi = aoi.to_crs('EPSG:4326')
    
    # Set extent from AOI
    bounds = aoi.total_bounds
    ax.set_extent([
        bounds[0] - bbox_buffer,
        bounds[2] + bbox_buffer,
        bounds[1] - bbox_buffer,
        bounds[3] + bbox_buffer
    ])
    
    # Read and plot raster
    with rasterio.open(raster_path) as src:
        data = src.read(1)
        extent = [src.bounds.left, src.bounds.right, src.bounds.bottom, src.bounds.top]
        
        if vmin is None:
            vmin = np.nanmin(data)
        if vmax is None:
            vmax = np.nanmax(data)
        
        # Special handling for binary water rasters
        is_binary_water = "water" in Path(raster_path).stem.lower() or "osm" in Path(raster_path).stem.lower()
        
        if is_binary_water:
            # Create a masked array where zeros are masked out
            masked_data = np.ma.masked_where(data == 0, data)
            
            # Create custom colormap with specified color for value 1
            water_cmap = mcolors.ListedColormap(['#4878d0'])
            
            # Plot only the pixels with value 1
            im = ax.imshow(
                masked_data,
                extent=extent,
                origin='upper',
                cmap=water_cmap,
                vmin=1,
                vmax=1
            )
        else:
            # For other rasters, plot normally
            im = ax.imshow(
                data,
                extent=extent,
                origin='upper',
                cmap=cmap,
                vmin=vmin,
                vmax=vmax
            )
    
    # Add AOI boundary
    aoi.boundary.plot(
        ax=ax,
        color='#d45e00',
        linestyle='--',
        linewidth=3,
        label='AOI'
    )
    
    # Remove spines
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    # Add colorbar with WHITE text (except for binary water maps)
    if not is_binary_water:
        cbar = fig.colorbar(
            im,
            ax=ax,
            orientation='vertical',
            pad=0.02,
            fraction=0.1,  # Width of colorbar
            shrink=1.0     # Height of colorbar
        )
        
        # Add ticks at regular intervals
        if vmin is not None and vmax is not None:
            tick_count = 5
            ticks = np.linspace(vmin, vmax, tick_count)
            cbar.set_ticks(ticks)
        
        # Set colorbar text to white and increase font size
        cbar.ax.yaxis.label.set_color('black')
        cbar.ax.yaxis.label.set_fontsize(20)  # Set label font size to 20
        cbar.ax.yaxis.label.set_fontweight('bold')  # Make label bold
        cbar.ax.tick_params(colors='black', labelsize=20)  # Set tick font size to 20
        for t in cbar.ax.get_yticklabels():
            t.set_color('black')
            t.set_fontsize(20)  # Ensure tick labels are size 20
            t.set_fontweight('bold')  # Make tick labels bold
    
    # Save figure
    fig.savefig(output_path, bbox_inches='tight', dpi=300, transparent=True)
    plt.close()
    
    return str(output_path)

def main():
    """Create simplified maps for all raster files."""
    # Set site ID
    site_id = "danube"
    
    # Path to AOI shapefile
    aoi_path = "data/example/aoi/EMSR728_AOI04_DEL_PRODUCT_areaOfInterestA_v1.shp"
    
    # Define paths
    base_dir = Path("data/output") / site_id
    interim_dir = base_dir / "interim"
    processed_dir = base_dir / "processed"
    
    # Define output directories
    output_dirs = {
        "root": base_dir,
        "figures": base_dir / "figures",
        "static_figures": base_dir / "figures" / "simplified_maps"
    }
    
    # Create output directories if they don't exist
    for dir_path in output_dirs.values():
        os.makedirs(dir_path, exist_ok=True)
    
    # Find all raster files (*.tif) in interim and processed directories
    raster_files = []
    for directory in [interim_dir, processed_dir]:
        if directory.exists():
            raster_files.extend(list(directory.glob("*.tif")))
    
    if not raster_files:
        print("Error: No raster files found in the data directories.")
        return
    
    print(f"Found {len(raster_files)} raster files.")
    
    # Define common colormaps for different types of data
    # Match by substring in filename
    colormap_mapping = {
        "dem": "terrain",
        "hand": "terrain",
        "slope": "viridis",
        "edtw": "viridis",
        "water": "binary",
        "osm": "binary",
    }
    
    # Create simplified maps for each raster
    map_paths = []
    for raster_path in raster_files:
        print(f"Processing {raster_path.name}...")
        
        # Determine appropriate colormap based on filename
        cmap = "viridis"  # default
        for key, value in colormap_mapping.items():
            if key in raster_path.name.lower():
                cmap = value
                break
        
        # Determine appropriate value range based on filename
        vmin, vmax = 0, None
        if "dem" in raster_path.name.lower():
            vmax = 1000
        elif "slope" in raster_path.name.lower():
            vmax = 90
        elif "hand" in raster_path.name.lower():
            vmax = 200
        elif "edtw" in raster_path.name.lower():
            vmax = 1000
        elif "water" in raster_path.name.lower() or "osm" in raster_path.name.lower():
            vmax = 1
        
        # Create simplified static map (no title, no lat/lon, no scale bar, with white colorbar text)
        map_path = plot_custom_map(
            site_id=site_id,
            raster_path=str(raster_path),
            aoi_path=aoi_path,
            cmap=cmap,
            vmin=vmin,
            vmax=vmax,
            output_dirs=output_dirs
        )
        
        map_paths.append(map_path)
        print(f"  Map saved to: {map_path}")
    
    print(f"\nAll simplified maps created successfully!")
    print(f"Maps saved to: {output_dirs['static_figures']}")

if __name__ == "__main__":
    main() 