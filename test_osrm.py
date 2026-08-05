import requests

# Public OSRM Demo Server Endpoint
OSRM_URL = "http://router.project-osrm.org/route/v1/driving"

# Coordinates: Changi Airport -> Jurong West
# Note: OSRM expects Longitude FIRST, then Latitude! (Lon, Lat)
start_lon, start_lat = [103.8499, 1.3798]
end_lon, end_lat = [103.9940, 1.3502]

# Build URL Request
coordinates = f"{start_lon},{start_lat};{end_lon},{end_lat}"
params = {
    "overview": "false",
    "alternatives": "true"  # Requests multiple route options
}

print("Fetching OSRM Routes for Singapore...")
response = requests.get(f"{OSRM_URL}/{coordinates}", params=params)

if response.status_code == 200:
    data = response.json()
    print(f"\nSuccess! Found {len(data['routes'])} routes across Singapore:\n")
    
    for idx, route in enumerate(data['routes']):
        dist_km = round(route['distance'] / 1000, 2)
        time_min = round(route['duration'] / 60, 1)
        avg_speed = round(dist_km / (time_min / 60), 1)
        
        print(f"🛣️  Route Choice #{idx + 1}:")
        print(f"    - Distance: {dist_km} km")
        print(f"    - Duration: {time_min} mins")
        print(f"    - Avg Speed: {avg_speed} km/h\n")
else:
    print("Failed to reach OSRM server.")