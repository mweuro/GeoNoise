import numpy as np
import geopandas as gpd
from shapely.ops import split
from shapely.geometry import MultiPolygon, LineString, Polygon
import warnings
warnings.filterwarnings("ignore")
from src.utils import load_yaml




def get_squares_from_rect(RectangularPolygon: Polygon | MultiPolygon, 
                          side_length: int) -> list[Polygon]:
    rect_coords = np.array(RectangularPolygon.boundary.coords.xy)
    y_list = rect_coords[1]
    x_list = rect_coords[0]
    y1 = min(y_list)
    y2 = max(y_list)
    x1 = min(x_list)
    x2 = max(x_list)
    width = x2 - x1
    height = y2 - y1

    xcells = int(np.round(width / side_length))
    ycells = int(np.round(height / side_length))

    yindices = np.linspace(y1, y2, ycells + 1)
    xindices = np.linspace(x1, x2, xcells + 1)
    horizontal_splitters = [
        LineString([(x, yindices[0]), (x, yindices[-1])]) for x in xindices
    ]
    vertical_splitters = [
        LineString([(xindices[0], y), (xindices[-1], y)]) for y in yindices
    ]
    result = RectangularPolygon
    for splitter in vertical_splitters:
        result = MultiPolygon(split(result, splitter))
    for splitter in horizontal_splitters:
        result = MultiPolygon(split(result, splitter))
    square_polygons = list(result.geoms)

    return square_polygons



def split_polygon(G: Polygon, side_length: int = None, 
                  number_of_pixels_on_side: int = None, 
                  thresh: float = 0.01) -> list[Polygon]:

    side_param = load_yaml('params.yaml')['s2_grid_params']['side_length']
    if side_length is not None and number_of_pixels_on_side is not None:
        raise ValueError("Provide either side_length or number_of_pixels_on_side, not both")
    
    if side_length is not None:
        assert side_length > 0, "side_length must be a float>0"
    elif number_of_pixels_on_side is not None:
        side_length = int(side_param / number_of_pixels_on_side)
        assert side_length > 0, "side_length must be a float>0"
    else:
        raise ValueError("Either side_length or number_of_pixels_on_side must be provided")

    Rectangle = G.envelope
    squares = get_squares_from_rect(Rectangle, side_length=side_length)
    SquareGeoDF = gpd.GeoDataFrame(squares).rename(columns={0: "geometry"})
    SquareGeoDF.set_geometry('geometry', inplace=True)
    Geoms = SquareGeoDF[SquareGeoDF.intersects(G)].geometry.values
    geoms = [g for g in Geoms if ((g.intersection(G)).area / g.area) >= thresh]
    return geoms



def main() -> None:
    yaml_path = 'params.yaml'
    params = load_yaml(yaml_path)['s2_grid_params']
    
    districts = gpd.read_file('data/DISTRICTS.zip')
    city_boundary = districts.unary_union
    squares = split_polygon(city_boundary, 
                            **params)
    squares = gpd.GeoDataFrame(squares).rename(columns = {0: "geometry"})
    squares.set_geometry('geometry', inplace = True)
    squares.set_crs(epsg = 5514, inplace = True)
    squares.to_file('data/S2_GRID.geojson', driver = 'GeoJSON')



if __name__ == "__main__":
    main()