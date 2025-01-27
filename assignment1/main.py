# import gps

# def main():
#     locations1 = [(40.7128, -74.0060), (34.0522, -118.2437)]
#     locations2 = [(37.7749, -122.4194), (40.7128, -74.0060), (34.0522, -118.2437)]

#     matches = gps.gps_match(locations1, locations2)

#     for match in matches:
#         print(f"Point 1: {match[0]}, Point 2: {match[1]}, Distance: {match[2]}")


# def test():
#     assert(round(gps.haversine(40.7, -74.0, 37.7, -122.4), 1) == 4131.1)

# if __name__ == "__main__":
#     main()