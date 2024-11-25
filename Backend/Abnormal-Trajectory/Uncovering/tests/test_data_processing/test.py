"""Simple testing script for data processing."""

from pathlib import Path
from Uncovering.data_processing.noise_removal import NoiseRemover
from Uncovering.data_processing.data_loader import TrajectoryLoader
import pandas as pd

def test_data_processing(data_dir: str):
    """
    Test data loading and cleaning on actual PLT files.
    
    Args:
        data_dir: Path to directory containing PLT files
    """
    print(f"Testing data processing on files in {data_dir}")
    
    # Initialize components
    loader = TrajectoryLoader()
    cleaner = NoiseRemover()
    
    # Get all PLT files
    plt_files = list(Path(data_dir).glob("*.plt"))
    print(f"Found {len(plt_files)} PLT files")
    
    # Process each file
    for plt_file in plt_files:
        print(f"\nProcessing {plt_file.name}")
        
        # Load data
        try:
            df = loader.load_plt_file(plt_file)
            print(f"- Loaded {len(df)} points")
            
            # Basic data validation
            print(f"- Latitude range: {df['latitude'].min():.6f} to {df['latitude'].max():.6f}")
            print(f"- Longitude range: {df['longitude'].min():.6f} to {df['longitude'].max():.6f}")
            print(f"- Time range: {df['timestamp'].min()} to {df['timestamp'].max()}")
            
            # Clean data
            cleaned_df = cleaner.clean_trajectory(df)
            points_removed = len(df) - len(cleaned_df)
            percent_removed = (points_removed / len(df)) * 100
            print(f"- Removed {points_removed} points ({percent_removed:.1f}%)")
            
            # Validate cleaning
            if len(cleaned_df) == 0:
                print("WARNING: All points were removed!")
            elif len(cleaned_df) < 0.5 * len(df):
                print("WARNING: More than 50% of points were removed!")
                
        except Exception as e:
            print(f"ERROR processing {plt_file.name}: {str(e)}")
            continue

if __name__ == "__main__":
    # Replace with your actual data directory
    DATA_DIR = "Backend/Dataset/Geolife Trajectories 1.3/Geolife Trajectories 1.3/Data/000/Trajectory/20081027115449.plt"
    test_data_processing(DATA_DIR)