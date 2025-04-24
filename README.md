# Hydro-Topo Features

A Python package for the automated extraction of hydro-topographic features from Digital Elevation Models (DEMs) and OpenStreetMap (OSM) water data. These features are critical for understanding flood susceptibility and analyzing terrain characteristics.

[![PyPI Version](https://img.shields.io/pypi/v/hydro-topo-features.svg)](https://pypi.org/project/hydro-topo-features/)
[![Documentation Status](https://readthedocs.org/projects/hydro-topo-features/badge/?version=latest)](https://hydro-topo-features.readthedocs.io/en/latest/?badge=latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

This package implements a quasi-global, automated workflow for the extraction of three key hydro-topographic variables:

1. **Height Above Nearest Drainage (HAND)**: Vertical distance to the nearest drainage channel
2. **Euclidean Distance to Waterbody (EDTW)**: Straight-line distance to the nearest water body
3. **Terrain Slope**: Maximum rate of elevation change

The extracted features provide critical contextual information for flood susceptibility analysis, hydrological modeling, and terrain characterization.

## Key Features

- **DEM Conditioning**: Implemented using the four-step process inspired by MERIT Hydro:
  - Stream burning (lowering the DEM by 20m along OSM water features)
  - Pit filling (removing single-cell depressions)
  - Depression filling (removing multi-cell depressions)
  - Resolving flats (creating synthetic flow gradients)
- **Feature Extraction**:
  - HAND: Height Above Nearest Drainage computation
  - EDTW: Euclidean Distance to Waterbody computation
  - Slope: Terrain gradient calculation using Horn's method
- **Data Sources**:
  - DEM: Compatible with FathomDEM (1 arc second ~30m grid spacing)
  - Water features: Automatically extracted from OpenStreetMap (OSM)
- **Visualization**:
  - Static maps with customizable parameters
  - Interactive web maps for exploration

## Methodology

<figure style="text-align: center;">
  <img src="pipeline.png" alt="Hydro-Topo Features Processing Pipeline" width="80%">
  <figcaption><em>Figure 1:</em> Quasi Global and Automatic Pipeline To Compute the Hydro Topographic Descriptors: (X1) HAND, (X2) Slope and (X3) Euclidean Distance To Water, using (A1) FathomDEM and (A2) OpenStreetMap Water as Input Data. A (B) Conditioned DEM is computed to ensure drainage and an accurate (C) Flow Direction approximation.</figcaption>
</figure>

### Data Sources

#### Global 30m Terrain Model (FathomDEM)

This study employs FathomDEM (Uhe et al., 2025), a high-quality terrain model available at 1 arc second (~30 m) grid spacing between 60°S and 80°N. FathomDEM, a Digital Terrain Model (DTM), represents the bare earth surface excluding all natural and anthropogenic features such as vegetation and structures. It is derived from the Copernicus DEM (ESA, 2021) and refined using a hybrid visual transformer model with additional predictors to remove buildings, trees, and other non-terrain elements. Comparative evaluations have demonstrated FathomDEM's superior performance against commonly used DTMs such as FABDEM (Uhe et al., 2025).

#### Global Water Layer

The water layer was derived from OpenStreetMap (OSM) water features (OpenStreetMap, 2023), adapting and simplifying the workflow established in MERIT Hydro (Yamazaki et al., 2019). While MERIT Hydro utilized three different data sources (G1WBM, GSWO, and OSM) to create a probabilistic water layer, our approach streamlines the process by exclusively using OSM water-related features. These features were extracted using the following OSM tags (Yamazaki et al., 2019):

- "natural = water"
- "waterway = \*"
- "landuse = reservoir"

This simplification was justified through visual comparisons of OSM data with optical and aerial imagery, which confirmed sufficient accuracy in representing channel networks within our AOIs. (Multi-)Polygon and (Multi-)Line OSM water features were rasterized at 3 arc-second resolution to match the DEM. The decision was also based on the assumption that during flood events, high precipitation and elevated water levels would ensure that even non-permanent and smaller channels would be water-filled.

### DEM Conditioning

To ensure accurate hydrological modeling, we implemented a four-step DEM conditioning process inspired by MERIT Hydro (Yamazaki et al., 2019) that enforces known drainage patterns, removes artifacts, and establishes continuous flow paths that would otherwise be compromised by data inconsistencies and terrain ambiguities.

#### Stream Burning

Stream burning was performed by lowering the elevation of the original FathomDEM by dZ=20m along the OSM-derived water features. This value was selected based on the maximum value of the probabilistic calculations used in MERIT Hydro, with recent research by Chen et al. (2024) suggesting that even higher stream burning values (40-50m) may be effective. Our experimental testing confirmed that a 20m constant channel depth provided satisfactory results. For computational efficiency, no smoothing (e.g., Gaussian blurring) was applied, as experiments demonstrated no significant influence on computed flow directions.

#### Pit Filling

Single-cell depressions (pits) in the DEM, which prevent downstream flow and often result from noise or data artifacts, were identified and filled by raising their elevation to match the lowest adjacent neighbor. This conservative correction ensures minimal alteration to the DEM while enabling proper flow direction calculation. The procedure was implemented efficiently in PySheds through Numba-accelerated routines.

#### Depression Filling

Multi-cell depressions (sinks) surrounded by higher terrain can disrupt hydrological modeling by creating unintended internal basins. These features were removed using the Priority-Flood algorithm, which fills each depression to the level of its lowest exterior spill point, ensuring water routing toward depression edges. This computationally efficient and robust algorithm is particularly suitable for large-scale DEMs (Barnes et al., 2014) and implemented in PySheds (Bartos, 2018).

#### Resolving Flats

Following pit and depression removal, large areas of uniform elevation (flats) can remain and be introduced through the filling process, resulting in ambiguous flow directions. To resolve these flats, we implemented the algorithm proposed by Barnes et al. (2015) in PySheds (Bartos, 2018), which constructs an artificial drainage gradient across flat areas by combining gradients from higher terrain and toward lower terrain. Small elevation increments proportional to this synthetic gradient were applied to the DEM, ensuring water flows across flat regions while preserving the relative elevation relationships in surrounding terrain.

### Flow Direction

Flow direction was calculated from the Conditioned DEM using the deterministic D8 method (O'Callaghan & Mark, 1984), where water from each grid cell flows to the steepest downslope neighbor among the eight surrounding cells. Using the Conditioned DEM, a more accurate computation of the flow direction is possible. This operation was implemented using PySheds (Bartos, 2018), providing the last required input for the subsequent HAND calculation.

### Hydro-Topographic Variable Calculation

#### Height Above Nearest Drainage (HAND)

HAND was calculated following the methodology established by Rennó et al. (2008). For each cell in the DEM, the flow path based on the flow direction was traced downstream until reaching the nearest water cell in the OSM raster. Then using the raw FathomDEM, the elevation difference between the current cell and the first encountered water cell was defined as the HAND value. This metric effectively quantifies the vertical distance to the nearest drainage channel, providing a powerful indicator of flood susceptibility.

Often the water layer for the stream burning and the calculation of HAND is derived by setting a stream initiation accumulation threshold. However, there are no definitive best practices, and determining appropriate thresholds can vary drastically (e.g., Chen et al., 2024 investigated accumulation thresholds ranging from 2,500 to 30,000 cells in a 30m grid), becoming a major challenge in delineating an accurate river network. These threshold values are highly dependent on regional geomorphology, catchment size, climate conditions, seasonal variability, and underlying geological formations, requiring manual calibration for each study area to achieve adequate representation of the drainage network.

#### Terrain Slope

The terrain slope was calculated from the unconditioned FathomDEM using the standard eight-direction (D8) method, representing the maximum rate of elevation change between each cell and its eight neighbors and is measured in degrees. The slope captures, for example, the gravitational influence on surface water flow and retention capacity.

#### Euclidean Distance to Waterbody (EDTW)

The Euclidean distance to the next waterbody (EDTW) was computed as the straight-line distance from each cell to the nearest water cell in the OSM water raster. This metric complements HAND by incorporating horizontal proximity to water bodies, which significantly influences flood susceptibility.

## Installation

### Using pip

```bash
pip install hydro-topo-features
```

### From source

```bash
# Clone the repository
cd hydro-topo-features

# Create a conda environment
conda create -n hydro_topo_env python=3.11
conda activate hydro_topo_env

# Install dependencies and package
pip install -e .
```

## Quick Start

```python
from hydro_topo_features.pipeline import run_pipeline

outputs = run_pipeline(
    site_id="my_area",
    aoi_path="path/to/area_of_interest.shp",
    dem_tile_folder_path="path/to/dem_tiles/", # (.tif)
    output_path="outputs",
    create_static_maps=True,
    create_interactive_map=True
)

# Print output paths
for key, path in outputs.items():
    print(f"{key}: {path}")
```

## Command Line Usage

```bash
python test_hydro_topo.py --site-id my_area \
                         --aoi-path path/to/area_of_interest.shp \
                         --dem-dir path/to/dem_tiles/ \
                         --output-dir outputs \
                         --static-maps \
                         --interactive-map
```

## Documentation

For comprehensive documentation, please visit:
[https://hydro-topo-features.readthedocs.io/](https://hydro-topo-features.readthedocs.io/)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Citation

If you use this package in your research, please cite:

```
@software{hydro_topo_features,
  author = {Hosch, Paul},
  title = {Hydro-Topo Features: A Python package for extracting hydro-topographic features},
  year = {2025},
  url = {https://github.com/paulhosch/hydro-topo-features}
}
```

## Future Improvements

### Slope Calculation

The current implementation calculates slope using Horn's method, which offers a good balance between computational efficiency and accuracy. However, this approach has some limitations:

- **Smoothing Effect**: The algorithm has an inherent smoothing effect that can underestimate slope in areas with high terrain variability.
- **Directional Bias**: Horn's gradient estimation may miss subtle directional variations, particularly in terrains with complex anisotropic features.

Future improvements could include:

- richdem, WhiteboxTools for more advanced slope calculations.

### EDTW Computation

The current Euclidean Distance to Waterbody (EDTW) implementation calculates the straight-line distance to the nearest water cell, which doesn't account for flow dynamics:

- **Flow Direction Ignorance**: The straight-line approach doesn't consider that water actually moves along flow paths governed by terrain, not in straight lines.
- **Terrain Barriers**: Terrain barriers (like ridges) between a point and water body are not considered in a simple Euclidean calculation.

Potential enhancements could include:

- Implementing a flow-path distance calculation that traces along the actual flow direction network

## References

### Scientific Publications

Barnes, R., Lehman, C., & Mulla, D. (2014). Priority-flood: An optimal depression-filling and watershed-labeling algorithm for digital elevation models. _Computers & Geosciences, 62_, 117-127.

Barnes, R., Lehman, C., & Mulla, D. (2015). An efficient assignment of drainage direction over flat surfaces in raster digital elevation models. _Computers & Geosciences, 77_, 138-148.

Chen, L., Gong, G., Li, X., & Jiang, C. (2024). Optimizing threshold selection for river network extraction from high-resolution DEMs. _Journal of Hydrology, 628_, 130308.

ESA. (2021). Copernicus Digital Elevation Model. European Space Agency. https://spacedata.copernicus.eu/collections/copernicus-digital-elevation-model

O'Callaghan, J. F., & Mark, D. M. (1984). The extraction of drainage networks from digital elevation data. _Computer Vision, Graphics, and Image Processing, 28(3)_, 323-344.

OpenStreetMap. (2023). OpenStreetMap Data. https://www.openstreetmap.org

Rennó, C. D., Nobre, A. D., Cuartas, L. A., Soares, J. V., Hodnett, M. G., Tomasella, J., & Waterloo, M. J. (2008). HAND, a new terrain descriptor using SRTM-DEM: Mapping terra-firme rainforest environments in Amazonia. _Remote Sensing of Environment, 112(9)_, 3469-3481.

Uhe, P., Pickering, M., Smith, A., Smith, N., Schumann, G., Sampson, C., Wing, O., & Bates, P. (2025). FathomDEM: A global bare-earth digital elevation model. [Publication in preparation]

Yamazaki, D., Ikeshima, D., Sosa, J., Bates, P. D., Allen, G. H., & Pavelsky, T. M. (2019). MERIT Hydro: A high-resolution global hydrography map based on latest topography dataset. _Water Resources Research, 55(6)_, 5053-5073.

### Software and Tools

Bartos, M. (2018). PySheds: Simple and efficient hydrologic terrain analysis in Python. GitHub Repository. https://github.com/mdbartos/pysheds
