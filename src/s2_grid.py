import numpy as np
import geopandas as gpd
from shapely.ops import split
from shapely.geometry import MultiPolygon, LineString
import warnings
warnings.filterwarnings("ignore")




def get_squares_from_rect(RectangularPolygon, side_length=0.0025):
    """
    Divide a Rectangle (Shapely Polygon) into squares of equal area.

    `side_length` : required side of square

    """
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



def split_polygon(G, side_length = None, 
                  number_of_pixels_on_side = None, 
                  thresh = 0.9):
    """
    Using a rectangular envelope around `G`, creates a mesh of squares of required length.
    
    Removes non-intersecting polygons. 
            

    Args:
    
    - `thresh` : Range - [0,1]

        This controls - the number of smaller polygons at the boundaries.
        
        A thresh == 1 will only create (or retain) smaller polygons that are 
        completely enclosed (area of intersection=area of smaller polygon) 
        by the original Geometry - `G`.
        
        A thresh == 0 will create (or retain) smaller polygons that 
        have a non-zero intersection (area of intersection>0) with the
        original geometry - `G` 

    - `side_length` : Range - (0,infinity)
        side_length must be such that the resultant geometries are smaller 
        than the original geometry - `G`, for a useful result.

        side_length should be >0 (non-zero positive)

    - `shape` : {square/rhombus}
        Desired shape of subset geometries. 


    """
    if side_length is not None and number_of_pixels_on_side is not None:
        raise ValueError("Provide either side_length or number_of_pixels_on_side, not both")
    
    if side_length is not None:
        assert side_length > 0, "side_length must be a float>0"
    elif number_of_pixels_on_side is not None:
        side_length = int(1500 / number_of_pixels_on_side)
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



def main():
    try:
        districts = gpd.read_file('data/DISTRICTS.zip')
    except:
        districts = gpd.read_file('data/DISTRICTS.geojson')
    city_boundary = districts.unary_union
    squares   = split_polygon(city_boundary, 
                              thresh = 0.01, 
                              side_length = 1500)
    squares = gpd.GeoDataFrame(squares).rename(columns = {0: "geometry"})
    squares.set_geometry('geometry', inplace = True)
    squares.set_crs(epsg = 5514, inplace = True)
    squares.to_file('data/S2_GRID.geojson', driver = 'GeoJSON')



if __name__ == "__main__":
    main()