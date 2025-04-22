from setuptools import setup, find_packages
import os

# Read the contents of the README file
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="hydro-topo-features",
    version="0.1.0",
    description="Extract hydro-topographic features from DEM and OSM data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Paul Hosch",
    author_email="paul.hosch@rwth-aachen.de",
    url="https://github.com/yourusername/hydro-topo-features",
    project_urls={
        "Documentation": "https://hydro-topo-features.readthedocs.io/",
        "Source Code": "https://github.com/yourusername/hydro-topo-features",
        "Bug Tracker": "https://github.com/yourusername/hydro-topo-features/issues",
    },
    packages=find_packages(),
    install_requires=[
        "numpy>=1.26",
        "rasterio",
        "geopandas",
        "pysheds",
        "matplotlib",
        "folium",
        "cartopy",
        "geemap",
        "osmnx",
        "scipy",
        "tqdm"
    ],
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