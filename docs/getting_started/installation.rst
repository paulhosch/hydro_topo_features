Installation
============

This guide provides comprehensive instructions for installing the Hydro-Topo Features package on various platforms and environments.

Requirements
-----------

Hydro-Topo Features requires:

- Python 3.9 or higher
- GDAL >= 3.0.0
- NumPy >= 1.20.0
- rasterio >= 1.2.0
- PySheds >= 0.2.8
- geopandas >= 0.9.0
- matplotlib >= 3.4.0
- folium >= 0.12.0
- tqdm >= 4.60.0

Using pip
--------

The simplest way to install Hydro-Topo Features is via pip:

.. code-block:: bash

    pip install hydro-topo-features

This will install the package and all its dependencies.

Using conda
----------

If you use the Anaconda Python distribution, you can install Hydro-Topo Features using conda:

.. code-block:: bash

    # Create a new conda environment (recommended)
    conda create -n hydro_topo_env python=3.11
    conda activate hydro_topo_env
    
    # Install dependencies that work better via conda
    conda install -c conda-forge gdal rasterio geopandas
    
    # Install Hydro-Topo Features
    pip install hydro-topo-features

Installing from Source
--------------------

For the latest development version, you can install directly from the GitHub repository:

.. code-block:: bash

    # Clone the repository
    git clone https://github.com/paulhosch/hydro-topo-features.git
    cd hydro-topo-features
    
    # Create a conda environment (recommended)
    conda create -n hydro_topo_env python=3.11
    conda activate hydro_topo_env
    
    # Install dependencies
    pip install -e .

Platform-Specific Instructions
----------------------------

Windows
^^^^^^

Installing GDAL and other geospatial libraries on Windows can sometimes be challenging. We recommend using Anaconda:

.. code-block:: bash

    conda create -n hydro_topo_env python=3.11
    conda activate hydro_topo_env
    conda install -c conda-forge gdal rasterio geopandas
    pip install hydro-topo-features

macOS
^^^^

On macOS, you can use Homebrew to install GDAL before installing the package:

.. code-block:: bash

    # Install GDAL with Homebrew
    brew install gdal
    
    # Then install the package
    pip install hydro-topo-features

Linux
^^^^

On Ubuntu/Debian:

.. code-block:: bash

    # Install GDAL dependencies
    sudo apt-get update
    sudo apt-get install gdal-bin libgdal-dev
    
    # Install the package
    pip install hydro-topo-features

Docker
-----

For a containerized environment, you can use our Docker image:

.. code-block:: bash

    # Pull the Docker image
    docker pull paulhosch/hydro-topo-features:latest
    
    # Run a container with mounted volumes for data
    docker run -it --rm \
      -v /path/to/your/data:/data \
      -v /path/to/your/outputs:/outputs \
      paulhosch/hydro-topo-features:latest

Verifying Installation
--------------------

To verify that Hydro-Topo Features is installed correctly, run the following Python code:

.. code-block:: python

    from hydro_topo_features import __version__
    
    print(f"Hydro-Topo Features version: {__version__}")
    
    # Try importing key modules
    from hydro_topo_features import pipeline
    from hydro_topo_features import dem_conditioning
    from hydro_topo_features import feature_extraction
    
    print("All modules imported successfully!")

Troubleshooting
-------------

Common Issues
^^^^^^^^^^^

1. **GDAL installation errors**:
   
   If you encounter issues with GDAL, try installing it separately before installing Hydro-Topo Features:
   
   .. code-block:: bash
   
       conda install -c conda-forge gdal
   
2. **ImportError: No module named 'osgeo'**:
   
   This indicates GDAL is not installed correctly. Try:
   
   .. code-block:: bash
   
       pip install --upgrade GDAL==$(gdal-config --version)
   
3. **Memory errors during processing**:
   
   For large areas, you may need more memory. Try processing smaller areas or use a machine with more RAM.

Getting Help
^^^^^^^^^^

If you encounter persistent installation issues:

1. Check the GitHub issues page: https://github.com/paulhosch/hydro-topo-features/issues
2. Create a new issue with details about your environment and the error messages
3. Contact the maintainers via GitHub 