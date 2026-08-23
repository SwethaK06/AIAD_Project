import os
import uuid
import requests
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional

# Load central root .env file if present
root_env = Path(__file__).resolve().parent.parent / ".env"
if root_env.exists():
    load_dotenv(dotenv_path=root_env, override=False)
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

# =====================================================================
# 1. MODULAR CONFIGURATION BLOCK
# Centralized settings allow teammates to modify parameters, URLs, 
# and weights without modifying core engine logic.
# =====================================================================
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Routing Service",
    description="Multi-objective route optimization engine integrated with carbon prediction ML models.",
    version="1.0.0"
)

# CORs middleware to allow cross-origin requests from frontend application (allows communication between frontend and backend without getting HTTP 405)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs & DB Connection purposes: Reads strictly from environment variables so it can switch between localhost and containerised deployments.
# Service URLs & DB Connection: Reads strictly from environment variables (.env / Docker Compose)
ML_SERVICE_URL = os.getenv("ML_SERVICE_URL")
OSRM_BASE_URL = os.getenv("OSRM_BASE_URL")
DATABASE_URL = os.getenv("DATABASE_URL")
STRICT_MODE = os.getenv("STRICT_MODE", "true").lower() == "true"

# Multi-Objective Weight profiles for optimisating the score.
# Multi-Objective Scoring Weights (w_co2 + w_time MUST equal 1.0)
WEIGHT_PROFILES = {
    "green":    {"w_co2": 0.80, "w_time": 0.20},
    "fastest":  {"w_co2": 0.20, "w_time": 0.80},
    "balanced": {"w_co2": 0.50, "w_time": 0.50}
}


# 2. DATA CONTRACT SCHEMAS (JSON PAYLOAD DEFINITIONS)
# Standardized Pydantic models that ensures strict input/output parsing  or frontend UI integration.

class Coordinates(BaseModel):
    lat: float = Field(..., example=1.3521, description="Latitude in decimal degrees")
    lng: float = Field(..., example=103.8198, description="Longitude in decimal degrees")
    address: Optional[str] = Field(None, description="Optional human-readable street address")
    #  All the fields are required except for address, which is optional. The example values are provided for clarity and testing purposes.


class RouteRequest(BaseModel):
    """Payload received from the Frontend UI."""
    origin: Coordinates
    destination: Coordinates
    cargo_weight_kg: float = Field(..., gt=0, description="Payload weight in kilograms")
    vehicle_type: str = Field(..., description="Vehicle category expected by ML model")
    priority_weight: Optional[str] = Field("balanced", description="Optimization goal: green, fastest, or balanced")
    
    # The priority_weight field is optional and defaults to "balanced" if not provided. 
    # It allows the user to specify their preference for route optimization, whether they prioritize lower carbon emissions (green), faster travel time (fastest), or a balanced approach between the two.


class RouteOption(BaseModel):
    """Single candidate route output for UI display."""
    route_id: str
    tag: str
    distance_km: float
    duration_mins: float
    predicted_co2_kgco2e: float
    traffic_level: str
    cost_score: float
    geometry_polyline: str
    
    # The RouteOption model defines the structure of each route option returned to the frontend.
    # It includes the route's unique identifier, a descriptive tag, distance, duration, predicted CO2 emissions, traffic level, cost score, and the polyline geometry for mapping purposes.



class OptimizationResponse(BaseModel):
    """Final output response returned to the Frontend UI."""
    status: str
    trip_id: str
    recommended_route_id: str
    routes: List[RouteOption]
    
    # The OptimizationResponse model encapsulates the overall response sent back to the frontend after route optimization (after evaluating multiple route options connected to the ML model).
    # It includes a status message, a unique trip identifier, the ID of the recommended route, and a list of all evaluated route options, each represented by the RouteOption model.



# 3. HELPER & UTILITY FUNCTIONS


def calculate_traffic_level(distance_km: float, duration_mins: float) -> str:
    """
    Estimates traffic density by computing average speed across segment.
    """
    if duration_mins <= 0:
        return "Normal"
        
    avg_speed_kmh = distance_km / (duration_mins / 60.0)
    
    if avg_speed_kmh < 25.0:
        return "High"
    elif avg_speed_kmh < 50.0:
        return "Normal"
    else:
        return "Low"
    
    # The calculate_traffic_level function estimates traffic density based on the average speed calculated from the distance and duration of a route segment.
    # It returns a string indicating the traffic level: "High" for slow speeds, 
    # "Normal" for moderate speeds, and 
    # "Low" for fast speeds. 
    # This information is used to inform the ML model about traffic conditions when predicting CO2 emissions.


