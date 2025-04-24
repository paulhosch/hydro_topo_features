Methodology
===========

.. figure:: images/pipeline.png
   :alt: Hydro-Topo Features Processing Pipeline
   :align: center
   :width: 100%
   
   *Quasi Global and Automatic Pipeline To Compute the Hydro Topographic Descriptors: (X1) HAND, (X2) Slope and (X3) Euclidean Distance To Water, using (A1) FathomDEM and (A2) OpenStreetMap Water as Input Data. A (B) Conditioned DEM is computed to ensure drainage and an accurate (C) Flow Direction approximation.*

Data Sources
-----------

Global 30m Terrain Model (FathomDEM)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This study employs FathomDEM (Uhe et al., 2025), a high-quality terrain model available at 1 arc second (~30 m) grid spacing between 60°S and 80°N. FathomDEM, a Digital Terrain Model (DTM), represents the bare earth surface excluding all natural and anthropogenic features such as vegetation and structures. It is derived from the Copernicus DEM (ESA, 2021) and refined using a hybrid visual transformer model with additional predictors to remove buildings, trees, and other non-terrain elements. Comparative evaluations have demonstrated FathomDEM's superior performance against commonly used DTMs such as FABDEM (Uhe et al., 2025).

Global Water Layer
^^^^^^^^^^^^^^^^^

The water layer was derived from OpenStreetMap (OSM) water features (OpenStreetMap, 2023), adapting and simplifying the workflow established in MERIT Hydro (Yamazaki et al., 2019). While MERIT Hydro utilized three different data sources (G1WBM, GSWO, and OSM) to create a probabilistic water layer, our approach streamlines the process by exclusively using OSM water-related features. These features were extracted using the following OSM tags (Yamazaki et al., 2019):

- "natural = water"
- "waterway = *"
- "landuse = reservoir"

This simplification was justified through visual comparisons of OSM data with optical and aerial imagery, which confirmed sufficient accuracy in representing channel networks within our AOIs. (Multi-)Polygon and (Multi-)Line OSM water features were rasterized at 3 arc-second resolution to match the DEM. The decision was also based on the assumption that during flood events, high precipitation and elevated water levels would ensure that even non-permanent and smaller channels would be water-filled.

DEM Conditioning
---------------

To ensure accurate hydrological modeling, we implemented a four-step DEM conditioning process inspired by MERIT Hydro (Yamazaki et al., 2019) that enforces known drainage patterns, removes artifacts, and establishes continuous flow paths that would otherwise be compromised by data inconsistencies and terrain ambiguities.

Stream Burning
^^^^^^^^^^^^^

Stream burning was performed by lowering the elevation of the original FathomDEM by dZ=20m along the OSM-derived water features. This value was selected based on the maximum value of the probabilistic calculations used in MERIT Hydro, with recent research by Chen et al. (2024) suggesting that even higher stream burning values (40-50m) may be effective. Our experimental testing confirmed that a 20m constant channel depth provided satisfactory results. For computational efficiency, no smoothing (e.g., Gaussian blurring) was applied, as experiments demonstrated no significant influence on computed flow directions.

Pit Filling
^^^^^^^^^^

Single-cell depressions (pits) in the DEM, which prevent downstream flow and often result from noise or data artifacts, were identified and filled by raising their elevation to match the lowest adjacent neighbor. This conservative correction ensures minimal alteration to the DEM while enabling proper flow direction calculation. The procedure was implemented efficiently in PySheds through Numba-accelerated routines.

Depression Filling
^^^^^^^^^^^^^^^^^

Multi-cell depressions (sinks) surrounded by higher terrain can disrupt hydrological modeling by creating unintended internal basins. These features were removed using the Priority-Flood algorithm, which fills each depression to the level of its lowest exterior spill point, ensuring water routing toward depression edges. This computationally efficient and robust algorithm is particularly suitable for large-scale DEMs (Barnes et al., 2014) and implemented in PySheds (Bartos, 2018).

Resolving Flats
^^^^^^^^^^^^^^

Following pit and depression removal, large areas of uniform elevation (flats) can remain and be introduced through the filling process, resulting in ambiguous flow directions. To resolve these flats, we implemented the algorithm proposed by Barnes et al. (2015) in PySheds (Bartos, 2018), which constructs an artificial drainage gradient across flat areas by combining gradients from higher terrain and toward lower terrain. Small elevation increments proportional to this synthetic gradient were applied to the DEM, ensuring water flows across flat regions while preserving the relative elevation relationships in surrounding terrain.

Flow Direction
-------------

Flow direction was calculated from the Conditioned DEM using the deterministic D8 method (O'Callaghan & Mark, 1984), where water from each grid cell flows to the steepest downslope neighbor among the eight surrounding cells. Using the Conditioned DEM, a more accurate computation of the flow direction is possible. This operation was implemented using PySheds (Bartos, 2018), providing the last required input for the subsequent HAND calculation.

Hydro-Topographic Variable Calculation
-------------------------------------

Height Above Nearest Drainage (HAND)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

HAND was calculated following the methodology established by Rennó et al. (2008). For each cell in the DEM, the flow path based on the flow direction was traced downstream until reaching the nearest water cell in the OSM raster. Then using the raw FathomDEM, the elevation difference between the current cell and the first encountered water cell was defined as the HAND value. This metric effectively quantifies the vertical distance to the nearest drainage channel, providing a powerful indicator of flood susceptibility.

Often the water layer for the stream burning and the calculation of HAND is derived by setting a stream initiation accumulation threshold. However, there are no definitive best practices, and determining appropriate thresholds can vary drastically (e.g., Chen et al., 2024 investigated accumulation thresholds ranging from 2,500 to 30,000 cells in a 30m grid), becoming a major challenge in delineating an accurate river network. These threshold values are highly dependent on regional geomorphology, catchment size, climate conditions, seasonal variability, and underlying geological formations, requiring manual calibration for each study area to achieve adequate representation of the drainage network.

Terrain Slope
^^^^^^^^^^^^

The terrain slope was calculated from the unconditioned FathomDEM using the standard eight-direction (D8) method, representing the maximum rate of elevation change between each cell and its eight neighbors and is measured in degrees. The slope captures, for example, the gravitational influence on surface water flow and retention capacity.

Euclidean Distance to Waterbody (EDTW)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Euclidean distance to the next waterbody (EDTW) was computed as the straight-line distance from each cell to the nearest water cell in the OSM water raster. This metric complements HAND by incorporating horizontal proximity to water bodies, which significantly influences flood susceptibility. 