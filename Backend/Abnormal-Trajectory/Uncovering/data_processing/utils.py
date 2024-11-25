"""Utility functions for trajectory data processing."""

import numpy as np
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2
from typing import Tuple, List
from .constants import (
    EARTH_RADIUS, 
    DATE_FORMAT, 
    TIME_FORMAT,
    DATETIME_FORMAT
)

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth.
    
    Args:
        lat1: Latitude of first point in decimal degrees
        lon1: Longitude of first point in decimal degrees
        lat2: Latitude of second point in decimal degrees
        lon2: Longitude of second point in decimal degrees
        
    Returns:
        Distance between points in meters
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return EARTH_RADIUS * c

def calculate_speed(
    lat1: float, 
    lon1: float, 
    lat2: float, 
    lon2: float, 
    time1: datetime, 
    time2: datetime
) -> float:
    """
    Calculate speed between two points in meters per second.
    
    Args:
        lat1: Latitude of first point
        lon1: Longitude of first point
        lat2: Latitude of second point
        lon2: Longitude of second point
        time1: Timestamp of first point
        time2: Timestamp of second point
        
    Returns:
        Speed in meters per second
    """
    distance = haversine_distance(lat1, lon1, lat2, lon2)
    time_diff = (time2 - time1).total_seconds()
    
    if time_diff == 0:
        return float('inf')
        
    return distance / time_diff

def parse_datetime(date_str: str, time_str: str) -> datetime:
    """
    Parse date and time strings from PLT format into datetime object.
    
    Args:
        date_str: Date string in YYYY-MM-DD format
        time_str: Time string in HH:mm:ss format
        
    Returns:
        datetime object
    """
    return datetime.strptime(f"{date_str} {time_str}", DATETIME_FORMAT)

def calculate_radiation(points: List[Tuple[float, float]], center_point: Tuple[float, float]) -> float:
    """
    Calculate the maximum distance (radiation) from a center point to a set of points.
    
    Args:
        points: List of (latitude, longitude) tuples
        center_point: (latitude, longitude) tuple of the center point
        
    Returns:
        Maximum distance in meters
    """
    if not points:
        return 0.0
        
    distances = [
        haversine_distance(
            center_point[0], 
            center_point[1], 
            point[0], 
            point[1]
        ) for point in points
    ]
    
    return max(distances)