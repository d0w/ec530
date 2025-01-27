
# GPS Distance Module

To use GPS module to find the closet points of one array's coordinates to another array's and the corresponding distance in kilometers:
```
import gps

matches = gps_match(locations1, locations2)
# where locations1 and locations2 are arrays of GPS coordinates
# Returns list of lists [[point1 from locations1, closest point in locations2, distance in km], ...]
```

