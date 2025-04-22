Feature Extraction
================

Overview
-------

After DEM conditioning, Hydro-Topo Features extracts three key hydro-topographic variables that are critical for understanding flood susceptibility and terrain characteristics:

1. Height Above Nearest Drainage (HAND)
2. Terrain Slope
3. Euclidean Distance to Waterbody (EDTW)

This section explains how each feature is computed and how to customize the extraction process.

Height Above Nearest Drainage (HAND)
----------------------------------

HAND quantifies the vertical distance to the nearest drainage channel. It's a powerful indicator of flood susceptibility - areas with low HAND values are more likely to flood than areas with high HAND values, even if they have similar absolute elevations.

The HAND calculation follows the methodology established by Rennó et al. (2008):

1. The flow path is traced downstream from each cell based on the flow direction grid
2. When a water body is encountered along the flow path, the elevation difference between the starting cell and the water cell is calculated
3. This elevation difference is the HAND value

.. code-block:: python

    from hydro_topo_features.processing import derive_products
    
    hand_path = derive_products.get_osm_hand(
        site_id="my_area",
        raw_dem="path/to/raw_dem.tif",
        osm_water_raster="path/to/osm_water.tif",
        burned_dem="path/to/burned_dem.tif",
        output_dirs=directory_dict
    )

Computationally, HAND is derived after the flow direction has been calculated from the conditioned DEM:

.. code-block:: python

    # Compute HAND
    hand = grid.compute_hand(fdir, raw_dem_data, osm_water > 0)

The raw DEM is used for elevation values, while flow direction is computed from the conditioned DEM to ensure proper routing.

Terrain Slope
-----------

Slope captures the gravitational influence on surface water flow and retention capacity. Steep slopes promote rapid runoff, while gentle slopes allow water to accumulate.

Hydro-Topo Features computes slope using Horn's method, which considers the elevation of all eight surrounding cells:

.. code-block:: python

    from hydro_topo_features.processing import derive_products
    
    slope_path = derive_products.get_slope(
        site_id="my_area",
        raw_dem="path/to/raw_dem.tif",
        output_dirs=directory_dict
    )

The slope calculation uses the raw (unconditioned) DEM as input and can be computed in either degrees or percent slope:

.. code-block:: python

    # Compute slope using Horn's method
    dy, dx = np.gradient(dem)
    slope = np.arctan(np.sqrt(dy**2 + dx**2))
    
    # Convert to degrees if requested
    if units == 'degrees':
        slope = np.degrees(slope)
    elif units == 'percent':
        slope = np.tan(slope) * 100

Euclidean Distance to Waterbody (EDTW)
------------------------------------

EDTW measures the straight-line distance from each cell to the nearest water body. It complements HAND by incorporating horizontal proximity to water, which significantly influences flood susceptibility.

.. code-block:: python

    from hydro_topo_features.processing import derive_products
    
    edtw_path = derive_products.get_edtw(
        site_id="my_area",
        osm_water_raster="path/to/osm_water.tif",
        output_dirs=directory_dict
    )

The EDTW calculation uses a distance transform on the water raster and then converts pixel distances to metric distances:

.. code-block:: python

    # Compute Euclidean distance transform in pixel units
    # 0 for water, 1 for non-water
    distance = distance_transform_edt(water == 0)
    
    # Convert to metric distance
    distance_meters = distance * pixel_size

Customization
-----------

You can customize the feature extraction process by modifying the parameters in the configuration:

.. code-block:: python

    from hydro_topo_features import config
    
    # Configure HAND parameters
    config.FEATURE_PARAMS["HAND"]["min_slope"] = 0.00005  # Increase minimum slope
    
    # Change slope units to percent
    config.FEATURE_PARAMS["SLOPE"]["units"] = "percent"
    
    # Limit maximum EDTW distance
    config.FEATURE_PARAMS["EDTW"]["max_distance"] = 10000  # meters

Usage in Analysis
---------------

These features provide complementary information about terrain characteristics and can be used together for flood susceptibility analysis, hydrological modeling, and terrain characterization.

For example:

- Areas with low HAND values, low slope, and low EDTW are typically the most flood-prone
- Areas with high HAND values, steep slopes, and high EDTW are typically the least flood-prone
- Areas with low HAND but high EDTW may be susceptible to riverine flooding but not pluvial flooding

References
---------

- Rennó, C.D., Nobre, A.D., Cuartas, L.A., Soares, J.V., Hodnett, M.G., Tomasella, J. and Waterloo, M.J. (2008). HAND, a new terrain descriptor using SRTM-DEM: Mapping terra-firme rainforest environments in Amazonia. Remote Sensing of Environment. 