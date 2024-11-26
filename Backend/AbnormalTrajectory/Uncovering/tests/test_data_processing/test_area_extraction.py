"""Test script for area extraction functionality with real PLT files."""

import sys
sys.path.append(r"C:\Users\Admin\BraveHeart\Backend")

# Verify that the path has been added
print(sys.path)


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from AbnormalTrajectory.Uncovering.data_processing.data_loader import TrajectoryLoader
from AbnormalTrajectory.Uncovering.data_processing.area_extraction import AreaExtractor
import time

def visualize_area_filtering(df: pd.DataFrame, 
                           area_extractor: AreaExtractor,
                           title: str = "Area Filtering Results") -> None:
    """
    Visualize original trajectory and points within area of interest.
    
    Args:
        df: Original trajectory DataFrame
        area_extractor: Configured AreaExtractor instance
        title: Plot title
    """
    # Get filtered points
    filtered_df = area_extractor.filter_points(df)
    
    # Get polygon points for plotting
    polygon = area_extractor.polygon
    
    

    # Create plot
    plt.figure(figsize=(15, 10))
    
    # Plot original trajectory
    plt.plot(df['longitude'], df['latitude'], 'b.', alpha=0.3, label='Original Points')
    
    # Plot filtered points
    plt.plot(filtered_df['longitude'], filtered_df['latitude'], 'r.', 
             alpha=0.6, label='Points in Area')
    
    # Plot polygon
    plt.plot(polygon[:, 1], polygon[:, 0], 'g-', linewidth=2, 
             label='Area of Interest')
    
    # Plot centroid
    centroid = area_extractor.get_centroid()
    plt.plot(centroid[1], centroid[0], 'k*', markersize=15, 
             label='Area Centroid')
    
    plt.title(title)
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.legend()
    plt.grid(True)
    plt.draw()

    output_path = f"plot_{title.replace(' ', '_')}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.show()
    time.sleep(2000000000)
    
    #plt.pause(0.001)  # Small pause to render the plot
    #input("Press Enter to continue...")  # Wait for user input before closing
    #plt.close()
    
    # Print statistics
    print(f"\nFiltering Statistics:")
    print(f"Original points: {len(df)}")
    print(f"Points in area: {len(filtered_df)}")
    print(f"Points filtered: {len(df) - len(filtered_df)}")
    print(f"Percentage in area: {len(filtered_df)/len(df)*100:.1f}%")
    
    # Print area information
    area = area_extractor.estimate_area()
    bbox = area_extractor.get_bounding_box()
    print(f"\nArea Information:")
    print(f"Estimated area: {area/1000000:.2f} km²")
    print(f"Bounding box: {bbox}")

def test_area_extraction(file_path: Path, polygon_points: list) -> None:
    """
    Test area extraction on a single trajectory file.
    
    Args:
        file_path: Path to PLT file
        polygon_points: List of (lat, lon) tuples defining area of interest
    """
    print(f"\nProcessing file: {file_path.name}")
    
    try:
        # Load trajectory
        df = TrajectoryLoader.load_plt_file(file_path)
        
        # Create area extractor
        area_extractor = AreaExtractor(polygon_points)
        
        # Visualize results
        visualize_area_filtering(df, area_extractor, 
                               f"Area Filtering - {file_path.stem}")
        
    except Exception as e:
        print(f"Error processing file: {e}")

def main():
    """Main function to run the area extraction test."""
    # Replace with your actual data directory path
    data_directory = "Backend/Dataset/GeolifeTrajectories/GeolifeTrajectories/Data/000/Trajectory/"
    
    # Define area of interest (replace with your actual area)
    # Example polygon (approximately rectangular area)
    polygon_points = [
        (39.9, 116.3),  # Southwest corner
        (39.9, 116.4),  # Southeast corner
        (40.0, 116.4),  # Northeast corner
        (40.0, 116.3),  # Northwest corner
        (39.9, 116.3)   # Close the polygon
    ]
    
    print("Testing Area Extraction")
    print("=" * 50)
    
    # Process a sample of files
    directory = Path(data_directory)
    plt_files = list(directory.glob("*.plt"))
    sample_size = min(3, len(plt_files))
    
    for file_path in plt_files[:sample_size]:
        test_area_extraction(file_path, polygon_points)

if __name__ == "__main__":
    print("Hello")
    main()
    
    

