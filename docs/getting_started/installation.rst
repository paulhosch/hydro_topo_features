Installation
============

There are multiple ways to install the Hydro-Topo Features package. Choose the option that works best for your workflow.

Installing from PyPI
-------------------

The simplest way to install the package is via pip:

.. code-block:: bash

   pip install hydro-topo-features

This will install the package and all its dependencies.

Installing from Source
---------------------

For the latest development version or to contribute to the package, you can install from source:

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/yourusername/hydro-topo-features.git
   cd hydro-topo-features
   
   # Create a conda environment
   conda create -n hydro_topo_env python=3.11
   conda activate hydro_topo_env
   
   # Install package in development mode
   pip install -e .

Dependencies
-----------

The package has the following dependencies:

- Python >= 3.11
- numpy >= 1.26
- rasterio
- geopandas
- pysheds
- matplotlib
- folium
- cartopy
- geemap
- osmnx
- scipy
- tqdm

These will be automatically installed when using pip. If you prefer to use conda:

.. code-block:: bash

   conda install -c conda-forge numpy rasterio geopandas pysheds matplotlib folium cartopy geemap osmnx scipy tqdm

Verifying Installation
--------------------

You can verify that the installation was successful by running:

.. code-block:: python

   import hydro_topo_features
   print(hydro_topo_features.__version__)

This should print the version number of the installed package. 