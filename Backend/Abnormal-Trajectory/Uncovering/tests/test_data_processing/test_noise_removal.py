"""Unit tests for the noise removal functionality using real PLT files."""

import unittest
import pandas as pd
from pathlib import Path
from data_processing.noise_removal import NoiseRemover
from data_processing.data_loader import TrajectoryLoader
from data_processing.constants import MAX_SPEED_THRESHOLD, RADIATION_TIME_WINDOW

class TestNoiseRemover(unittest.TestCase):
    """Test cases for NoiseRemover class."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures that are reused across all tests."""
        # Replace with your actual test data path
        cls.test_data_dir = Path("Backend/Dataset/Geolife Trajectories 1.3/Geolife Trajectories 1.3/Data/000/Trajectory/20081027115449.plt")
        cls.loader = TrajectoryLoader()
        cls.noise_remover = NoiseRemover()
        
        # Load sample trajectory data
        cls.plt_files = list(cls.test_data_dir.glob("*.plt"))
        if not cls.plt_files:
            raise ValueError(f"No PLT files found in {cls.test_data_dir}")
            
        # Load first file for single file tests
        cls.sample_df = cls.loader.load_plt_file(cls.plt_files[0])

    def test_speed_outlier_removal(self):
        """Test removal of speed-based outliers."""
        cleaned_df = self.noise_remover.remove_speed_outliers(self.sample_df)
        
        # Check that we still have data after cleaning
        self.assertGreater(len(cleaned_df), 0)
        
        # Calculate speeds between consecutive points in cleaned data
        for i in range(len(cleaned_df) - 1):
            lat1, lon1 = cleaned_df.iloc[i][['latitude', 'longitude']]
            lat2, lon2 = cleaned_df.iloc[i+1][['latitude', 'longitude']]
            time1 = cleaned_df.iloc[i]['timestamp']
            time2 = cleaned_df.iloc[i+1]['timestamp']
            
            speed = self.noise_remover.calculate_speed(
                lat1, lon1, lat2, lon2, time1, time2
            )
            self.assertLessEqual(speed, MAX_SPEED_THRESHOLD)

    def test_radiation_outlier_removal(self):
        """Test removal of radiation-based outliers."""
        cleaned_df = self.noise_remover.remove_radiation_outliers(self.sample_df)
        
        # Check that we still have data after cleaning
        self.assertGreater(len(cleaned_df), 0)
        
        # Verify radiation constraint for each point
        for i in range(len(cleaned_df)):
            current_time = cleaned_df.iloc[i]['timestamp']
            window_end = current_time + pd.Timedelta(seconds=RADIATION_TIME_WINDOW)
            
            # Get points in the next minute
            window_points = cleaned_df[
                (cleaned_df['timestamp'] > current_time) & 
                (cleaned_df['timestamp'] <= window_end)
            ]
            
            if len(window_points) > 0:
                current_point = (
                    cleaned_df.iloc[i]['latitude'],
                    cleaned_df.iloc[i]['longitude']
                )
                window_coords = list(zip(
                    window_points['latitude'],
                    window_points['longitude']
                ))
                
                max_radiation = self.noise_remover.calculate_radiation(
                    window_coords, current_point
                )
                implied_speed = max_radiation / RADIATION_TIME_WINDOW
                
                self.assertLessEqual(implied_speed, MAX_SPEED_THRESHOLD)

    def test_complete_cleaning_pipeline(self):
        """Test the complete trajectory cleaning process on multiple files."""
        for plt_file in self.plt_files[:5]:  # Test first 5 files
            df = self.loader.load_plt_file(plt_file)
            cleaned_df = self.noise_remover.clean_trajectory(df)
            
            # Basic checks on cleaned data
            self.assertGreater(len(cleaned_df), 0)
            self.assertLess(len(cleaned_df), len(df))  # Should remove some points
            
            # Check that remaining points form a valid trajectory
            for i in range(len(cleaned_df) - 1):
                lat1, lon1 = cleaned_df.iloc[i][['latitude', 'longitude']]
                lat2, lon2 = cleaned_df.iloc[i+1][['latitude', 'longitude']]
                time1 = cleaned_df.iloc[i]['timestamp']
                time2 = cleaned_df.iloc[i+1]['timestamp']
                
                speed = self.noise_remover.calculate_speed(
                    lat1, lon1, lat2, lon2, time1, time2
                )
                self.assertLessEqual(speed, MAX_SPEED_THRESHOLD)

    def test_custom_speed_threshold(self):
        """Test noise removal with custom speed threshold."""
        custom_threshold = 5.0  # 5 m/s
        custom_remover = NoiseRemover(speed_threshold=custom_threshold)
        
        cleaned_df = custom_remover.clean_trajectory(self.sample_df)
        
        # Verify that all consecutive points have speeds below custom threshold
        for i in range(len(cleaned_df) - 1):
            lat1, lon1 = cleaned_df.iloc[i][['latitude', 'longitude']]
            lat2, lon2 = cleaned_df.iloc[i+1][['latitude', 'longitude']]
            time1 = cleaned_df.iloc[i]['timestamp']
            time2 = cleaned_df.iloc[i+1]['timestamp']
            
            speed = custom_remover.calculate_speed(
                lat1, lon1, lat2, lon2, time1, time2
            )
            self.assertLessEqual(speed, custom_threshold)

if __name__ == '__main__':
    unittest.main()