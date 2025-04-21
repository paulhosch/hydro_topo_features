from setuptools import setup, find_packages

setup(
    name="hydro_topo_features",
    version="0.1.0",
    description="Extract hydro-topological features from DEM and OSM data",
    author="Paul Hosch",
    author_email="paul.hosch@outlook.com",
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
    python_requires=">=3.11",
) 