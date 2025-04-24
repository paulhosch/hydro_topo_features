Visualization
=============

The Hydro-Topo Features package offers flexible visualization options for exploring and presenting the extracted hydro-topographic variables. This section provides guidance on how to create both static and interactive maps from your results.

Static Maps
----------

Static maps are useful for publications, reports, and presentations. The package includes functionality to create customized maps of HAND, EDTW, and Slope variables with options for color scales, annotations, and map elements.

Basic Static Map
^^^^^^^^^^^^^^^

The following example demonstrates how to create a basic static map of the HAND variable:

.. code-block:: python

    from hydro_topo_features.visualization import create_static_map
    
    # Create a static map of HAND values
    map_file = create_static_map(
        raster_path="path/to/hand_result.tif",
        output_path="hand_map.png",
        title="Height Above Nearest Drainage",
        colormap="terrain",
        add_colorbar=True
    )
    
    print(f"Map saved to: {map_file}")

Customized Map
^^^^^^^^^^^^^

For more advanced visualization needs, you can customize various aspects of the map:

.. code-block:: python

    from hydro_topo_features.visualization import create_static_map
    
    # Create a customized map
    map_file = create_static_map(
        raster_path="path/to/hand_result.tif",
        output_path="custom_hand_map.png",
        title="HAND Values for Study Area",
        colormap="viridis_r",  # Reversed viridis colormap
        add_colorbar=True,
        colorbar_label="Height (m)",
        add_scalebar=True,
        add_north_arrow=True,
        mask_value=0,  # Mask out zero values
        add_hillshade=True,  # Add hillshading for terrain visualization
        hillshade_opacity=0.3,
        dem_path="path/to/dem.tif",  # For hillshade
        add_water_overlay=True,
        water_path="path/to/water_mask.tif",
        water_color="blue",
        water_opacity=0.5,
        add_basemap=True,
        basemap_style="OpenStreetMap"
    )

Interactive Web Maps
------------------

Interactive web maps allow for dynamic exploration of the data. The package provides functionality to create browser-based maps that users can pan, zoom, and query.

Basic Interactive Map
^^^^^^^^^^^^^^^^^^^

To create a simple interactive map that can be opened in a web browser:

.. code-block:: python

    from hydro_topo_features.visualization import create_interactive_map
    
    # Create an interactive map with all three variables
    map_file = create_interactive_map(
        hand_path="path/to/hand_result.tif",
        edtw_path="path/to/edtw_result.tif",
        slope_path="path/to/slope_result.tif",
        output_path="interactive_map.html",
        add_water_layer=True,
        water_path="path/to/water_mask.tif"
    )
    
    print(f"Interactive map saved to: {map_file}")

Advanced Interactive Map
^^^^^^^^^^^^^^^^^^^^^^

For more advanced interactive maps with additional features:

.. code-block:: python

    from hydro_topo_features.visualization import create_interactive_map
    
    # Create an advanced interactive map
    map_file = create_interactive_map(
        hand_path="path/to/hand_result.tif",
        edtw_path="path/to/edtw_result.tif",
        slope_path="path/to/slope_result.tif",
        output_path="advanced_map.html",
        title="Hydro-Topographic Analysis Results",
        description="Interactive map showing HAND, EDTW, and Slope values for the study area.",
        add_water_layer=True,
        water_path="path/to/water_mask.tif",
        add_dem_layer=True,
        dem_path="path/to/dem.tif",
        add_basemap_selector=True,
        default_basemap="Satellite",
        add_legend=True,
        add_scale=True,
        add_fullscreen=True,
        add_measure=True,
        add_opacity_slider=True,
        add_screenshot=True,
        add_geocoder=True
    )

Batch Visualization
-----------------

If you have multiple study areas or time periods, you can create a batch of maps efficiently:

.. code-block:: python

    from hydro_topo_features.visualization import batch_create_maps
    
    # Define the study areas
    study_areas = [
        {
            "name": "Area1",
            "hand_path": "path/to/area1/hand.tif",
            "edtw_path": "path/to/area1/edtw.tif",
            "slope_path": "path/to/area1/slope.tif"
        },
        {
            "name": "Area2",
            "hand_path": "path/to/area2/hand.tif",
            "edtw_path": "path/to/area2/edtw.tif",
            "slope_path": "path/to/area2/slope.tif"
        }
    ]
    
    # Create static and interactive maps for all study areas
    map_files = batch_create_maps(
        study_areas=study_areas,
        output_dir="maps/",
        create_static=True,
        create_interactive=True,
        colormap="viridis",
        add_water_layers=True
    )
    
    for area_name, files in map_files.items():
        print(f"Maps for {area_name}:")
        for map_type, file_path in files.items():
            print(f"  - {map_type}: {file_path}")

Exporting Visualizations
----------------------

Maps created with Hydro-Topo Features can be exported in various formats:

- Static maps: PNG, JPEG, PDF, SVG, TIFF
- Interactive maps: HTML (for web browsers), standalone applications

To export a static map in multiple formats:

.. code-block:: python

    from hydro_topo_features.visualization import export_map
    
    # Export a static map in multiple formats
    export_map(
        map_file="hand_map.png",
        formats=["pdf", "svg", "jpeg"],
        output_dir="exports/"
    )

For interactive maps, you can convert them to standalone applications:

.. code-block:: python

    from hydro_topo_features.visualization import convert_to_app
    
    # Convert an interactive map to a standalone application
    app_file = convert_to_app(
        map_file="interactive_map.html",
        output_path="hydro_map_app",
        app_name="Hydro-Topo Map Viewer",
        icon_path="path/to/icon.png"
    )
    
    print(f"Standalone application created at: {app_file}") 