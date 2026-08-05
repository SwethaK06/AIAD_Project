import requests

# Endpoints (Local or Container Network)
OSRM_URL = "http://router.project-osrm.org/route/v1/driving"
ML_API_URL = "http://localhost:8000/predict"  # Update to container service name in K8s/Docker

def derive_traffic_condition(avg_speed_kmh: float) -> str:
    """Derives categorical traffic condition from OSRM average speed."""
    if avg_speed_kmh >= 50.0:
        return "Low"
    elif avg_speed_kmh >= 35.0:
        return "Normal"
    elif avg_speed_kmh >= 20.0:
        return "High"
    else:
        return "Severe Congestion"

def get_greenest_route(
    start_lon: float, 
    start_lat: float, 
    end_lon: float, 
    end_lat: float, 
    vehicle_type: str, 
    route_type: str, 
    package_weight_kg: float
):
    # 1. Fetch Candidate Routes from OSRM
    coordinates = f"{start_lon},{start_lat};{end_lon},{end_lat}"
    osrm_params = {
        "overview": "full",
        "geometries": "geojson",
        "alternatives": "true"
    }
    
    osrm_response = requests.get(f"{OSRM_URL}/{coordinates}", params=osrm_params)
    if osrm_response.status_code != 200:
        raise Exception("Failed to fetch routes from OSRM engine.")
        
    routes_data = osrm_response.json().get("routes", [])
    evaluated_routes = []

    # 2. Process each candidate route through the ML Model
    for idx, route in enumerate(routes_data):
        dist_km = route["distance"] / 1000.0
        duration_min = route["duration"] / 60.0
        avg_speed_kmh = dist_km / (duration_min / 60.0) if duration_min > 0 else 30.0
        
        traffic = derive_traffic_condition(avg_speed_kmh)
        
        # Payload for ML API
        ml_payload = {
            "vehicle_type": vehicle_type,
            "route_type": route_type,
            "traffic_conditions": traffic,
            "distance_km": round(dist_km, 2),
            "package_weight_kg": package_weight_kg
        }
        
        try:
            ml_res = requests.post(ML_API_URL, json=ml_payload).json()
            predicted_co2 = ml_res["predicted_co2_kgco2e"]
        except Exception:
            # Fallback if ML API is offline (Basic calculation)
            predicted_co2 = round(dist_km * 0.25, 2)
            
        evaluated_routes.append({
            "option_id": f"Route_{idx + 1}",
            "distance_km": round(dist_km, 2),
            "duration_min": round(duration_min, 1),
            "avg_speed_kmh": round(avg_speed_kmh, 1),
            "traffic_conditions": traffic,
            "predicted_co2_kgco2e": predicted_co2,
            "geometry": route["geometry"]
        })

    # 3. Sort by lowest emissions
    evaluated_routes.sort(key=lambda x: x["predicted_co2_kgco2e"])
    
    winning_route = evaluated_routes[0]
    return {
        "recommended_route": winning_route,
        "all_candidates": evaluated_routes
    }

# --- Test Execution ---
if __name__ == "__main__":
    # Test from Changi Airport -> Jurong West
    result = get_greenest_route(
        start_lon=103.9915, start_lat=1.3644,
        end_lon=103.6831, end_lat=1.3404,
        vehicle_type="Heavy Truck",
        route_type="Inter-City",
        package_weight_kg=1200.0
    )
    
    print("=== RECOMMENDED GREEN ROUTE ===")
    print(f"Option: {result['recommended_route']['option_id']}")
    print(f"Distance: {result['recommended_route']['distance_km']} km")
    print(f"Duration: {result['recommended_route']['duration_min']} mins")
    print(f"Predicted CO2: {result['recommended_route']['predicted_co2_kgco2e']} kgCO2e")