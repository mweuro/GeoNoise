import os
import geopandas as gpd
import warnings
warnings.filterwarnings("ignore")



def shp2geojson(file_path: str) -> None:
    gdf = gpd.read_file(file_path)
    new_file_path = f"{file_path.split('.')[0]}.geojson"
    if gdf.crs.to_epsg() == 5514:
        print(f"Geometry in {file_path} is already set to 5514")
        pass
    else:
        gdf = gdf.to_crs(epsg = 5514)
        print(f"Geometry in {file_path} changed successfully to 5514")
    os.remove(file_path)
    gdf.to_file(new_file_path, driver = 'GeoJSON')
    print(f"{file_path} is now saved as {new_file_path}")
    
    return



def main() -> None:
    data_paths = [os.path.join('data', file) for file in os.listdir('data') if file.endswith('.zip') or file.endswith('.geojson') and file != 'S2_GRID.geojson']
    for data in data_paths:
        shp2geojson(data)
    return



if __name__ == '__main__':
    main()