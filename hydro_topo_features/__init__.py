"""Hydro-topological features extraction package.

This package provides functionality for extracting hydro-topological features 
from Digital Elevation Models (DEM) and OpenStreetMap (OSM) water data.

Main modules:
- processing: Data processing and feature extraction
- visualization: Static and interactive visualization
- pipeline: Main pipeline for end-to-end processing
- config: Configuration settings

For detailed usage, see the README.md file.
"""

from . import config
from . import processing
from . import visualization
from .pipeline import run_pipeline

__version__ = '0.1.0'
__author__ = 'Paul Hosch'
__email__ = 'paul.hosch@outlook.com' 