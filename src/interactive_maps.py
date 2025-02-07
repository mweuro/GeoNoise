import pandas as pd
import geopandas as gpd
import folium
import branca.colormap as cmp
from utils import *
from plots import *




def noise_map() -> None:
    m = folium.Map(location = [50.08804, 14.42076], zoom_start = 12)
    
    NOISE = gpd.read_file('data/NOISE.geojson')
    NOISE = pd.concat([NOISE.iloc[[-1]], NOISE.iloc[:-1]]).reset_index(drop = True)
    NOISE.geometry = NOISE.geometry.simplify(tolerance = 150, preserve_topology = True)
    folium.GeoJson(
        NOISE,
        name = 'Noise',
        style_function = lambda feature: style_function(feature, NOISE, 'DB_LO', 'turbo'),
        tooltip = folium.GeoJsonTooltip(fields = ['DB_LO', 'DB_HI'], aliases = ['DB_LO', 'DB_HI']),
    ).add_to(m)
    step = cmp.StepColormap(
    colorbar(18),
    vmin = 0, 
    vmax = 85,
    caption = 'Noise level'
    )
    m.add_child(step)
    
    PARKS = gpd.read_file('data/PARKS.geojson')
    folium.GeoJson(
        PARKS,
        name = 'Parks',
        style_function = lambda x: {'color': 'black', 
                                    'fillColor': 'darkgreen', 
                                    'weight': 2, 
                                    'fillOpacity': 0.4},
        tooltip = folium.GeoJsonTooltip(fields = ['NAZEV'], aliases = ['Park name']),
    ).add_to(m)

    DEMOGRAPHY = gpd.read_file('data/DEMOGRAPHY.geojson')
    folium.GeoJson(
        DEMOGRAPHY,
        name = 'Population',
        style_function = lambda x: {'color': 'black', 
                                    'fillColor': 'brown', 
                                    'weight': 2, 
                                    'fillOpacity': 0.4},
        tooltip = folium.GeoJsonTooltip(fields = ['region_id', 'population'], aliases = ['region_id', 'population']),
    ).add_to(m)
    
    DISTRICTS = gpd.read_file('data/DISTRICTS.geojson')
    folium.GeoJson(
        DISTRICTS,
        name = 'Districts',
        style_function = lambda x: {'color': 'black', 
                                    'fillColor': 'lightblue', 
                                    'weight': 2, 
                                    'fillOpacity': 0.4},
        tooltip = folium.GeoJsonTooltip(fields = ['NAZEV_MC'], aliases = ['District name']),
    ).add_to(m)
    
    ROADS = gpd.read_file('data/ROADS.geojson')
    folium.GeoJson(
        ROADS,
        name = 'Roads',
        style_function = lambda x: {'color': 'black', 
                                    'weight': 2, 
                                    'fillOpacity': 0.6},
        tooltip = folium.GeoJsonTooltip(fields = ['maxspeed'], aliases = ['Speed limit']),
    ).add_to(m)
    
    BUILDINGS = gpd.read_file('data/BUILDINGS.geojson')
    folium.GeoJson(
        BUILDINGS,
        name = 'Buildings',
        style_function = lambda x: {'color': 'black', 
                                    'fillColor': 'violet',
                                    'weight': 2, 
                                    'fillOpacity': 0.8},
        tooltip = folium.GeoJsonTooltip(fields = ['buildings_levels'], aliases = ['Building levels']),
    ).add_to(m)
    
    
    
    NOISE_BARRIERS_1 = gpd.read_file('data/NOISE_BARRIERS.geojson')
    NOISE_BARRIERS_2 = gpd.read_file('data/NOISE_BARRIERS_2.geojson')
    NOISE_BARRIERS_1.drop(columns = 'ID_CLONA', inplace = True)
    NOISE_BARRIERS_2.drop(columns = 'ID_VAL', inplace = True)
    NOISE_BARRIERS = pd.concat([NOISE_BARRIERS_1, NOISE_BARRIERS_1]).reset_index(drop = True)
    folium.GeoJson(
        NOISE_BARRIERS,
        name = 'Noise Barriers',
        style_function = lambda x: {'color': 'black', 
                                    'fillColor': 'darkblue',
                                    'weight': 2, 
                                    'fillOpacity': 0.8},
    ).add_to(m)
    
    
    folium.LayerControl().add_to(m)
    m.save("maps/prague_map.html")
    return



def main() -> None:
    noise_map()
    print('MAP CREATED')
    return



if __name__ == '__main__':
    main()