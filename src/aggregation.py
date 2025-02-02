import geopandas as gpd
import pandas as pd
import os
from src.s2_grid import split_polygon
from src.download_roads_data import get_roads_from_osmnx



def create_pixels_gdf(picture):
    pixels = split_polygon(picture, number_of_pixels_on_side = 25, thresh=0.99)
    pixels = gpd.GeoDataFrame(pixels).rename(columns={0: "geometry"})
    pixels.set_geometry('geometry', inplace=True)
    pixels.set_crs('EPSG:5514', inplace=True)
    return pixels



def calculate_weighted_db(pixel, noise_gdf):
    total_area = pixel.area  # Total area of the square
    weighted_sum = 0  # Weighted sum of DB_HI
    total_weight = 0  # Total weight (should sum to 1 if fully covered)

    for _, noise in noise_gdf.iterrows():
        # Calculate intersection geometry between pixel and noise polygon
        intersection = pixel.intersection(noise.geometry)

        # If there's an intersection, calculate the weight and add to the weighted sum
        if intersection.is_valid and not intersection.is_empty:
            intersection_area = intersection.area
            weight = intersection_area / total_area  # Weight based on area covered
            weighted_sum += weight * noise["DB_HI"]
            total_weight += weight

    # Return the weighted average, default to 0 if there's no coverage
    return round(weighted_sum / 5) * 5 if total_weight > 0 else 0



def get_max_speed(pixel, roads_for_picture):
    intersecting_roads = roads_for_picture[roads_for_picture.geometry.intersects(pixel)]
    
    if not intersecting_roads.empty:
        # Convert 'maxspeed' column to numeric, handle missing values, and find the max
        return pd.to_numeric(intersecting_roads["maxspeed"], errors="coerce").max(skipna=True)
    
    return 0  # If no road is found in the square



def get_barrier(pixel, bariers_for_pixel):
    if bariers_for_pixel.geometry.intersects(pixel).any():
        return 1
    else:
        return 0



def get_buildings_levels(pixel, buildings_for_pixel):
    intersecting_buildings = buildings_for_pixel[buildings_for_pixel.geometry.intersects(pixel)].copy()
    
    if not intersecting_buildings.empty:
        intersecting_buildings['intersected_area'] = intersecting_buildings.geometry.intersection(pixel).area
        area_by_levels = intersecting_buildings.groupby('buildings_levels')['intersected_area'].sum()
        max_levels = area_by_levels.idxmax()
        return max_levels
    
    else:
        return 0



def get_parks_area(pixel, parks_for_pixel):
    parks_area = 0
    for _, park in parks_for_pixel.iterrows():
        intersecting_park = pixel.intersection(park.geometry)
        if intersecting_park:
            parks_area += intersecting_park.area

    return parks_area / pixel.area if parks_area > 0 else 0



def get_population(pixel, population_for_pixel):
    population = 0
    for _, row in population_for_pixel.iterrows():
        intersecting_district = pixel.intersection(row.geometry)
        if intersecting_district:
            population += intersecting_district.area / row.geometry.area * row.population
    
    return population



def main():
    pictures = gpd.read_file("data/S2_GRID.geojson")
    noise = gpd.read_file("data/NOISE.geojson")
    transport_lines = gpd.read_file("data/TRANSPORT_LINES.geojson")
    noise_barriers_1 = gpd.read_file('data/NOISE_BARRIERS.geojson')
    noise_barriers_2 = gpd.read_file('data/NOISE_BARRIERS_2.geojson')
    noise_barriers_1.drop(columns='ID_CLONA', inplace=True)
    noise_barriers_2.drop(columns='ID_VAL', inplace=True)
    noise_barriers = pd.concat([noise_barriers_1, noise_barriers_2]).reset_index(drop=True)
    parks = gpd.read_file('data/PARKS.geojson')
    buildings = gpd.read_file('data/BUILDINGS.geojson')
    population = gpd.read_file('data/DEMOGRAPHY.geojson')
    
    if not isinstance(population, gpd.GeoDataFrame) or 'geometry' not in population.columns:
        population = gpd.GeoDataFrame({'geometry': population})
        
    roads = get_roads_from_osmnx()
    
    # Validate and correct geometries
    noise.geometry = noise.geometry.buffer(0)
    transport_lines.geometry = transport_lines.geometry.buffer(0)
    noise_barriers.geometry = noise_barriers.geometry.buffer(0)
    parks.geometry = parks.geometry.buffer(0)
    buildings.geometry = buildings.geometry.buffer(0)
    # population = population.buffer(0)
    roads.geometry = roads.geometry.buffer(0)

    noise_bounds = noise.unary_union
    transport_lines = gpd.clip(transport_lines, noise_bounds)
    roads = gpd.clip(roads, noise_bounds)
    noise_barriers = gpd.clip(noise_barriers, noise_bounds)

    for i, picture in enumerate(pictures['geometry']):
        if os.path.exists(f"data/pictures/picture_{i}.geojson"):
            print(f"Picture {i} already processed")
            continue
        else:
            noise_for_picture = gpd.clip(noise, picture)
            roads_for_picture = gpd.clip(roads, picture)
            transport_lines_for_picture = gpd.clip(transport_lines, picture)
            buildings_for_picture = gpd.clip(buildings, picture)
            bariers_for_picture = gpd.clip(noise_barriers, picture)
            parks_for_picture = gpd.clip(parks, picture)
            
            population_subgdf = gpd.GeoDataFrame({'geometry': [picture]}, crs=population.crs)
            print(f"population_subgdf type: {type(population_subgdf)}")  # Debug print
            print(f"population type: {type(population)}")  # Debug print
            population_for_picture = gpd.sjoin(population, population_subgdf, how='inner', predicate='intersects')
            population_for_picture = population_for_picture.drop(columns='index_right')

            pixels = create_pixels_gdf(picture)

            #liczenie wzonego halasu dla kazdego piksela
            pixels["weighted_db_hi"] = pixels.geometry.apply(lambda pixel: calculate_weighted_db(pixel, noise_for_picture))
            
            #droga z max predkoscia na pixeulu
            pixels["max_speed"] = pixels["geometry"].apply(lambda pixel: get_max_speed(pixel, roads_for_picture))
            
            #czy pixel posiada transport line
            pixels['has_transport_line'] = pixels.geometry.apply(lambda pixel: transport_lines_for_picture.geometry.intersects(pixel).any())

            #noise barriers
            pixels['has_barrier'] = pixels.geometry.apply(lambda pixel: get_barrier(pixel, bariers_for_picture))

            #parks
            pixels['parks_area'] = pixels.geometry.apply(lambda pixel: get_parks_area(pixel, parks_for_picture))

            #buildings
            pixels['buildings_levels'] = pixels.geometry.apply(lambda pixel: get_buildings_levels(pixel, buildings_for_picture))

            #population
            pixels['population'] = pixels.geometry.apply(lambda pixel: get_population(pixel, population_for_picture))
            
            pixels.to_file(f"data/pictures/picture_{i}.geojson", driver="GeoJSON")
            print(f"Picture {i} processed")

    return

if __name__ == '__main__':
    main()