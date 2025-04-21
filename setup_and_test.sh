#!/bin/bash

# Exit on error
set -e

echo "Creating conda environment..."
conda env create -f environment.yml

echo "Activating environment..."
conda activate hydro_topo_2

echo "Installing package in development mode..."
pip install -e .

echo "Running test pipeline..."
python test_pipeline.py

echo "Done! Check the example_output_dir folder for results." 