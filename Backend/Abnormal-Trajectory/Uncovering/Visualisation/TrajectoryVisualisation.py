import pandas as pd
import folium
from datetime import datetime

def parse_plt_file(file_path):
    """Parse .plt trajectory file into pandas DataFrame."""
    # Skip first 6 lines
    df = pd.read_csv(file_path, skiprows=6, header=None,
                    names=['lat', 'lon', 'zero', 'alt', 'days', 'date', 'time'])
    return df

def visualize_trajectory(file_path, save_path='trajectory_map.html'):
    """Create interactive map visualization of trajectory."""
    # Parse data
    df = parse_plt_file(file_path)
    
    # Create map centered on first point
    m = folium.Map(location=[df.lat.iloc[0], df.lon.iloc[0]], 
                  zoom_start=13)
    
    # Add trajectory line
    points = list(zip(df.lat, df.lon))
    folium.PolyLine(points, weight=2, color='blue', opacity=0.8).add_to(m)
    
    # Add markers for start and end points
    folium.Marker(
        [df.lat.iloc[0], df.lon.iloc[0]],
        popup=f"Start: {df.date.iloc[0]} {df.time.iloc[0]}",
        icon=folium.Icon(color='green')
    ).add_to(m)
    
    folium.Marker(
        [df.lat.iloc[-1], df.lon.iloc[-1]],
        popup=f"End: {df.date.iloc[-1]} {df.time.iloc[-1]}",
        icon=folium.Icon(color='red')
    ).add_to(m)
    
    # Add markers every hour
    df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'])
    hourly = df.groupby(df.datetime.dt.hour).first()
    
    for _, row in hourly.iterrows():
        folium.CircleMarker(
            location=[row.lat, row.lon],
            radius=3,
            popup=f"{row.datetime.strftime('%H:%M')}",
            color='purple',
            fill=True
        ).add_to(m)
    
    # Save map
    m.save(save_path)
    return m

if __name__ == '__main__':
    # Example usage
    trajectory_file = 'Backend/Dataset/Geolife Trajectories 1.3/Geolife Trajectories 1.3/Data/000/Trajectory/20081027115449.plt'
    visualize_trajectory(trajectory_file)