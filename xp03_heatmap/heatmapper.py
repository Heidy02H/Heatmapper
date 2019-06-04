"""Map the heights to color."""
import topo
from PIL import Image
from PIL import ImageDraw
import os


def generate_map(topo_data, width, height, filename):
    """
    Generate (heat)map into an image file.

    topo_data comes from topo module. The data is a list
    where every element contains latitude, longitude and altitude (in meters).
    The function should treat coordinates as regular y and x (flat world).
    The image should fill the whole width, height. Every "point" in the data
    should be represented as a rectangle on the image.

    For example, if topo_data has 12 elements (latitude, longitude, altitude):
    10, 10, 1
    10, 12, 1
    10, 14, 2
    12, 10, 1
    12, 12, 3
    12, 14, 1
    14, 10, 6
    14, 12, 9
    14, 14, 12
    16, 10, 1
    16, 12, 1
    16, 14, 3
    and the width = 100, height = 100
    then the first line in data should be represented as a rectangle (0, 0) - (33, 25)
    (x1, y1) - (x2, y2).
    The height is divided into 4, each "point" is 100/4 = 25 pixels high,
    the width is divided into 3, each "point" is 100/3 = 33 pixels wide.
    :param topo_data: list of topography data (from topo module)
    :param width: width of the image
    :param height: height of the image
    :param filename: the file to be written
    :return: True if everything ok, False otherwise
    """
    try:
        all_lats = []
        all_lng = []
        all_heights = []
        for e in topo_data:
            all_lats.append(e[0])
            all_lng.append(e[1])
            all_heights.append(e[2])

        # How many different values to I have to use
        all_lats = set(all_lats)
        all_lng = set(all_lng)

        high = height / len(all_lats)
        wide = width / len(all_lng)

        im = Image.new('RGB', (width, height), (255, 0, 0))
        draw = ImageDraw.Draw(im)

        for i in range(len(list(all_lng))):
            for j in range(len(list(all_lats))):
                height_count = i + len(list(all_lng)) * j
                draw.rectangle(((i * wide, j * high), ((i + 1) * wide, (j + 1) * high)), fill=calculate_color(all_heights[height_count], min(all_heights), max(all_heights)))

        im.save(filename)

        return True
    except ValueError:
        return False


def calculate_color(height, min_height, max_height):
    """
    Calculate the color according to height.

    :param height: int
    :param min_height: int
    :param max_height: int
    :return: tuple
    """
    if height < 0:
        difference = abs(min_height)
        return 0, 0, 255 - int((abs(height) / difference) * 255)
    else:
        difference = max_height
        return 0, 255 - int((height / difference) * 255), 0


def generate_map_with_coordinates(topo_params, image_width, image_height, filename):
    """
    Given the topo parameters and image parameters, generate map into a file.

    topo_parameters = (min_latitude, max_latitude, latitude_stride, min_longitude, max_longitude, longitude_stride)
    In the case where latitude_stride and/or longitude_stride are 0,
    you have to calculate step yourself, based on the image parameters.
    For example, if image size is 10 x 10, there is no point to query more than 10 x 10 topological points.
    Hint: check the website, there you see "size" for both latitude and longitude.
    Also, read about "stride" (the question mark behind stride in the form).

    Caching:
    if all the topo params are calculated (or given), then it would be wise
    to cache the query results. One implementation could be as follows:
    filename = topo_57-60-3_22-28-1.json
    (where 57 = min_lat, 60 = max_lat, 3 latitude stride etc)
     if file exists:
         topo.read_json_from_file(file)
     else:
         result = topo.read_json_from_web(...)
         with open(filename, 'w'):
             f.write(result)

     ... do the rest


    :param topo_params: tuple with parameters for topo query
    :param image_width: image width in pixels
    :param image_height: image height in pixels
    :param filename: filename to store the image
    :return: True, if everything ok, False otherwise
    """
    min_latitude = topo_params[0]
    max_latitude = topo_params[1]
    latitude_stride = topo_params[2]
    min_longitude = topo_params[3]
    max_longitude = topo_params[4]
    longitude_stride = topo_params[5]

    if latitude_stride == 0:
        latitude_stride = int(max(1, (max_latitude - min_latitude) / 0.0083333 / image_height))

    if longitude_stride == 0:
        longitude_stride = int(max(1, (max_longitude - min_longitude) / 0.0083333 / image_height))

    cache = f"topo_{min_latitude} - {max_latitude} - {latitude_stride}_{min_longitude} - {max_longitude} - {longitude_stride}.json"

    if not os.path.exists(cache):
        result = topo.read_json_from_web(min_latitude, max_latitude, latitude_stride, min_longitude, max_longitude, longitude_stride)
        with open(cache, 'w') as f:
            f.write(result)

    topo_data = topo.get_topo_data_from_string(topo.read_json_from_file(cache))
    print("pikkus", len(topo_data))
    generate_map(topo_data, image_width, image_height, filename)

    return True


if __name__ == '__main__':
    topo_data = topo.get_topo_data_from_string(topo.read_json_from_web(57.5, 60, 2, 22, 29, 2))
    generate_map(topo_data, 1500, 1000, "mymap.png")

    # generate_map_with_coordinates((57.5, 60, 0, 22, 29, 0), 11, 10, "eesti.png")
    # generate_map_with_coordinates((-89.9, 90, 0, -180, 179.9, 0), 600, 400, "world.png")
