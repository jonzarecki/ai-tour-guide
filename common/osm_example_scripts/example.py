import overpy

from common.nominatim_importance.importance_cache import importance_cache
from common.osm_example_scripts.osm_location import OSMLocation

# Replace <latitude> and <longitude> with the coordinates you want to search around
lat = 41.905965
lon = 12.482790

# Define the Overpass API query to filter for nodes with the "tourism" tag
api = overpy.Overpass()
result = api.query(
    f"""
    way(around:500,{lat},{lon});
    out;
"""
)
ways = [n for n in result.ways if len(n.tags) != 0]
result = api.query(
    f"""
    node(around:500,{lat},{lon});
    out;
"""
)
nodes = [n for n in result.nodes if len(n.tags) != 0]
objs = nodes + ways
locs = []
filters = {
    "road",
    "footway",
    "path",
    "highway",
    "shop",
    "barrier",
    "railway",
    "bus",
    "created_by",
    "emergency",
    "entrance",
    "restaurant",
    "abandoned:amenity",
    "diplomatic",
    "disused:amenity",
    "surveillance",
    "fixme",
}
for n in objs:
    if (
        len(n.tags) == 0
        or len(filters.intersection(n.tags)) > 0
        or n.tags.get("amenity", None)
        in [
            "fuel",
            "bicycle_parking",
            "car_sharing",
            "motorcycle_parking",
            "taxi",
            "bench",
            "atm",
            "restaurant",
            "cafe",
            "drinking_water",
            "bicycle_rental",
            "parking",
            "theatre",
            "bank",
            "post_office",
            "police",
            "cinema",
            "fast_food",
            "bar",
            "toilets",
            "ice_cream",
            "pharmacy",
            "railway",
        ]
        or n.tags.get("natural", None) == "tree"
        or n.tags.get("tourism", None) in ["hotel", "guest_house"]
        or not any("name" in t for t in n.tags)
    ) and "wikipedia" not in n.tags:
        continue
    lat, lon = round(float(n.lat), 4), round(float(n.lon), 4)
    wikidata = n.tags.get("wikidata", None)
    # if 'name' in n.tags:
    #     print(f"has name {'name' in n.tags} - ", end="")

    # print(f"{importance_dict[(n.lo)]}")
    cached_importance = importance_cache[n]

    # if loc.importance > 0.01 and round(loc.importance, 4) != cached_importance:
    #     print(loc)
    #     print(loc.importance, cached_importance)
    if cached_importance > 0.2:
        loc = OSMLocation.from_osm_id(n.id)
        if loc is None:
            print(f"Could not be found - {n.tags}")
            continue
        locs.append(loc)
        print(f"important - {n.tags}")
    else:
        pass
        # print(f"not important - {n.tags}")

print(sorted(locs, key=lambda l: l.importance, reverse=True))
# Extract the names and locations of the nearest tourism spots
tourism_spots = []
for node in result.nodes:
    spot = {}
    spot["name"] = node.tags.get("name", "Unknown")
    spot["lat"] = node.lat
    spot["lon"] = node.lon
    tourism_spots.append(spot)

# Print the list of nearest tourism spots
print(tourism_spots)
