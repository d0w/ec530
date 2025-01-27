import math

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)

    Args:
        lat1: latitude of point 1
        lon1: longitude of point 1
        lat2: latitude of point 2
        lon2: longitude of point 2

    Returns:
        distance: distance between the two points in meters
    """
    
    # Haversine formula: https://en.wikipedia.org/wiki/Haversine_formula

    # find differences and convert to radians
    dLat = (lat2 - lat1) * math.pi / 180.0
    dLon = (lon2 - lon1) * math.pi / 180.0
 
    # convert latitude to radians
    lat1 = (lat1) * math.pi / 180.0
    lat2 = (lat2) * math.pi / 180.0
 
    # apply formulae
    a = 1 - math.cos(dLat) + math.cos(lat1) * math.cos(lat2) * (1 - math.cos(dLon))
    radius = 6371 # Earth radius in km
    return 2 * radius * math.asin(math.sqrt(a/2))


def gps_match(locations1, locations2):
    """
    Matches each GPS location of the first array with the closest of the second

    Args:
        locations1: list of GPS locations
        locations2: list of GPS locations

    Returns:
        List of lists (point from locations1, closest point in locadtions2, distance)
    """

    out = []

    for point1 in locations1:
        # calculate distances between point1 and all points in locations2
        distances = [haversine(point1[0], point1[1], point2[0], point2[1]) for point2 in locations2]

        # find the minimum distance
        min_distance = min(distances)

        # find the index of the minimum distance
        index = distances.index(min_distance)

        # add the two points and the distance to the result
        out.append([point1, locations2[index], min_distance])

    return out





