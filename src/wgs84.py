import os
import geopandas as gpd
from functools import partial
import pyproj
from shapely.ops import transform



def convert_to_wgs84(polygon):
    
    project = partial(
        pyproj.transform,
        pyproj.Proj(init = 'epsg:3857'),
        pyproj.Proj(init = 'epsg:4326')
    )
    polygon_wgs84 = transform(project, polygon)
    
    return polygon_wgs84



def convert_to_wgs84_df(df):
    df = df.copy()
    df['geometry'] = df['geometry'].apply(convert_to_wgs84)
    return df



def main():
    data_paths = [os.path.join('data', path) for path in os.listdir('data')][0]
    for data in data_paths:
        gdf = gpd.read_file(data)
        gdf = convert_to_wgs84_df(gdf)
        filename = (os.path.join('data', data.split('/')[1].split['.'][0]))