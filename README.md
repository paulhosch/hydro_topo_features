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
conda create -n hydro_topo_3 python=3.11
conda activate hydro_topo_3
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

1. Prepare your data:

   - Place your DEM tiles in `example_data/dem_tiles/danube/`
   - Place your AOI shapefile in `example_data/aoi/danube/`

2. Run the test pipeline:

```bash
python test_pipeline.py
```

The script will:

- Merge and condition DEM tiles
- Extract water features from OSM
- Compute HAND, slope, and EDTW
- Create static and interactive visualizations

## Output

Results are saved in the `example_output_dir` directory:

```
example_output_dir/
└── SITE_ID/
    ├── interim/
    │   ├── raw_dem.tif
    │   └── osm_water_raster.tif
    ├── processed/
    │   ├── osm_hand.tif
    │   ├── slope.tif
    │   └── edtw.tif
    └── figures/
        ├── static/
        │   └── *.svg
        └── interactive/
            └── interactive_map.html
```

## Configuration

Adjust parameters in `hydro_topo_features/config.py`:

- Processing parameters (e.g., burn depth)
- Visualization settings
- OSM water feature tags
- Output paths and formats

## License

MIT License
