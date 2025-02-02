import osmnx as ox
import pandas as pd
import os



def download_buildings():
    if os.path.exists('data/BUILDINGS.geojson'):
        print('The file data/BUILDINGS.geojson already exists')
    else:
        city = 'Praha'
        buildings = ox.features_from_place(city, tags={'building': True})
        buildings = buildings[['geometry', 'building:levels']]
        buildings = buildings[(buildings['building:levels'].notna())]
        buildings['building:levels'] = pd.to_numeric(buildings['building:levels'], errors='coerce')
        buildings = buildings[buildings['building:levels'].notna()]
        buildings = buildings[buildings.geometry.type.isin(['Polygon', 'MultiPolygon'])]
        buildings = buildings.rename(columns={'building:levels': 'buildings_levels'})
        buildings.to_file(f"data/BUILDINGS.geojson", driver="GeoJSON")
        print('Buildings data downloaded to data/BUILDINGS.geojson')
    return



def main():
    download_buildings()
    return



if __name__ == '__main__':
    main()