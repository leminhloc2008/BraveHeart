"""Unit tests for the trajectory data loader using real PLT files."""

import unittest
import pandas as pd
from pathlib import Path
from datetime import datetime
from data_processing.data_loader import TrajectoryLoader
from data_processing.constants import INVALID_ALTITUDE

class TestTrajectoryLoader(unittest.TestCase):
    """Test cases for TrajectoryLoader class."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures that are reused across all tests."""
        # Replace with your actual test data path
        cls.test_data_dir = Path("Backend/Dataset/Geolife Trajectories 1.3/Geolife Trajectories 1.3/Data/000/Trajectory/20081027115449.plt")
        cls.loader = TrajectoryLoader()
        
        # Get list of all PLT files
        cls.plt_files = list(cls.test_data_dir.glob("*.plt"))
        if not cls.plt_files:
            raise ValueError(f"No PLT files found in {cls.test_data_dir}")
            
        # Load first file for single file tests
        cls.sample_df = cls.loader.load_plt_file(cls.plt_files[0])

    def test_load_plt_file_structure(self):
        """Test that loaded PLT file has correct structure."""
        df = self.sample_df
        
        # Check basic DataFrame properties
        self.assertIsInstance(df, pd.DataFrame)
        self.assertGreater(len(df), 0)
        
        # Check column names
        expected_columns = {
            'latitude', 'longitude', 'altitude', 
            'timestamp', 'original_date', 'original_time'
        }
        self.assertEqual(set(df.columns), expected_columns)
        
        # Check data types
        self.assertTrue(df['latitude'].dtype in ['float32', 'float64'])
        self.assertTrue(df['longitude'].dtype in ['float32', 'float64'])
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(df['timestamp']))

    def test_coordinate_ranges(self):
        """Test that coordinates are within valid ranges."""
        df = self.sample_df
        
        # Latitude should be between -90 and 90
        self.assertTrue(all(-90 <= df['latitude']) and all(df['latitude'] <= 90))
        
        # Longitude should be between -180 and 180
        self.assertTrue(all(-180 <= df['longitude']) and all(df['longitude'] <= 180))

    def test_timestamp_order(self):
        """Test that timestamps are in chronological order."""
        df = self.sample_df
        timestamps = df['timestamp'].values
        self.assertTrue(all(timestamps[i] <= timestamps[i+1] 
                          for i in range(len(timestamps)-1)))

    def test_load_directory(self):
        """Test loading multiple PLT files from directory."""
        trajectories = self.loader.load_directory(self.test_data_dir)
        
        # Check that files were loaded
        self.assertGreater(len(trajectories), 0)
        
        # Each trajectory should be a DataFrame with correct structure
        for trajectory_id, df in trajectories.items():
            self.assertIsInstance(df, pd.DataFrame)
            self.assertGreater(len(df), 0)
            expected_columns = {
                'latitude', 'longitude', 'altitude', 
                'timestamp', 'original_date', 'original_time'
            }
            self.assertEqual(set(df.columns), expected_columns)

    def test_invalid_altitude_handling(self):
        """Test that invalid altitudes (-777) are properly handled."""
        df = self.sample_df
        self.assertTrue(all(alt is None for alt in df['altitude'][df['altitude'] == INVALID_ALTITUDE]))

    def test_all_files_loadable(self):
        """Test that all PLT files in directory can be loaded."""
        for plt_file in self.plt_files:
            try:
                df = self.loader.load_plt_file(plt_file)
                self.assertIsInstance(df, pd.DataFrame)
                self.assertGreater(len(df), 0)
            except Exception as e:
                self.fail(f"Failed to load {plt_file}: {str(e)}")

if __name__ == '__main__':
    unittest.main()