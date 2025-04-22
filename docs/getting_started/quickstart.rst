Quick Start Guide
===============

This guide will walk you through a basic workflow using the Hydro-Topo Features package. The examples below demonstrate how to extract hydro-topographic features from a sample area.

Basic Usage
----------

The simplest way to use the package is through the main ``run_pipeline`` function:

.. code-block:: python

   from hydro_topo_features.pipeline import run_pipeline
   
   outputs = run_pipeline(
       site_id="my_area",
       aoi_path="path/to/area_of_interest.shp",
       dem_tile_folder_path="path/to/dem_tiles/",
       output_path="outputs",
       create_static_maps=True,
       create_interactive_map=True
   )
   
   # Print output paths
   for key, path in outputs.items():
       print(f"{key}: {path}")

This will:

1. Load and merge DEM tiles that intersect with your area of interest
2. Extract water features from OpenStreetMap
3. Perform DEM conditioning (stream burning, pit filling, etc.)
4. Compute HAND, slope, and EDTW
5. Generate visualizations if requested
6. Return a dictionary with paths to all output files

Command Line Usage
----------------

The package also provides a command line interface through the ``test_hydro_topo.py`` script:

.. code-block:: bash

   python test_hydro_topo.py --site-id my_area \
                            --aoi-path path/to/area_of_interest.shp \
                            --dem-dir path/to/dem_tiles/ \
                            --output-dir outputs \
                            --static-maps \
                            --interactive-map

Output Structure
--------------

After running the pipeline, your output directory will have the following structure:

.. code-block:: text

   outputs/
   └── SITE_ID/
       ├── raw/
       │   └── raw_dem.tif
       ├── interim/
       │   ├── osm_water_vector.gpkg
       │   └── osm_water_raster.tif
       ├── processed/
       │   ├── burned_dem.tif
       │   ├── hand.tif
       │   ├── slope.tif
       │   └── edtw.tif
       └── figures/
           ├── static/
           │   ├── raw_dem_map.svg
           │   ├── burned_dem_map.svg
           │   ├── osm_water_map.svg
           │   ├── hand_map.svg
           │   ├── slope_map.svg
           │   └── edtw_map.svg
           └── interactive/
               └── interactive_map.html 