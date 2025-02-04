import sys
sys.path.insert(0, '.')
import pytest

# import importlib  
# foobar = importlib.import_module("assignment-1")

import gps

def test_valid_coordinates():
    locations1 = [[42.3601, -71.0589], [40.7128, -74.0060]]  # Boston, NYC
    locations2 = [[42.3601, -71.0589], [41.8781, -87.6298]]  # Boston, Chicago
    result = gps.gps_match(locations1, locations2)
    assert len(result) == len(locations1)
    assert all(isinstance(match, list) and len(match) == 3 for match in result)

def test_invalid_format():
    invalid_inputs = [
        ("string", [[0, 0]]),
        ([[0, 0]], "string"),
        ([0, 0], [[0, 0]]),
        ([[0]], [[0, 0]]),
        ([[0, 0, 0]], [[0, 0]])
    ]
    for loc1, loc2 in invalid_inputs:
        with pytest.raises(ValueError):
            gps.gps_match(loc1, loc2)


def test_haversine():
    assert(round(gps.haversine(40.7, -74.0, 37.7, -122.4), 1) == 4131.1)

def test_wrong_input():
    locations1 = [(40.111, 43, 41), (12, 43)]
    locations2 = [(40.111, -42), (12, 44)]

    try:
        gps.gps_match(locations1, locations2)
        assert(False)
    except:
        assert(True)

def test_wrong_input2():
    locations1 = [(40.111, 43), (12, 43)]
    locations2 = [(40.111, -42), (12, 44)]

    try:
        gps.gps_match(locations1, locations2)
        assert(False)
    except:
        assert(True)


def test_basic_distance():
    # Test same point
    result = gps.gps_match([[0, 0]], [[0, 0]])
    assert result[0][2] == 0  # Distance should be 0

    ny = [40.7128, -74.0060]
    boston = [42.3601, -71.0589]
    result = gps.gps_match([ny], [boston])
    assert 300 < result[0][2] < 310

def test_closest_match():
    point = [42.3601, -71.0589]  # Boston
    locations = [
        [40.7128, -74.0060],  # NYC
        [41.8781, -87.6298],  # Chicago
        [42.3601, -71.0589]   # Boston
    ]
    result = gps.gps_match([point], locations)
    assert result[0][1] == locations[2]  # Should match with Boston
    assert result[0][2] == 0  # Distance should be 0

# def false():
#     assert(False)




    