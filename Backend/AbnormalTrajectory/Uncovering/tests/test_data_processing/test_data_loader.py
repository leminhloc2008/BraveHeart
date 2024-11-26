"""Test script for validating the trajectory data loader with real PLT files."""

'''
set PYTHONPATH=%PYTHONPATH%;C:\Users\Admin\BraveHeart\Backend
echo %PYTHONPATH%
set PYTHONPATH=
'''

import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from AbnormalTrajectory.Uncovering.data_processing.data_loader import TrajectoryLoader

def analyze_trajectory_file(file_path: Path) -> None:
    """
    Analyze a single trajectory file and print its characteristics.
    
    Args:
        file_path: Path to the PLT file
    """
    print(f"\nAnalyzing file: {file_path.name}")
    try:
        df = TrajectoryLoader.load_plt_file(file_path)
        
        # Print basic statistics
        print(f"Number of points: {len(df)}")
        print(f"Time range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        print(f"Latitude range: {df['latitude'].min():.6f} to {df['latitude'].max():.6f}")
        print(f"Longitude range: {df['longitude'].min():.6f} to {df['longitude'].max():.6f}")
        
        # Check for missing or invalid values
        null_counts = df.isnull().sum()
        if null_counts.any():
            print("\nMissing values:")
            print(null_counts[null_counts > 0])
            
        return df
        
    except Exception as e:
        print(f"Error processing file: {e}")
        return None

def analyze_directory(directory_path: str) -> None:
    """
    Analyze all PLT files in the given directory and visualize sample trajectories.
    
    Args:
        directory_path: Path to directory containing PLT files
    """
    directory = Path(directory_path)
    if not directory.exists():
        print(f"Directory not found: {directory_path}")
        return
        
    plt_files = list(directory.glob("*.plt"))
    if not plt_files:
        print(f"No PLT files found in {directory_path}")
        return
        
    print(f"Found {len(plt_files)} PLT files")
    
    # Analyze first few files in detail
    sample_size = min(5, len(plt_files))
    sample_trajectories = {}
    
    for file_path in plt_files[:sample_size]:
        df = analyze_trajectory_file(file_path)
        if df is not None:
            sample_trajectories[file_path.stem] = df
    
    # Plot sample trajectories
    if sample_trajectories:
        plt.figure(figsize=(15, 10))
        for trajectory_id, df in sample_trajectories.items():
            plt.plot(df['longitude'], df['latitude'], label=trajectory_id, alpha=0.7)
        
        plt.title("Sample Trajectories")
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        plt.legend()
        plt.grid(True)
        plt.show()
        
        # Print overall statistics
        total_points = sum(len(df) for df in sample_trajectories.values())
        print(f"\nOverall Statistics (for {sample_size} sample trajectories):")
        print(f"Total points: {total_points}")
        print(f"Average points per trajectory: {total_points / sample_size:.1f}")

def main():
    """Main function to run the data loader test."""
    # Replace with your actual data directory path
    data_directory = "Backend/Dataset/GeolifeTrajectories/GeolifeTrajectories/Data/000/Trajectory/"
    
    print("Testing Trajectory Data Loader")
    print("=" * 50)
    
    analyze_directory(data_directory)

if __name__ == "__main__":
    main()