def calculate_cost_score(
    duration_mins: float, 
    co2_kg: float, 
    priority: str, 
    max_duration: float, 
    max_co2: float
) -> float:
    """
    Computes normalized multi-objective penalty score based on user preference.
    Lower score indicates a better route matching user criteria.
    """
    weights = WEIGHT_PROFILES.get(priority.lower(), WEIGHT_PROFILES["balanced"])
    
    # Scale variables between 0.0 and 1.0 relative to route maxes
    norm_co2 = co2_kg / max_co2 if max_co2 > 0 else 0.0
    norm_time = duration_mins / max_duration if max_duration > 0 else 0.0
    
    score = (weights["w_co2"] * norm_co2) + (weights["w_time"] * norm_time)
    return round(score, 4)

    # The calculate_cost_score function computes a normalized penalty score for a given route based on its predicted CO2 emissions and travel duration, weighted according to the user's specified priority (green, fastest, or balanced).
    # It normalizes the CO2 and time values relative to the maximum observed values across all candidate routes, applies the appropriate weights, and returns a final score.
    # Why Normalisation is because travel duration + CO2 emissions use completely different measurements cales.
    #   Normalising both values between 0.0 and 1.0 allows for a fair comparison and combination of these two objectives into a single cost score, enabling effective multi-objective optimization.
    # Lower score = better route to take.



# 4. ROUTING ENGINE ENDPOINTS

# Health check endpoint for Docker container orchestration - for example if the endpoint is actually being used in a Kubernetes cluster, the health check endpoint can be used to determine if the container is running and healthy. 
# If the health check fails, the container can be restarted or replaced automatically by the orchestration system.


@app.get("/")
@app.get("/health")
def health_check():
    """Health check endpoint for Docker container orchestration."""
    return {"status": "healthy", "service": "routing_engine"}


@app.post("/api/v1/optimize-route", response_model=OptimizationResponse)
# The /api/v1/optimize-route endpoint is the main entry point for the routing engine. 
# It accepts a POST request with a JSON payload containing the origin and destination coordinates, cargo weight, vehicle type, and optimization priority. 
# The endpoint processes the request through these steps:

