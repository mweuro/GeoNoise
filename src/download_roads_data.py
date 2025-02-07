import pandas as pd
import geopandas as gpd
import osmnx as ox


def extract_max_speed(maxspeed: float | int) -> float | int:
    if isinstance(maxspeed, list):  
        # Convert list to numeric, drop NaN, take the highest value
        maxspeed_values = pd.to_numeric(maxspeed, errors = "coerce")
        return max(maxspeed_values, default = 40)
    elif pd.isna(maxspeed):
        return 40
    value = pd.to_numeric(maxspeed, errors = "coerce")
    if pd.isna(value):
        return 40
    return value



def get_roads_from_osmnx() -> gpd.GeoDataFrame:
    city = "Praha"
    roads = ox.graph_from_place(city, network_type = "drive")
    roads = ox.graph_to_gdfs(roads, nodes = False, edges = True)
    roads = roads.to_crs('EPSG:5514')
    roads["maxspeed"] = roads["maxspeed"].apply(extract_max_speed)
    return roads



def main() -> None:
    roads = get_roads_from_osmnx()
    roads.to_file("data/ROADS.geojson", driver = "GeoJSON")
    print('Roads data downloaded to data/ROADS.geojson')
    return



if __name__ == "__main__":
    main()