import numpy as np
import yaml
import geopandas as gpd
import matplotlib
import matplotlib.cm as cm


def load_yaml(file_path: str) -> dict[dict[str, str]]:
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


def filter_poligon(gdf, gdf_district, district_name):
    selected_district = gdf_district[gdf_district['NAZEV_MC'] == district_name]  
    return gpd.overlay(gdf, selected_district, how = 'intersection'), selected_district


def get_color_from_colormap(value, feature_col, colormap_name = 'turbo'):
    colormap = cm.get_cmap(colormap_name)
    min_value = feature_col.min()
    max_value = feature_col.max()
    normalized_value = (value - min_value) / (max_value - min_value)
    rgba_color = colormap(normalized_value)
    return matplotlib.colors.rgb2hex(rgba_color)


def colorbar(n, colormap_name = 'turbo'):
    values = np.linspace(0, 1, n)
    colormap = cm.get_cmap(colormap_name)
    colors = [colormap(value) for value in values]
    return colors


def style_function(feature, gdf, feature_col, colormap_name = 'turbo'):
    value = feature['properties'][feature_col]
    return {
        'color': 'black',
        'fillColor': get_color_from_colormap(value, gdf[feature_col], colormap_name),
        'weight': 2,
        'fillOpacity': 0.8
    }