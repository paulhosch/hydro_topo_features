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
  - Stream burning (lowering the DEM by 20m along water features)
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

## Installation

### Using pip

```bash
pip install hydro-topo-features
```

### From source

```bash
# Clone the repository
git clone https://github.com/yourusername/hydro-topo-features.git
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
    dem_tile_folder_path="path/to/dem_tiles/",
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

## Workflow Details

1. **DEM Conditioning**

   - Stream burning with a constant depth of 20m along OSM-derived water features
   - Pit filling to remove single-cell depressions
   - Depression filling using the Priority-Flood algorithm
   - Resolving flat areas by creating artificial drainage gradients

2. **Flow Direction Calculation**

   - Uses the deterministic D8 method for flow direction computation

3. **Feature Extraction**

   - HAND: Traces flow paths downstream to calculate elevation difference
   - Slope: Computes maximum rate of elevation change in degrees
   - EDTW: Calculates Euclidean distance to nearest water cell

4. **Visualization**
   - Creates static maps with proper scaling and colormaps
   - Generates interactive web maps for data exploration

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
  year = {2023},
  url = {https://github.com/yourusername/hydro-topo-features}
}
```
