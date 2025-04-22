Configuration
=============

Hydro-Topo Features provides a flexible configuration system that allows you to customize various aspects of the processing pipeline. This guide explains the key configuration options available.

Configuration File
----------------

The main configuration options are defined in ``hydro_topo_features/config.py``. You can modify these settings to customize the behavior of the package.

Directory Structure
-----------------

The directory structure defines where different types of files are stored:

.. code-block:: python

    DIRECTORY_STRUCTURE = {
        "RAW": "raw",         # Original data without processing
        "INTERIM": "interim", # Intermediate processing results
        "PROCESSED": "processed", # Final data products
        "FIGURES": "figures", # Visualizations
        "STATIC": "static",   # Static visualizations
        "INTERACTIVE": "interactive" # Interactive visualizations
    }

DEM Processing Parameters
-----------------------

These parameters control how the DEM is processed:

.. code-block:: python

    DEM_PROCESSING = {
        "BURN_DEPTH": 20,  # meters to burn streams into DEM
        "NODATA_VALUE": 0, # Value for no data
        "DEFAULT_CRS": "EPSG:4326", # WGS84
        "RASTERIZE_RESOLUTION": 30, # meters
    }

The ``BURN_DEPTH`` parameter is particularly important - it defines how deeply to burn stream channels into the DEM. The default of 20 meters was selected based on experimental testing and provides satisfactory results for most use cases.

Feature Computation Parameters
----------------------------

These parameters control how different features are computed:

.. code-block:: python

    FEATURE_PARAMS = {
        "HAND": {
            "min_slope": 0.00001,  # minimum slope for flow direction
            "routing": "d8"  # flow routing algorithm
        },
        "SLOPE": {
            "units": "degrees",  # or 'percent'
            "algorithm": "horn"  # Horn's method for slope calculation
        },
        "EDTW": {
            "max_distance": None,  # None for unlimited
            "units": "meters"
        }
    }

Visualization Settings
--------------------

The visualization settings control how different rasters are displayed:

.. code-block:: python

    RASTER_VIS = {
        "raw_dem": {
            "name": "Raw DEM",
            "unit": "m",
            "vmin": 0,
            "vmax": 1000,
            "cmap": "terrain"
        },
        "burned_dem": {
            "name": "Burned DEM",
            "unit": "m",
            "vmin": 0,
            "vmax": 1000,
            "cmap": "terrain"
        },
        "hand": {
            "name": "Height Above Nearest Drainage",
            "unit": "m",
            "vmin": 0,
            "vmax": 50,
            "cmap": "viridis"
        },
        "slope": {
            "name": "Slope",
            "unit": "°",
            "vmin": 0,
            "vmax": 45,
            "cmap": "YlOrRd"
        },
        "edtw": {
            "name": "Euclidean Distance to Water",
            "unit": "m",
            "vmin": 0,
            "vmax": 5000,
            "cmap": "Blues_r"
        },
        "osm_water": {
            "name": "OSM Water Features",
            "unit": "",
            "vmin": 0,
            "vmax": 1,
            "cmap": "Blues"
        }
    }

Custom Configuration
------------------

For more advanced customization, you can modify the configuration file directly or create your own configuration by subclassing or replacing the default settings:

.. code-block:: python

    from hydro_topo_features import config
    
    # Modify a parameter
    config.DEM_PROCESSING["BURN_DEPTH"] = 30
    
    # Use custom visualization settings
    config.RASTER_VIS["hand"]["vmax"] = 100
    config.RASTER_VIS["hand"]["cmap"] = "plasma"
    
    # Now run the pipeline with these custom settings
    from hydro_topo_features.pipeline import run_pipeline
    run_pipeline(...) 