def optimize_route(req: RouteRequest):
    """
    Main pipeline:
    1. Queries OSRM for route alternatives & spatial geometries.
    2. Sends path attributes to Machine Learning model for CO2 inference.
    3. Normalizes and ranks route options using penalty cost function.
    4. Returns JSON payload optimized for direct UI rendering.
    """
    
    # Step 1: Query OSRM for spatial route alternatives
    osrm_url = (
        f"{OSRM_BASE_URL}/route/v1/driving/"
        f"{req.origin.lng},{req.origin.lat};{req.destination.lng},{req.destination.lat}"
        f"?alternatives=true&overview=full&geometries=polyline"
        # The OSRM query URL is constructed using the origin and destination coordinates provided in the request payload.
        # The query requests driving routes, allows for alternative routes, requests a full overview of the route geometry, and specifies that the geometry should be returned in polyline format.
    )
    
    try:
        # Then following that;
        # The routing engine sends a GET request to the OSRM service using the constructed URL.
        osrm_resp = requests.get(osrm_url, timeout=5.0) # timeout of 5 seconds to avoid long waits if OSRM cannot respond.
        if osrm_resp.status_code != 200:
            # raise an http exception if the OSRM service does not return a successful response (200). 
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"OSRM Routing service failed with status code {osrm_resp.status_code}"
            )
            
        # The response from the OSRM service is expected to be in JSON format. The routing engine attempts to parse this JSON response.
        osrm_data = osrm_resp.json()
        
        # If the parsed data does not contain any routes, or if the routes list is empty, the routing engine raises an HTTP 404 Not Found exception, indicating that no drivable routes were found between the specified origin and destination.
        
        if "routes" not in osrm_data or len(osrm_data["routes"]) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No drivable routes found between specified origin and destination."
            )
            
        # If the OSRM service returns a successful response with valid route data, the routing engine proceeds to the next steps of processing the routes, sending them to the ML model for CO2 prediction, and ranking them based on the multi-objective cost function.
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Routing service communication error: {str(e)}"
        )

    # Parse raw OSRM candidates
    candidate_routes = []
    # The routing engine iterates over each route returned by the OSRM service. Each route's distance and duration are extracted and converted to km and mins, then the traffic level is calculated with the helper function.
    # Then, each potential route is stored in a dictionary containing the parameters
    
    for idx, r_data in enumerate(osrm_data["routes"]):
        dist_km = round(r_data["distance"] / 1000.0, 2)
        dur_mins = round(r_data["duration"] / 60.0, 2)
        traffic = calculate_traffic_level(dist_km, dur_mins)
        
        candidate_routes.append({
            "route_id": f"route_{idx + 1}",
            "distance_km": dist_km,
            "duration_mins": dur_mins,
            "traffic_level": traffic,
            "geometry_polyline": r_data["geometry"]
        })
    
    # Querying ML Model API for live prediction

    # The routing engine then prepares to send each potential route's attributes to the ML service for CO2 emission prediction.
    # It constructs a payload for each route:

    evaluated_routes = []
    
    for candidate in candidate_routes:
        ml_payload = {
            "vehicle_type": req.vehicle_type,
            "traffic_conditions": candidate["traffic_level"], # Must match 'traffic_conditions' in app.py
            "distance_km": candidate["distance_km"],
            "package_weight_kg": req.cargo_weight_kg         # Must match 'package_weight_kg' in app.py
        }
        try:
            
            # The routing engine sends 1 POST request to the ML service with the constructed payload for each candidate route. 
            # It handles potential errors, such as connection issues or unexpected responses, and raises appropriate HTTP exceptions if necessary. 
            # If the ML service returns a valid prediction, the predicted CO2 emissions are added to the candidate route's data for further evaluation and scoring.

            ml_resp = requests.post(ML_SERVICE_URL, json=ml_payload, timeout=3.0)
            
            if ml_resp.status_code != 200:
                # Log detailed failure to terminal stdout for debugging
                print(f"[ERROR] ML Service failed (HTTP {ml_resp.status_code}): {ml_resp.text}")
                
                if STRICT_MODE:
                    # Strict mode means that if the ML service fails, the engine will not return any routes
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=f"ML Prediction Engine returned HTTP {ml_resp.status_code}. Cannot provide verified CO2 calculation."
                    )
            
            prediction_data = ml_resp.json()
            predicted_co2 = prediction_data.get("predicted_co2_kgco2e")
            # Routing engine attempts to parse the JSON response and extract the predicted CO2 emissions.
            # If there is an error, then the a HTTP Exception is raised.
            
            if predicted_co2 is None:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="ML Prediction Engine returned malformed response lacking 'predicted_co2_kgco2e' field."
                )

        except requests.exceptions.RequestException as e:
            # Raises an HTTP 503 Service Unavailable exception if ML service is down, indicating that the ML backend service is not reachable.
            print(f"[CRITICAL ERROR] Failed to connect to ML Service at {ML_SERVICE_URL}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Unable to reach Machine Learning backend service ({ML_SERVICE_URL}). Ensure ml_service container is running."
            )

        candidate["predicted_co2_kgco2e"] = round(float(predicted_co2), 3)
        # The predicted CO2 emissions are rounded to three decimal places and added to the candidate route's data. 
        evaluated_routes.append(candidate)
        # results are appended to evaluated_routes.

    # Multi-objective normalization and scoring
    max_time = max(r["duration_mins"] for r in evaluated_routes) or 1.0
    max_co2 = max(r["predicted_co2_kgco2e"] for r in evaluated_routes) or 1.0
    # The routing engine calculates the maximum duration and maximum predicted CO2 emissions across all evaluated routes.
    # These  values are used to normalize each route's duration and CO2 emissions when calculating the multi-objective cost score, ensuring that the scores are comparable across different routes.

    for route in evaluated_routes:
        # iterate over each evaluated route and calculates a cost score using the calculate_cost_score function.
        route["cost_score"] = calculate_cost_score(
            duration_mins=route["duration_mins"],
            co2_kg=route["predicted_co2_kgco2e"],
            priority=req.priority_weight,
            max_duration=max_time,
            max_co2=max_co2
        )
        # lower cost score indicates a better route that aligns with the user's specified priority (like green, fastest, or balacned)

    # Sort candidates by cost_score ascending (lowest penalty wins)
    ranked_routes = sorted(evaluated_routes, key=lambda x: x["cost_score"])

    #Format response for Frontend UI integration
    formatted_options = []
    for idx, route in enumerate(ranked_routes):
        # The routing engine formats the ranked routes into a list of RouteOption objects for the final response.
        # The first route in the ranked list is tagged as "Recommended", subsequent routes are tagged as "Alternative Option".
        
        if idx == 0:
            tag = f"Recommended ({req.priority_weight.capitalize()} Choice)"
        else:
            tag = "Alternative Option"

        formatted_options.append(RouteOption(
            route_id=route["route_id"],
            tag=tag,
            distance_km=route["distance_km"],
            duration_mins=route["duration_mins"],
            predicted_co2_kgco2e=route["predicted_co2_kgco2e"],
            traffic_level=route["traffic_level"],
            cost_score=route["cost_score"],
            geometry_polyline=route["geometry_polyline"]
        ))
        # all routeoption objects are appended to formatted_options list. 

    return OptimizationResponse(
        status="success",
        trip_id=f"TRIP-OPT-{uuid.uuid4().hex[:8].upper()}",
        recommended_route_id=formatted_options[0].route_id,
        routes=formatted_options
    )

# OptimizationResponse object. So now the frontend can see the recommended route + all alternative routes with details.