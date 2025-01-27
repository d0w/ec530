import sys
sys.path.insert(0, '..')

from assignment1 import gps



def test_haversine():
    assert(round(gps.haversine(40.7, -74.0, 37.7, -122.4), 1) == 4131.1)

def test_gps_match():
    locations1 = [(40.7128, -74.0060), (34.0522, -118.2437)]
    locations2 = [(37.7749, -122.4194), (40.7128, -74.0060), (34.0522, -118.2437)]

    matches = gps.gps_match(locations1, locations2)

    assert(matches == [(locations1[0], locations2[1], 4131.1), (locations1[1], locations2[2], 0.0)])

def test_wrong_input():
    locations1 = [(40.111, 43, 41), (12, 43)]
    locations2 = [(40.111, -42), (12, 44)]

    try:
        gps.gps_match(locations1, locations2)
        assert(False)
    except:
        assert(True)

# def false():
#     assert(False)




    