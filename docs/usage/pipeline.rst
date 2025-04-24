Processing Pipeline
=================

The Hydro-Topo Features package implements a comprehensive workflow for extraction of hydro-topographic features from digital elevation data and water feature information.

Pipeline Overview
----------------

.. figure:: ../images/pipeline.png
   :alt: Hydro-Topo Features Processing Pipeline
   :align: center
   :width: 100%
   
   *Quasi Global and Automatic Pipeline To Compute the Hydro Topographic Descriptors: (X1) HAND, (X2) Slope and (X3) Euclidean Distance To Water, using (A1) FathomDEM and (A2) OpenStreetMap Water as Input Data. A (B) Conditioned DEM is computed to ensure drainage and an accurate (C) Flow Direction approximation.*

The workflow consists of the following main steps:

1. **Data Preparation**

   - **Digital Elevation Model (DEM)**: The process begins with a 30m resolution DEM (e.g., FathomDEM)
   - **OpenStreetMap Water Layer**: Water features are extracted from OpenStreetMap data

2. **DEM Conditioning**

   - **Stream Burning**: Lowering the DEM by 20m along OSM-derived water features
   - **Pit & Depression Filling**: Removing depressions that would create artificial sinks
   - **Flat Resolving**: Creating artificial drainage gradients in flat areas

3. **Flow Direction Computation**

   - Using the D8 algorithm to determine flow directions from each cell to its steepest downslope neighbor

4. **Feature Extraction**

   - **HAND (Height Above Nearest Drainage)**: Vertical distance to the nearest drainage channel
   - **Terrain Slope**: Maximum rate of elevation change in the terrain
   - **EDTW (Euclidean Distance To Water)**: Straight-line distance to the nearest water body

The generated hydro-topographic features provide critical contextual information for:
- Flood susceptibility analysis
- Hydrological modeling
- Terrain characterization 
- Water resource management

Running the Pipeline
-------------------

The entire pipeline can be executed with a single function call:

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

For more details on specific steps, refer to:

- :doc:`dem_conditioning` - Details on the DEM conditioning process
- :doc:`feature_extraction` - Information about feature extraction methods
- :doc:`visualization` - Guidance on visualizing the extracted features 