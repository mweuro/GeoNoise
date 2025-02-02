import pandas as pd
import osmnx as ox


def extract_max_speed(maxspeed):
    if isinstance(maxspeed, list):  
        # Convert list to numeric, drop NaN, take the highest value
        maxspeed_values = pd.to_numeric(maxspeed, errors="coerce")
        return max(maxspeed_values, default=40)  # Return highest speed or 40 if empty
    elif pd.isna(maxspeed):  # If NaN, return 40
        return 40
    value = pd.to_numeric(maxspeed, errors="coerce")
    if pd.isna(value):
        return 40
    return value



def get_roads_from_osmnx():
    city = "Praha"
    roads = ox.graph_from_place(city, network_type="drive")
    roads = ox.graph_to_gdfs(roads, nodes=False, edges=True)
    roads = roads.to_crs('EPSG:5514')
    roads["maxspeed"] = roads["maxspeed"].apply(extract_max_speed)
    return roads