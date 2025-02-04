import math
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gps.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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

    logger.debug(f"dLat: {dLat}, dLon: {dLon}, lat1: {lat1}, lat2: {lat2}")
 
    # apply formulae
    a = 1 - math.cos(dLat) + math.cos(lat1) * math.cos(lat2) * (1 - math.cos(dLon))
    radius = 6371 # Earth radius in km
    logger.info(f"Distance calculated: {2 * radius * math.asin(math.sqrt(a/2))}")
    return 2 * radius * math.asin(math.sqrt(a/2))

def validate_coordinates(locations, name="locations"):
    """Validate GPS coordinate array format and values"""
    logger.debug(f"Validating coordinates for {name}")
    if not isinstance(locations, (list, tuple)) or not locations:
        logger.error(f"{name} must be a non-empty list/tuple")
        raise ValueError(f"{name} must be a non-empty list/tuple")
    
    for point in locations:
        if not isinstance(point, (list, tuple)) or len(point) != 2:
            logger.error(f"Each point in {name} must be a list/tuple of length 2")
            raise ValueError(f"Each point in {name} must be a list/tuple of length 2")
        
        lat, lon = point
        if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
            logger.error(f"Coordinates in {name} must be numbers")
            raise ValueError(f"Coordinates in {name} must be numbers")
            
        if not -90 <= lat <= 90:
            logger.error(f"Invalid latitude in {name}: {lat}")
            raise ValueError(f"Invalid latitude in {name}: {lat}")
        if not -180 <= lon <= 180:
            logger.error(f"Invalid longitude in {name}: {lon}")
            raise ValueError(f"Invalid longitude in {name}: {lon}")


def gps_match(locations1, locations2):
    """
    Matches each GPS location of the first array with the closest of the second

    Args:
        locations1: list of GPS locations
        locations2: list of GPS locations

    Returns:
        List of lists (point from locations1, closest point in locadtions2, distance)
    """

    logger.info("Starting GPS location matching")

    validate_coordinates(locations1, "locations1")
    validate_coordinates(locations2, "locations2")

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

        logger.info(f"Match found")


    return out





