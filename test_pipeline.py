#!/usr/bin/env python
import os
import hydro_topo_features
from hydro_topo_features.config import Config
from hydro_topo_features.pipeline import Pipeline

def main():
    """Test the hydro-topo feature extraction pipeline."""
    print("Starting hydro-topo feature extraction test...")
    
    # Load default configuration
    config = Config()
    
    # Set input paths for test data
    config.paths.dem = os.path.join('data', 'dem')
    config.paths.aoi = os.path.join('data', 'aoi', 'aoi.shp')
    
    # Create pipeline with our configuration
    pipeline = Pipeline(config)
    
    # Run the pipeline
    pipeline.run()
    
    print("Pipeline completed successfully!")

if __name__ == "__main__":
    main() 