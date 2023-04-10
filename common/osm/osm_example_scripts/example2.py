import requests

# Replace <latitude> and <longitude> with the coordinates you want to search around
lat, lon = 37.969272, 23.720927

# Define the Nominatim Search API query to search for tourism spots within a 1km radius
nominatim_url = "https://nominatim.openstreetmap.org/search"
nominatim_params = {
    "format": "json",
    "lat": lat,
    "lon": lon,
    "radius": 10000,
}

# Send the query to the Nominatim Search API and parse the JSON response
response = requests.get(nominatim_url, params=nominatim_params)
data = response.json()

# Extract the names and locations of the nearest tourism spots
tourism_spots = []
for result in data:
    spot = {}
    spot["name"] = result.get("display_name", "Unknown")
    spot["lat"] = float(result["lat"])
    spot["lon"] = float(result["lon"])
    tourism_spots.append(spot)

# Print the list of nearest tourism spots
print(tourism_spots)
