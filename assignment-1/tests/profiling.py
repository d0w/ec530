import sys
sys.path.insert(0, '.')

import cProfile
import tracemalloc

import gps



def test_profiling():
    """Function to profile GPS matching performance"""
    locations1 = [(40.7128, -74.0060), (34.0522, -118.2437)] 
    locations2 = [(37.7749, -122.4194), (45.7128, -74.0060), (34.0522, -118.2437)] 
    return gps.gps_match(locations1, locations2)

def main():
    """Main profiling function"""
    tracemalloc.start()
    
    # Memory profiling
    test_profiling()
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory usage: {current / 10**6}MB")
    print(f"Peak memory usage: {peak / 10**6}MB")
    tracemalloc.stop()
    
    # CPU profiling
    profiler = cProfile.Profile()
    profiler.enable()
    test_profiling()
    profiler.disable()
    profiler.print_stats(sort='cumulative')

main()