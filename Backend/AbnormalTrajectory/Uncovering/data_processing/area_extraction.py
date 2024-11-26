"""Module for extracting trajectory points within an area of interest."""

from typing import List, Tuple, Union
import numpy as np
import pandas as pd
from .utils import haversine_distance

class AreaExtractor:
    """Class for filtering trajectory points based on an area of interest."""
    
    def __init__(self, polygon_points: List[Tuple[float, float]]):
        """
        Initialize AreaExtractor with polygon vertices.
        
        Args:
            polygon_points: List of (latitude, longitude) tuples defining the polygon vertices
        
        Raises:
            ValueError: If polygon is invalid (less than 3 points or not closed)
        """
        if len(polygon_points) < 3:
            raise ValueError("Polygon must have at least 3 points")
            
        # Ensure polygon is closed (first and last points are the same)
        if polygon_points[0] != polygon_points[-1]:
            polygon_points.append(polygon_points[0])
            
        self.polygon = np.array(polygon_points)
        
    def is_point_inside(self, lat: float, lon: float) -> bool:
        """
        Determine if a point is inside the polygon using ray-casting algorithm.
        
        Args:
            lat: Latitude of the point
            lon: Longitude of the point
            
        Returns:
            bool: True if point is inside polygon, False otherwise
        """
        crossings = 0
        n_points = len(self.polygon)
        
        for i in range(n_points - 1):
            # Get current and next vertex
            y1, x1 = self.polygon[i]
            y2, x2 = self.polygon[i + 1]
            
            # Check if point is on horizontal edge
            if y1 == y2 and y1 == lat and (min(x1, x2) <= lon <= max(x1, x2)):
                return True
                
            # Check if point is on vertical edge
            if x1 == x2 and x1 == lon and (min(y1, y2) <= lat <= max(y1, y2)):
                return True
            
            # Point is above the edge
            if ((y1 <= lat) and (y2 > lat)) or ((y2 <= lat) and (y1 > lat)):
                # Calculate intersection of ray with edge
                if x1 != x2:
                    slope = (y2 - y1) / (x2 - x1)
                    x_intersect = x1 + (lat - y1) / slope
                    
                    if x_intersect == lon:  # Point is on edge
                        return True
                    if x_intersect > lon:  # Ray crosses edge
                        crossings += 1
                else:  # Vertical edge
                    if x1 > lon:  # Ray crosses vertical edge
                        crossings += 1
        
        return crossings % 2 == 1
    
    def filter_points(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter trajectory points to keep only those within the polygon.
        
        Args:
            df: DataFrame with latitude and longitude columns
            
        Returns:
            DataFrame containing only points within the polygon
        """
        # Create mask for points inside polygon
        mask = df.apply(
            lambda row: self.is_point_inside(row['latitude'], row['longitude']),
            axis=1
        )
        
        return df[mask].reset_index(drop=True)
    
    def get_centroid(self) -> Tuple[float, float]:
        """
        Calculate the centroid of the polygon.
        
        Returns:
            Tuple of (latitude, longitude) for polygon centroid
        """
        # Remove the last point if it's duplicated
        points = self.polygon[:-1] if np.array_equal(self.polygon[0], self.polygon[-1]) else self.polygon
        
        # Calculate centroid
        lat_mean = np.mean(points[:, 0])
        lon_mean = np.mean(points[:, 1])
        
        return (lat_mean, lon_mean)
    
    def get_bounding_box(self) -> Tuple[float, float, float, float]:
        """
        Get the bounding box of the polygon.
        
        Returns:
            Tuple of (min_lat, min_lon, max_lat, max_lon)
        """
        min_lat = np.min(self.polygon[:, 0])
        min_lon = np.min(self.polygon[:, 1])
        max_lat = np.max(self.polygon[:, 0])
        max_lon = np.max(self.polygon[:, 1])
        
        return (min_lat, min_lon, max_lat, max_lon)
        
    def estimate_area(self) -> float:
        """
        Estimate the area of the polygon in square meters using haversine distances.
        
        Returns:
            Approximate area in square meters
        """
        # Remove the last point if it's duplicated
        points = self.polygon[:-1] if np.array_equal(self.polygon[0], self.polygon[-1]) else self.polygon
        
        # Calculate area using shoelace formula with haversine distances
        area = 0.0
        n = len(points)
        
        for i in range(n):
            j = (i + 1) % n
            # Get points
            lat1, lon1 = points[i]
            lat2, lon2 = points[j]
            # Calculate contribution to area
            area += lat1 * lon2 - lat2 * lon1
            
        # Convert to square meters (approximate)
        area = abs(area) * 0.5 * (111319.9) ** 2  # 111319.9 meters per degree
        
        return area