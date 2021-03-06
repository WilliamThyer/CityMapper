# CityMapper

By William Thyer
Using OSMnx in Python to visualize and quantify bikeability of cities.

[Click to enlarge figure](examples/best_worst_cities.pdf)  
<img src="examples/best_worst_cities.png" alt="drawing" width="600"/>

## Files

**network_functions.py:**  
Contains useful functions that notebooks call. Mostly wrappers for OSMnx and Matplotlib functions.  
**bike_networks.ipynb:**  
Main notebook for creating a map of cycleways and public roads in any given city. If you want to make a map, this is the file to look at!  
**best_worst_major_cities.ipynb:**  
Goes through top 30 cities and creates a cycleway map. Used to find best and worst cities for bike infrastructure.

## [More Example Maps](examples/pdf/)

<img src="examples/png/Chicago,&#32;IL.png" alt="drawing" height="300"/> <img src="examples/png/Austin,&#32;TX.png" alt="drawing" height="300"/> <img src="examples/png/Dallas,&#32;TX.png" alt="drawing" height="300"/> <img src="examples/png/New&#32;York&#32;City,&#32;NY.png" alt="drawing" height="300"/>

## Resources

[OSMnx Docs](https://osmnx.readthedocs.io/en/stable/)  
[Really nice tutorial](https://geoffboeing.com/2016/11/osmnx-python-street-networks/)  
[OSMnx examples Github](https://github.com/gboeing/osmnx-examples)  
[Useful thread related to cycleways](https://github.com/gboeing/osmnx/issues/151)  
[Other tutorial](https://automating-gis-processes.github.io/CSC/notebooks/L3/retrieve_osm_data.html)  
[Water thread](https://stackoverflow.com/questions/62285134/how-to-fill-water-bodies-with-osmnx-in-python)  
[Map polygon intersection thread](https://stackoverflow.com/questions/66391717/osmnx-how-to-make-sure-we-do-not-plot-outside-of-polygon)  
[Urban walkabililty](https://www.gispo.fi/en/blog/analysing-urban-walkability-using-openstreetmap-and-python/)
