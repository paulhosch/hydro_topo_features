# Examples for Hydro-Topological Features Extraction

This directory contains example scripts demonstrating how to use the `hydro_topo_features` package for various tasks.

## Available Examples

1. **run_full_pipeline.py** - Demonstrates running the complete pipeline for extracting hydro-topological features from DEM and OpenStreetMap data.

2. **static_maps.py** - Shows how to create static maps from processed data, focusing on visualization customization.

3. **interactive_map.py** - Creates interactive web maps from processed data with layer controls and customizable styling.

4. **jupyter_notebook_usage.ipynb** - A Jupyter notebook providing a comprehensive walkthrough of using the package in an interactive environment.

## Prerequisites

Before running these examples, make sure you have:

1. Installed the `hydro_topo_features` package and its dependencies
2. Downloaded the necessary test data (DEM tiles and AOI shapefiles)

## Test Data Structure

The examples assume the following data structure:

```
test_data/
├── aoi/
│   └── danube/
│       └── EMSR728_AOI04_DEL_PRODUCT_areaOfInterestA_v1.shp (and related files)
├── dem_tiles/
│   └── danube/
│       ├── n48e009.tif
│       ├── n48e010.tif
│       └── n48e011.tif
```

## Running the Examples

### Full Pipeline

Run the complete pipeline to extract all hydro-topological features and create visualizations:

```bash
python examples/run_full_pipeline.py
```

This creates a full directory structure with interim, processed, and figures subdirectories.

### Static Maps

Create customized static maps from previously processed data:

```bash
python examples/static_maps.py
```

### Interactive Map

Create an interactive web map with layer controls from previously processed data:

```bash
python examples/interactive_map.py
```

### Jupyter Notebook

Open and run the Jupyter notebook for an interactive walkthrough:

```bash
jupyter notebook examples/jupyter_notebook_usage.ipynb
```

## Output Structure

The examples generate outputs in the following structure:

```
data/output/
└── EMSR728_AOI04/
    ├── interim/
    │   ├── osm_water_raster.tif
    │   ├── osm_water_vector.gpkg
    │   └── raw_dem.tif
    ├── processed/
    │   ├── edtw.tif
    │   ├── hand.tif
    │   └── slope.tif
    └── figures/
        ├── static/
        │   ├── edtw.png
        │   ├── hand.png
        │   ├── osm_water.png
        │   ├── raw_dem.png
        │   └── slope.png
        └── interactive/
            └── EMSR728_AOI04_interactive_map.html
```

## Customization

Each example includes parameters that you can modify to customize the analysis and visualization. Look for comments in the code indicating customization points.
