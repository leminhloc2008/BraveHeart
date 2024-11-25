"""Module for removing noise from trajectory data."""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Tuple
from .constants import (
    MAX_SPEED_THRESHOLD,
    RADIATION_TIME_WINDOW
)
from .utils import calculate_speed, calculate_radiation

class NoiseRemover:
    """Class for removing noise from trajectory data."""
    
    def __init__(self, speed_threshold: float = MAX_SPEED_THRESHOLD):
        """
        Initialize NoiseRemover.
        
        Args:
            speed_threshold: Maximum allowed speed in m/s
        """
        self.speed_threshold = speed_threshold
    
    def remove_speed_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove points where speed exceeds threshold.
        
        Args:
            df: DataFrame with columns [latitude, longitude, timestamp]
            
        Returns:
            DataFrame with outlier points removed
        """
        # Calculate speeds between consecutive points
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
        speeds.append(0)  # Add 0 for last point
        
        # Create mask for valid points
        valid_mask = pd.Series(speeds) <= self.speed_threshold
        
        return df[valid_mask].reset_index(drop=True)
    
    def remove_radiation_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove points based on distance radiation check within time windows.
        
        Args:
            df: DataFrame with columns [latitude, longitude, timestamp]
            
        Returns:
            DataFrame with outlier points removed
        """
        valid_indices = []
        
        for i in range(len(df)):
            current_time = df.iloc[i]['timestamp']
            window_end = current_time + timedelta(seconds=RADIATION_TIME_WINDOW)
            
            # Get points in the next minute
            window_points = df[
                (df['timestamp'] > current_time) & 
                (df['timestamp'] <= window_end)
            ]
            
            if len(window_points) == 0:
                valid_indices.append(i)
                continue
            
            # Calculate maximum radiation from current point
            current_point = (
                df.iloc[i]['latitude'],
                df.iloc[i]['longitude']
            )
            window_coords = list(zip(
                window_points['latitude'],
                window_points['longitude']
            ))
            
            max_radiation = calculate_radiation(window_coords, current_point)
            
            # Calculate implied speed based on radiation
            implied_speed = max_radiation / RADIATION_TIME_WINDOW
            
            if implied_speed <= self.speed_threshold:
                valid_indices.append(i)
        
        return df.iloc[valid_indices].reset_index(drop=True)
    
    def clean_trajectory(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply both speed and radiation-based noise removal.
        
        Args:
            df: DataFrame with trajectory data
            
        Returns:
            Cleaned DataFrame
        """
        # First remove speed-based outliers
        df_clean = self.remove_speed_outliers(df)
        
        # Then remove radiation-based outliers
        df_clean = self.remove_radiation_outliers(df_clean)
        
        return df_clean