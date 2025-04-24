Hydro-Topo Features Documentation
===============================

A Python package for the automated extraction of hydro-topographic features from Digital Elevation Models (DEMs) and OpenStreetMap (OSM) water data. These features are critical for understanding flood susceptibility and analyzing terrain characteristics.

.. image:: https://img.shields.io/pypi/v/hydro-topo-features.svg
    :target: https://pypi.org/project/hydro-topo-features/
    :alt: PyPI Version

.. image:: https://readthedocs.org/projects/hydro-topo-features/badge/?version=latest
    :target: https://hydro-topo-features.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
    :target: https://opensource.org/licenses/MIT
    :alt: License: MIT

Overview
--------

This package implements a quasi-global, automated workflow for the extraction of three key hydro-topographic variables:

1. **Height Above Nearest Drainage (HAND)**: Vertical distance to the nearest drainage channel
2. **Euclidean Distance to Waterbody (EDTW)**: Straight-line distance to the nearest water body
3. **Terrain Slope**: Maximum rate of elevation change

The extracted features provide critical contextual information for flood susceptibility analysis, hydrological modeling, and terrain characterization.

Key Features
-----------

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

Table of Contents
----------------

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   getting_started/index
   usage/index
   methodology
   examples/index
   api/index
   references
   
Technical Background
-------------------

.. figure:: images/pipeline.png
   :alt: Hydro-Topo Features Processing Pipeline
   :align: center
   :width: 100%
   
   *Quasi Global and Automatic Pipeline To Compute the Hydro Topographic Descriptors: (X1) HAND, (X2) Slope and (X3) Euclidean Distance To Water, using (A1) FathomDEM and (A2) OpenStreetMap Water as Input Data. A (B) Conditioned DEM is computed to ensure drainage and an accurate (C) Flow Direction approximation.*

Terrain and hydrological characteristics significantly influence the flood susceptibility of a location. For example, low-lying areas near water bodies are inherently more prone to flooding than elevated and steep regions. Digital Elevation Models (DEMs) and hydrological network data provide critical contextual information enabling classifiers to establish associations between physiographic conditions and flooding potential.

This package implements an automated workflow for the extraction of three key hydro-topographic variables:

1. **Height Above Nearest Drainage (HAND)**
2. **Euclidean Distance to Waterbody (EDTW)**
3. **Terrain Slope**

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search` 