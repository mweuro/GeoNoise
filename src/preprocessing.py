import os
import geopandas as gpd
import warnings
warnings.filterwarnings("ignore")



def split_noise_multipolygons():
    gdf = gpd.read_file('data/NOISE.geojson')
    gdf = gdf.explode(index_parts = True).reset_index(drop = True)
    gdf.to_file('data/NOISE_SPLIT.geojson', driver = 'GeoJSON')
    print('NOISE.geojson splitted successfully')
    return



def shp2geojson(file_path):
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



def main():
    data_paths = [os.path.join('data', file) for file in os.listdir('data') if file.endswith('.zip') or file.endswith('.geojson') and file != 'S2_GRID.geojson']
    for data in data_paths:
        shp2geojson(data)
    split_noise_multipolygons()  
    return



if __name__ == '__main__':
    main()