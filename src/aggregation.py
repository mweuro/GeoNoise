import geopandas as gpd



def fix_geometry(geom):
    if not geom.is_valid:
        geom = geom.buffer(0)
    return geom



def aggregate_parks(tile, gdf):
    parks_area = 0
    tile = fix_geometry(tile)
    for _, row in gdf.iterrows():
        if tile.intersects(row.geometry):
            parks_area += tile.intersection(row.geometry).area
    return tile, parks_area / tile.area



def aggregate_noise(tile, gdf):
    total_noise = 0
    total_area = 0
    tile = fix_geometry(tile)
    for _, row in gdf.iterrows():
        if tile.intersects(row.geometry):
            total_noise += tile.intersection(row.geometry).area * row.DB_HI
            total_area += tile.intersection(row.geometry).area
            
    avg_noise = total_noise / total_area
    avg_noise = round(avg_noise / 5) * 5
    return tile, avg_noise



def aggregate_population(tile, gdf):
    population = 0
    tile = fix_geometry(tile)
    for _, row in gdf.iterrows():
        if tile.intersects(row.geometry):
            area_ratio = (tile.intersection(row.geometry).area / tile.area)
            population += area_ratio * row.population
    return tile, round(population)



# def aggregate_single_info(tile, feature_gdf, *features):
#     feature_values_dict = {feature: 0 for feature in features}
#     for _, row in feature_gdf.iterrows():
#         if tile.intersects(row.geometry):
#             dct = row.to_dict()
#             area_ratio = (tile.intersection(row.geometry).area / tile.area)
#             for feature in features:
#                 feature_values_dict[feature] += area_ratio * dct[feature]
#     for feature, feature_value in feature_values_dict.items():
#         feature_values_dict[feature] = round(feature_value)
#     feature_values_dict['tile'] = tile        
#     return feature_values_dict



def aggregate_features():
    tile_gdf = gpd.read_file('data/S2_GRID.geojson')
    parks_gdf = gpd.read_file('data/PARKS.geojson')
    noise_gdf = gpd.read_file('data/NOISE_SPLIT.geojson')
    demography_gdf = gpd.read_file('data/DEMOGRAPHY.geojson')
    tiles = []
    parks_areas = []
    avg_noises = []
    populations = []
    
    for _, row in tile_gdf.head(5).iterrows():
        try:
            tile = row.geometry
            _, avg_noise = aggregate_noise(tile, noise_gdf)
            _, parks_area = aggregate_parks(tile, parks_gdf)
            _, population = aggregate_population(tile, demography_gdf)
            tiles.append(tile)
            avg_noises.append(avg_noise)
            parks_areas.append(parks_area)
            populations.append(population)
        except:
            pass
    
    output_dict = {
        'avg_noise': avg_noises,
        'parks_area': parks_areas,
        'population': populations,
        'geometry': tiles
    }
    
    output_gdf = gpd.GeoDataFrame(output_dict)
    output_gdf.set_geometry('geometry', inplace = True)
    output_gdf.set_crs(epsg = 5514, inplace = True)
    output_gdf = output_gdf.to_file('data/OUTPUT_DATA.geojson', driver = 'GeoJSON')
    print('Features aggregated successfully')
    return



def main():
    aggregate_features()
    return



if __name__ == '__main__':
    main()