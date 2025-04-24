Quick Start Guide
===============

This guide will help you get started with the Hydro-Topo Features package and run your first analysis. We'll extract HAND, EDTW, and Slope features for a sample area.

Basic Usage
----------

Here's a simple example to extract hydro-topographic features from a DEM and OSM water data:

.. code-block:: python

    from hydro_topo_features.pipeline import run_pipeline
    
    # Run the complete pipeline
    outputs = run_pipeline(
        site_id="my_test_area",
        aoi_path="path/to/area_of_interest.shp",
        dem_tile_folder_path="path/to/dem_tiles/",
        output_path="outputs",
        create_static_maps=True,
        create_interactive_map=True
    )
    
    # Print the output paths
    for key, path in outputs.items():
        print(f"{key}: {path}")

This will:

1. Extract the DEM for the area of interest
2. Download OSM water features
3. Condition the DEM (stream burning, pit/depression filling, flat resolving)
4. Calculate flow direction
5. Extract HAND, EDTW, and Slope features
6. Generate static and interactive maps
7. Return paths to all outputs

Example with Custom Parameters
---------------------------

You can customize various aspects of the pipeline:

.. code-block:: python

    from hydro_topo_features.pipeline import run_pipeline
    
    outputs = run_pipeline(
        site_id="custom_area",
        aoi_path="path/to/area_of_interest.shp",
        dem_tile_folder_path="path/to/dem_tiles/",
        output_path="outputs/custom_run",
        
        # DEM conditioning parameters
        stream_burn_depth=30,  # 30m depth for stream burning
        fill_depressions=True,
        resolve_flats=True,
        
        # Feature extraction parameters
        extract_hand=True,
        extract_edtw=True,
        extract_slope=True,
        flow_direction_algorithm="D8",  # or "MFD" for multi-flow direction
        
        # Visualization parameters
        create_static_maps=True,
        create_interactive_map=True,
        colormap="viridis",
        add_hillshade=True,
        hillshade_opacity=0.3,
        
        # Processing parameters
        chunk_size=4000,  # Process in 4000x4000 pixel chunks
        no_data_value=-9999,
        verbose=True
    )

Command Line Interface
-------------------

Hydro-Topo Features also provides a command-line interface for easy execution:

.. code-block:: bash

    python -m hydro_topo_features.cli \
        --site-id my_test_area \
        --aoi-path path/to/area_of_interest.shp \
        --dem-dir path/to/dem_tiles/ \
        --output-dir outputs \
        --static-maps \
        --interactive-map

For a list of all available options:

.. code-block:: bash

    python -m hydro_topo_features.cli --help

Complete Example Workflow
-----------------------

Here's a complete workflow example:

.. code-block:: python

    import os
    from hydro_topo_features.pipeline import run_pipeline
    from hydro_topo_features.visualization import create_static_map
    
    # Define area of interest and paths
    site_id = "sample_watershed"
    aoi_path = "data/sample_watershed.shp"
    dem_path = "data/dem_tiles/"
    output_path = "results/sample_watershed"
    
    # Create output directory if it doesn't exist
    os.makedirs(output_path, exist_ok=True)
    
    # Run the pipeline
    outputs = run_pipeline(
        site_id=site_id,
        aoi_path=aoi_path,
        dem_tile_folder_path=dem_path,
        output_path=output_path,
        stream_burn_depth=20,
        extract_hand=True,
        extract_edtw=True,
        extract_slope=True,
        create_static_maps=True,
        create_interactive_map=True,
        verbose=True
    )
    
    print("Pipeline completed successfully!")
    print(f"Results saved to: {output_path}")
    
    # Access individual output rasters
    hand_raster = outputs['hand_raster']
    edtw_raster = outputs['edtw_raster']
    slope_raster = outputs['slope_raster']
    
    # Create a custom map with all features
    combined_map = create_static_map(
        hand_path=hand_raster,
        edtw_path=edtw_raster,
        slope_path=slope_raster,
        output_path=os.path.join(output_path, "combined_features_map.png"),
        title=f"Hydro-Topo Features: {site_id}",
        add_legend=True,
        add_scale=True,
        add_north_arrow=True
    )
    
    print(f"Combined map created: {combined_map}")

What's Next?
----------

Once you've successfully run the pipeline, you can:

- Explore the :doc:`../usage/index` section for more advanced usage scenarios
- Learn about :doc:`../usage/dem_conditioning` to customize the DEM preparation process
- Dive into :doc:`../usage/feature_extraction` for details on the feature extraction algorithms
- Check out :doc:`../usage/visualization` for advanced visualization options
- See :doc:`../examples/index` for real-world applications 