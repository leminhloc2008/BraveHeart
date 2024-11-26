"""Constants used in data processing."""

# Speed threshold based on Usain Bolt's world record (slightly above 10m/s)
MAX_SPEED_THRESHOLD = 10.0  # meters per second

# Time window for radiation check
RADIATION_TIME_WINDOW = 60  # seconds

# Number of header lines in PLT files
HEADER_LINES = 6

# Earth's radius in meters (for distance calculations)
EARTH_RADIUS = 6371000  # meters

# Invalid altitude indicator
INVALID_ALTITUDE = -777

# Column indices in PLT files
LATITUDE_IDX = 0
LONGITUDE_IDX = 1
ALTITUDE_IDX = 3
DATE_NUM_IDX = 4
DATE_STR_IDX = 5
TIME_STR_IDX = 6

# Date format in PLT files
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S"
DATETIME_FORMAT = f"{DATE_FORMAT} {TIME_FORMAT}"