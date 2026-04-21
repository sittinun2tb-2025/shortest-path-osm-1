# params.py
import os
import sys
from shapely import Point, LineString

dir_app = os.path.dirname(sys.argv[0])

start_p = Point(100.5044646, 13.7480028)
end_p = Point(100.5546609, 13.7410995)

centroid = LineString([start_p, end_p]).interpolate(0.5, normalized=True).coords[0]


# osmid start
osmid_u = 269740740
# osmid end
osmid_end = 2078129009

# Buffer distance (meters)
buffer_distance = 500

# 5933302261 -> 1856571595 -> 1637597374 -> 6154655536
# 2649275589 -> 2649275585 -> 13068408222 -> 1856571595 -> 5933302261
# 6154655536 -> 1637597374 -> 4588379141 -> 346610596 
# 269740740 -> 2078129009
# 5941680803 -> 2078129004 -> 5941680681 -> 2078129009 -> 2078129013
