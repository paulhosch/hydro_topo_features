DEM Conditioning
==============

Overview
-------

DEM conditioning is a critical step in hydrological analysis to ensure accurate flow routing and downstream calculations. The Hydro-Topo Features package implements a four-step DEM conditioning process inspired by MERIT Hydro (Yamazaki et al., 2019) that enforces known drainage patterns, removes artifacts, and establishes continuous flow paths.

The conditioning process includes:

1. Stream burning
2. Pit filling
3. Depression filling
4. Resolving flats

Stream Burning
-------------

Stream burning involves lowering the elevation of the DEM along known water features, forcing the flow routing algorithm to recognize these features as preferential flow paths.

In Hydro-Topo Features, stream burning is performed by lowering the elevation of the original DEM by 20 meters along OSM-derived water features. This value was selected based on experimental testing and provides satisfactory results for most use cases.

.. code-block:: python

    from hydro_topo_features.processing import burn_dem
    
    burned_dem_path = burn_dem.burn_streams(
        site_id="my_area",
        raw_dem="path/to/raw_dem.tif",
        osm_water_raster="path/to/osm_water.tif",
        output_dirs=directory_dict
    )

Pit Filling
----------

Single-cell depressions (pits) in the DEM prevent downstream flow and are often the result of noise or data artifacts. Hydro-Topo Features identifies and fills these pits by raising their elevation to match the lowest adjacent neighbor, ensuring minimal alteration to the DEM while enabling proper flow direction calculation.

This process is part of the HAND computation in the ``derive_products.py`` module and uses PySheds for efficient implementation:

.. code-block:: python

    # Initialize grid
    grid = Grid.from_raster(burned_dem_path)
    
    # Read raster data
    burned_dem_data = grid.read_raster(burned_dem_path)
    
    # Fill pits in DEM
    pit_filled_dem = grid.fill_pits(burned_dem_data)

Depression Filling
----------------

Multi-cell depressions (sinks) surrounded by higher terrain can disrupt hydrological modeling by creating unintended internal basins. Hydro-Topo Features removes these features using the Priority-Flood algorithm, which fills each depression to the level of its lowest exterior spill point.

This algorithm is particularly efficient for large-scale DEMs:

.. code-block:: python

    # Fill depressions in DEM
    flooded_dem = grid.fill_depressions(pit_filled_dem)

Resolving Flats
-------------

Following pit and depression removal, large areas of uniform elevation (flats) can remain or be introduced through the filling process, resulting in ambiguous flow directions. Hydro-Topo Features resolves these flats by applying an algorithm that constructs an artificial drainage gradient across flat areas.

This algorithm combines gradients from higher terrain and toward lower terrain, applying small elevation increments to ensure water flows across flat regions while preserving the relative elevation relationships:

.. code-block:: python

    # Resolve flats in DEM
    inflated_dem = grid.resolve_flats(flooded_dem)

Flow Direction Calculation
------------------------

Once the DEM has been conditioned, flow direction is calculated using the deterministic D8 method (O'Callaghan & Mark, 1984), where water from each grid cell flows to the steepest downslope neighbor among the eight surrounding cells.

.. code-block:: python

    # Compute flow direction
    dirmap = (64, 128, 1, 2, 4, 8, 16, 32)
    fdir = grid.flowdir(inflated_dem, dirmap=dirmap, flats=-1, pits=-2, nodata_out=0)

This flow direction grid is then used for computing HAND values.

References
---------

- Yamazaki, D., Ikeshima, D., Sosa, J., Bates, P.D., Allen, G.H. and Pavelsky, T.M. (2019). MERIT Hydro: A high-resolution global hydrography map based on latest topography dataset. Water Resources Research.
- O'Callaghan, J.F. and Mark, D.M. (1984). The extraction of drainage networks from digital elevation data. Computer Vision, Graphics, and Image Processing.
- Barnes, R., Lehman, C., and Mulla, D. (2014). Priority-flood: An optimal depression-filling and watershed-labeling algorithm for digital elevation models.
- Barnes, R., Lehman, C., and Mulla, D. (2015). An efficient assignment of drainage direction over flat surfaces in raster digital elevation models. 