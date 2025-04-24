Getting Started
===============

This section will help you get up and running with the Hydro-Topo Features package.

.. toctree::
   :maxdepth: 2
   
   installation
   quick_start
   
Overview
-------

Hydro-Topo Features is a Python package for extracting hydro-topographic variables from Digital Elevation Models (DEMs) and OpenStreetMap (OSM) water data. The package is designed to be:

- **Easy to use**: Simple API with sensible defaults
- **Flexible**: Numerous options for customization
- **Efficient**: Optimized for processing large areas
- **Well-documented**: Comprehensive documentation and examples

The package extracts three key variables:

1. **Height Above Nearest Drainage (HAND)**: Vertical distance to the nearest drainage channel
2. **Euclidean Distance to Waterbody (EDTW)**: Straight-line distance to the nearest water body
3. **Terrain Slope**: Maximum rate of elevation change

Key Features
----------

- Automated DEM conditioning including stream burning, depression filling, and flat resolution
- Efficient computation of flow direction and accumulation
- Multiple algorithms for feature extraction
- Flexible visualization options including static and interactive maps
- Command-line interface for batch processing
- Integration with common GIS libraries and formats

Next Steps
---------

1. Start by following the :doc:`installation` instructions
2. Try the examples in the :doc:`quick_start` guide
3. Explore the detailed documentation in the :doc:`../usage/index` section
4. Check out real-world examples in the :doc:`../examples/index` section 