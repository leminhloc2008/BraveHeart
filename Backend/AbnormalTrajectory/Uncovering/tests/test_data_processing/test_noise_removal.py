"""Test script for validating the noise removal process with real PLT files."""

import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from AbnormalTrajectory.Uncovering.data_processing.data_loader import TrajectoryLoader
from AbnormalTrajectory.Uncovering.data_processing.noise_removal import NoiseRemover
from AbnormalTrajectory.Uncovering.data_processing.utils import calculate_speed

def analyze_speeds(df: pd.DataFrame) -> tuple:
    """
    Calculate speed statistics for a trajectory.
    
    Args:
        df: DataFrame containing trajectory data
        
    Returns:
        Tuple of (speeds, max_speed, avg_speed)
    """
    speeds = []
    for i in range(len(df) - 1):
        speed = calculate_speed(
            df.iloc[i]['latitude'],
            df.iloc[i]['longitude'],
            df.iloc[i+1]['latitude'],
            df.iloc[i+1]['longitude'],
            df.iloc[i]['timestamp'],
            df.iloc[i+1]['timestamp']
        )
        speeds.append(speed)
    
    speeds = np.array(speeds)
    return speeds, np.max(speeds), np.mean(speeds)

def plot_trajectory_comparison(original_df: pd.DataFrame, 
                            cleaned_df: pd.DataFrame,
                            title: str = "Trajectory Comparison") -> None:
    """
    Plot original and cleaned trajectories side by side.
    
    Args:
        original_df: Original trajectory DataFrame
        cleaned_df: Cleaned trajectory DataFrame
        title: Plot title
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
    
    # Plot original trajectory
    ax1.plot(original_df['longitude'], original_df['latitude'], 'b.-', alpha=0.5)
    ax1.set_title("Original Trajectory")
    ax1.set_xlabel("Longitude")
    ax1.set_ylabel("Latitude")
    ax1.grid(True)
    
    # Plot cleaned trajectory
    ax2.plot(cleaned_df['longitude'], cleaned_df['latitude'], 'g.-', alpha=0.5)
    ax2.set_title("Cleaned Trajectory")
    ax2.set_xlabel("Longitude")
    ax2.set_ylabel("Latitude")
    ax2.grid(True)
    
    plt.suptitle(title)
    plt.tight_layout()
    plt.show()

def plot_speed_distribution(speeds: np.ndarray, title: str) -> None:
    """
    Plot speed distribution histogram.
    
    Args:
        speeds: Array of speeds
        title: Plot title
    """
    plt.figure(figsize=(10, 6))
    plt.hist(speeds, bins=50, alpha=0.7)
    plt.axvline(np.mean(speeds), color='r', linestyle='--', label='Mean Speed')
    plt.title(title)
    plt.xlabel("Speed (m/s)")
    plt.ylabel("Frequency")
    plt.legend()
    plt.grid(True)
    plt.show()

def test_noise_removal(file_path: Path) -> None:
    """
    Test noise removal on a single trajectory file.
    
    Args:
        file_path: Path to PLT file
    """
    print(f"\nProcessing file: {file_path.name}")
    
    # Load and clean trajectory
    df = TrajectoryLoader.load_plt_file(file_path)
    noise_remover = NoiseRemover()
    cleaned_df = noise_remover.clean_trajectory(df)
    
    # Calculate statistics
    original_speeds, original_max, original_avg = analyze_speeds(df)
    cleaned_speeds, cleaned_max, cleaned_avg = analyze_speeds(cleaned_df)
    
    # Print statistics
    print("\nTrajectory Statistics:")
    print(f"Original points: {len(df)}")
    print(f"Cleaned points: {len(cleaned_df)}")
    print(f"Points removed: {len(df) - len(cleaned_df)} ({(len(df) - len(cleaned_df))/len(df)*100:.1f}%)")
    print(f"\nSpeed Statistics (m/s):")
    print(f"Original - Max: {original_max:.2f}, Avg: {original_avg:.2f}")
    print(f"Cleaned  - Max: {cleaned_max:.2f}, Avg: {cleaned_avg:.2f}")
    
    # Plot results
    plot_trajectory_comparison(df, cleaned_df, f"Trajectory Comparison - {file_path.stem}")
    plot_speed_distribution(original_speeds, "Original Speed Distribution")
    plot_speed_distribution(cleaned_speeds, "Cleaned Speed Distribution")

def main():
    """Main function to run the noise removal test."""
    # Replace with your actual data directory path
    data_directory = "Backend/Dataset/GeolifeTrajectories/GeolifeTrajectories/Data/000/Trajectory/"
    directory = Path(data_directory)
    
    print("Testing Noise Removal")
    print("=" * 50)
    
    # Process a sample of files
    plt_files = list(directory.glob("*.plt"))
    sample_size = min(3, len(plt_files))  # Process 3 files as a sample
    
    for file_path in plt_files[:sample_size]:
        test_noise_removal(file_path)

if __name__ == "__main__":
    main()