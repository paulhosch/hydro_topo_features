Watershed Analysis
==================

This example demonstrates how to use the Hydro-Topo Features package to analyze a watershed and extract hydrological variables that can be used for flood susceptibility assessment.

Background
---------

Watersheds (also called catchments or drainage basins) are areas of land where precipitation collects and drains into a common outlet. Understanding the hydro-topographic characteristics of a watershed is crucial for:

- Flood risk assessment
- Water resource management
- Ecosystem analysis
- Land use planning

In this example, we'll analyze a watershed to extract HAND, EDTW, and Slope, which provide critical information about the terrain's relationship to water flow.

Step 1: Define the Watershed Area
-------------------------------

First, we need to define our watershed area. This can be done using a shapefile of the watershed boundary:

.. code-block:: python

    import os
    import geopandas as gpd
    from hydro_topo_features.pipeline import run_pipeline
    
    # Define paths
    watershed_path = "data/watersheds/sample_watershed.shp"
    dem_path = "data/dem_tiles/"
    output_path = "results/watershed_analysis"
    
    # Create output directory
    os.makedirs(output_path, exist_ok=True)
    
    # Load and examine the watershed boundary
    watershed = gpd.read_file(watershed_path)
    print(f"Watershed area: {watershed.area.values[0] / 1e6:.2f} km²")

Step 2: Run the Analysis Pipeline
------------------------------

Now we'll run the complete pipeline to extract the hydro-topographic features:

.. code-block:: python

    # Run the pipeline for the watershed
    outputs = run_pipeline(
        site_id="sample_watershed",
        aoi_path=watershed_path,
        dem_tile_folder_path=dem_path,
        output_path=output_path,
        
        # DEM conditioning parameters
        stream_burn_depth=20,
        fill_depressions=True,
        resolve_flats=True,
        
        # Feature extraction
        extract_hand=True,
        extract_edtw=True,
        extract_slope=True,
        
        # Visualization
        create_static_maps=True,
        create_interactive_map=True,
        
        # Processing
        verbose=True
    )
    
    print("Pipeline completed successfully!")
    for key, path in outputs.items():
        print(f"{key}: {path}")

Step 3: Analyze the Results
------------------------

Now let's analyze the results to better understand the watershed characteristics:

.. code-block:: python

    import numpy as np
    import rasterio
    import matplotlib.pyplot as plt
    from hydro_topo_features.visualization import plot_histograms
    
    # Load the output rasters
    hand_raster = outputs['hand_raster']
    edtw_raster = outputs['edtw_raster']
    slope_raster = outputs['slope_raster']
    
    # Create histograms of the features
    plot_histograms(
        hand_path=hand_raster,
        edtw_path=edtw_raster,
        slope_path=slope_raster,
        output_path=os.path.join(output_path, "feature_histograms.png"),
        n_bins=50,
        figsize=(15, 5)
    )
    
    # Calculate summary statistics
    with rasterio.open(hand_raster) as src:
        hand_data = src.read(1)
        hand_data = hand_data[hand_data != src.nodata]
    
    with rasterio.open(edtw_raster) as src:
        edtw_data = src.read(1)
        edtw_data = edtw_data[edtw_data != src.nodata]
    
    with rasterio.open(slope_raster) as src:
        slope_data = src.read(1)
        slope_data = slope_data[slope_data != src.nodata]
    
    # Print summary statistics
    print("\nWatershed Summary Statistics:")
    print(f"HAND: Mean = {np.mean(hand_data):.2f}m, Max = {np.max(hand_data):.2f}m")
    print(f"EDTW: Mean = {np.mean(edtw_data):.2f}m, Max = {np.max(edtw_data):.2f}m")
    print(f"Slope: Mean = {np.mean(slope_data):.2f}°, Max = {np.max(slope_data):.2f}°")
    
    # Calculate areas with low HAND values (potential flood zones)
    low_hand_threshold = 2.0  # 2 meters above nearest drainage
    low_hand_percentage = (hand_data < low_hand_threshold).sum() / len(hand_data) * 100
    
    print(f"\nPercentage of watershed within {low_hand_threshold}m of drainage: {low_hand_percentage:.2f}%")

Step 4: Visualize Flood-Prone Areas
--------------------------------

Now we'll create a map highlighting areas that are potentially prone to flooding (low HAND values):

.. code-block:: python

    from hydro_topo_features.visualization import create_static_map
    
    # Create a map of flood-prone areas
    flood_map = create_static_map(
        raster_path=hand_raster,
        output_path=os.path.join(output_path, "flood_prone_areas.png"),
        title="Potential Flood-Prone Areas",
        colormap="Blues_r",  # Reversed Blues colormap (darker = lower HAND)
        add_colorbar=True,
        colorbar_label="Height Above Nearest Drainage (m)",
        vmin=0,
        vmax=10,  # Focus on areas less than 10m above drainage
        custom_classes=[0, 1, 2, 5, 10],
        class_labels=["0-1m (High Risk)", "1-2m (Moderate Risk)", 
                     "2-5m (Low Risk)", "5-10m (Very Low Risk)"],
        add_water_overlay=True,
        water_path=outputs['water_raster'],
        add_hillshade=True,
        dem_path=outputs['dem_raster'],
        hillshade_opacity=0.3,
        add_scalebar=True,
        add_north_arrow=True
    )
    
    print(f"Flood risk map created: {flood_map}")

Step 5: Export Results for Further Analysis
----------------------------------------

Finally, we'll export the data for use in other GIS applications or machine learning models:

.. code-block:: python

    from hydro_topo_features.utils import export_features_as_single_tif
    
    # Export all features as a single multi-band GeoTIFF
    combined_path = export_features_as_single_tif(
        hand_path=hand_raster,
        edtw_path=edtw_raster,
        slope_path=slope_raster,
        output_path=os.path.join(output_path, "combined_features.tif")
    )
    
    print(f"Combined features exported to: {combined_path}")
    
    # Export as CSV for machine learning
    from hydro_topo_features.utils import rasters_to_csv
    
    csv_path = rasters_to_csv(
        raster_paths=[hand_raster, edtw_raster, slope_raster],
        band_names=["HAND", "EDTW", "Slope"],
        output_path=os.path.join(output_path, "features.csv"),
        sample_percentage=10  # Use 10% of the pixels to keep file size manageable
    )
    
    print(f"CSV exported to: {csv_path}")

Conclusion
---------

This example demonstrated how to use Hydro-Topo Features to analyze a watershed and identify potential flood-prone areas based on HAND values. The extracted features provide valuable information for flood risk assessment, watershed management, and hydrological modeling.

The low HAND values correspond to areas close to the drainage network and are more susceptible to flooding, while the EDTW and Slope provide additional context about the terrain characteristics that influence water flow and accumulation.

Complete Code
-----------

The complete code for this example is available in the GitHub repository:
https://github.com/paulhosch/hydro-topo-features/tree/main/examples/watershed_analysis.py 