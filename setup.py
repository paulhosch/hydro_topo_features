from setuptools import setup, find_packages
import os

# Read the contents of the README file
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="hydro-topo-features",
    version="0.1.4",
    description="Extract hydro-topographic features from DEM and OSM data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Paul Hosch",
    author_email="paul.hosch@rwth-aachen.de",
    url="https://github.com/paulhosch/hydro_topo_features",
    project_urls={
        "Documentation": "https://hydro-topo-features.readthedocs.io/",
        "Source Code": "https://github.com/paulhosch/hydro_topo_features",
        "Bug Tracker": "https://github.com/paulhosch/hydro_topo_features/issues",
    },
    packages=find_packages(),
    install_requires=[
        "numpy>=1.26.0",
        "rasterio>=1.3.8",
        "geopandas>=0.14.0",
        "pysheds>=0.3.3",
        "matplotlib>=3.7.0",
        "folium>=0.14.0",
        "cartopy>=0.22.0",
        "geemap>=0.28.0",
        "osmnx>=1.5.0",
        "scipy>=1.10.0",
        "tqdm>=4.64.0",
        "geopy>=2.4.0"
    ],
    extras_require={
        "docs": [
            "sphinx>=4.0.0",
            "sphinx_rtd_theme>=1.0.0",
            "sphinx-autodoc-typehints",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Scientific/Engineering :: Hydrology",
    ],
    keywords="dem, hydrology, gis, osm, hand, flood mapping, terrain analysis",
    python_requires=">=3.11",
) 