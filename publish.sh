#!/bin/bash
# Script to build and publish the hydro-topo-features package to PyPI

# Ensure we have the latest tools
python -m pip install --upgrade pip
pip install --upgrade build twine

# Clean up any previous builds
rm -rf dist/ build/ *.egg-info/

# Build the package
python -m build

# Check the distribution
twine check dist/*

# Upload to TestPyPI first (uncomment to use)
# twine upload --repository testpypi dist/*

# Upload to PyPI (will prompt for username and password)
echo "Ready to upload to PyPI"
echo "Press Enter to continue or Ctrl+C to abort"
read

# Upload to PyPI
twine upload dist/*

echo "Package published to PyPI!" 