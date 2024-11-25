"""Module for loading and parsing PLT trajectory files."""

import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path
from .constants import (
    HEADER_LINES,
    LATITUDE_IDX,
    LONGITUDE_IDX,
    ALTITUDE_IDX,
    DATE_NUM_IDX,
    DATE_STR_IDX,
    TIME_STR_IDX,
    INVALID_ALTITUDE
)
from .utils import parse_datetime

class TrajectoryLoader:
    """Class for loading and parsing trajectory data from PLT files."""
    
    @staticmethod
    def load_plt_file(file_path: Path) -> pd.DataFrame:
        """
        Load a PLT file and return its contents as a pandas DataFrame.
        
        Args:
            file_path: Path to the PLT file
            
        Returns:
            DataFrame containing the trajectory data with columns:
            [latitude, longitude, altitude, timestamp, original_date, original_time]
        """
        # Skip header lines and read data
        data = []
        with open(file_path, 'r') as f:
            # Skip header lines
            for _ in range(HEADER_LINES):
                next(f)
                
            # Read data lines
            for line in f:
                fields = line.strip().split(',')
                if len(fields) != 7:  # Verify line format
                    continue
                    
                try:
                    lat = float(fields[LATITUDE_IDX])
                    lon = float(fields[LONGITUDE_IDX])
                    alt = float(fields[ALTITUDE_IDX])
                    date_str = fields[DATE_STR_IDX]
                    time_str = fields[TIME_STR_IDX]
                    
                    # Parse timestamp
                    timestamp = parse_datetime(date_str, time_str)
                    
                    data.append({
                        'latitude': lat,
                        'longitude': lon,
                        'altitude': alt if alt != INVALID_ALTITUDE else None,
                        'timestamp': timestamp,
                        'original_date': date_str,
                        'original_time': time_str
                    })
                    
                except (ValueError, IndexError) as e:
                    # Log error and continue with next line
                    print(f"Error parsing line in {file_path}: {e}")
                    continue
        
        # Convert to DataFrame and sort by timestamp
        df = pd.DataFrame(data)
        df.sort_values('timestamp', inplace=True)
        df.reset_index(drop=True, inplace=True)
        
        return df
    
    @staticmethod
    def load_directory(directory_path: Path) -> Dict[str, pd.DataFrame]:
        """
        Load all PLT files from a directory.
        
        Args:
            directory_path: Path to directory containing PLT files
            
        Returns:
            Dictionary mapping trajectory IDs to their respective DataFrames
        """
        trajectories = {}
        
        for plt_file in directory_path.glob("*.plt"):
            trajectory_id = plt_file.stem  # Get filename without extension
            try:
                df = TrajectoryLoader.load_plt_file(plt_file)
                trajectories[trajectory_id] = df
            except Exception as e:
                print(f"Error loading trajectory {trajectory_id}: {e}")
                continue
                
        return trajectories