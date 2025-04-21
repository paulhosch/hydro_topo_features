# Hydro-Topological Features Extraction

A Python package for extracting hydro-topological features from Digital Elevation Models (DEM) and OpenStreetMap (OSM) water data.

## Features

- DEM conditioning with stream burning
- Height Above Nearest Drainage (HAND) computation
- Slope calculation
- Euclidean Distance to Water (EDTW) computation
- Static and interactive visualization of results
- OpenStreetMap water feature extraction

## Installation

1. Create a conda environment:

```bash
conda create -n hydro_topo_env python=3.11
conda activate hydro_topo_env
```

2. Install dependencies:

```bash
conda install -c conda-forge numpy=1.26 rasterio geopandas pysheds matplotlib folium cartopy geemap osmnx scipy tqdm
```

3. Install the package in development mode:

```bash
pip install -e .
```

## Usage

### Command Line Interface

Use the provided command-line script to run the pipeline:

```bash
python test_hydro_topo.py --site-id danube \
                        --aoi-path /path/to/aoi.shp \
                        --dem-dir /path/to/dem/tiles \
                        --output-dir outputs \
                        --static-maps \
                        --interactive-map
```

Arguments:

- `--site-id`: Unique identifier for the site
- `--aoi-path`: Path to AOI shapefile
- `--dem-dir`: Path to directory containing DEM tiles
- `--output-dir`: Path for output files (default: 'outputs')
- `--static-maps`: Create static maps
- `--interactive-map`: Create interactive map

### Python API

You can also use the package programmatically in your Python code:

```python
from hydro_topo_features.pipeline import run_pipeline

# Run the complete pipeline
outputs = run_pipeline(
    site_id="danube",
    aoi_path="/path/to/aoi.shp",
    dem_tile_folder_path="/path/to/dem/tiles",
    output_path="outputs",
    create_static_maps=True,
    create_interactive_map=True
)

# Print output paths
for key, path in outputs.items():
    print(f"{key}: {path}")
```

## Output Structure

Results are saved in the output directory with the following structure:

```
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
```

## Configuration

Adjust parameters in `hydro_topo_features/config.py`:

### Directory Structure

```python
DIRECTORY_STRUCTURE = {
    "RAW": "raw",         # Original data without processing
    "INTERIM": "interim", # Intermediate processing results
    "PROCESSED": "processed", # Final data products
    "FIGURES": "figures", # Visualizations
    "STATIC": "static",   # Static visualizations
    "INTERACTIVE": "interactive" # Interactive visualizations
}
```

### Processing Parameters

```python
DEM_PROCESSING = {
    "BURN_DEPTH": 20,  # meters to burn streams into DEM
    "NODATA_VALUE": 0, # Value for no data
    "DEFAULT_CRS": "EPSG:4326", # WGS84
    "RASTERIZE_RESOLUTION": 30, # meters
}
```

### Feature Computation Parameters

```python
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
```

### Visualization Settings

```python
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
    # ... other features
}
```

## Package Structure

The package is organized into several modules:

- `hydro_topo_features/processing/`: Data processing and feature extraction

  - `prepare_data.py`: Prepares input data (merges DEM tiles, extracts OSM water)
  - `burn_dem.py`: Burns streams into the DEM
  - `derive_products.py`: Computes HAND, slope, and EDTW

- `hydro_topo_features/visualization/`: Visualization functions

  - `static.py`: Creates static maps
  - `interactive.py`: Creates interactive maps

- `hydro_topo_features/pipeline.py`: Main pipeline for end-to-end processing
- `hydro_topo_features/config.py`: Configuration settings

## License

MIT License
