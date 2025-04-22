import os
import sys
import datetime

# Add the project root directory to the path
sys.path.insert(0, os.path.abspath('..'))

# Get package information
from hydro_topo_features import __version__, __author__, __project_name__

# Project information
project = 'Hydro-Topo Features'
copyright = f'{datetime.datetime.now().year}, {__author__}'
author = __author__
version = __version__
release = __version__

# General configuration
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.mathjax',
    'sphinx.ext.intersphinx',
    'sphinx_rtd_theme',
    'sphinx.ext.autosummary',
    'sphinx.ext.coverage',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# HTML output
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_title = f"{project} {version}"
html_logo = None  # Add path to logo if available

# Extension settings
autodoc_member_order = 'alphabetical'
autoclass_content = 'both'
add_module_names = False

# Intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable', None),
    'rasterio': ('https://rasterio.readthedocs.io/en/latest', None),
    'geopandas': ('https://geopandas.org/en/stable', None),
}

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = True
napoleon_type_aliases = None
napoleon_attr_annotations = True 