import os
import uuid
import requests
from typing import List, Dict, Any, Optional
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Service URLs: Reads from environment variables (Docker Compose) or defaults to local host
ML_SERVICE_URL = os.getenv("ML_SERVICE_URL", "http://localhost:8000/predict")
OSRM_BASE_URL = os.getenv("OSRM_BASE_URL", "http://router.project-osrm.org")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/logistics_db")
STRICT_MODE = os.getenv("STRICT_MODE", "true").lower() == "true"

# Fallback Configuration
STRICT_MODE = os.getenv("STRICT_MODE", "true").lower() == "true"  # Set to True to reject fake fallback values

# Multi-Objective Scoring Weights (w_co2 + w_time MUST equal 1.0)
WEIGHT_PROFILES = {
    "green":    {"w_co2": 0.80, "w_time": 0.20},
    "fastest":  {"w_co2": 0.20, "w_time": 0.80},
    "balanced": {"w_co2": 0.50, "w_time": 0.50}
}


# =====================================================================
# 2. DATA CONTRACT SCHEMAS (JSON PAYLOAD DEFINITIONS)
# Standardized Pydantic models ensure strict input/output parsing 
# for frontend UI integration.
# =====================================================================

class Coordinates(BaseModel):
    lat: float = Field(..., example=1.3521, description="Latitude in decimal degrees")
    lng: float = Field(..., example=103.8198, description="Longitude in decimal degrees")
    address: Optional[str] = Field(None, description="Optional human-readable street address")


class RouteRequest(BaseModel):
    """Payload received from the Frontend UI."""
    origin: Coordinates
    destination: Coordinates
    cargo_weight_kg: float = Field(..., gt=0, description="Payload weight in kilograms")
    vehicle_type: str = Field(..., description="Vehicle category expected by ML model")
    priority_weight: Optional[str] = Field("balanced", description="Optimization goal: green, fastest, or balanced")


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


class OptimizationResponse(BaseModel):
    """Final output response returned to the Frontend UI."""
    status: str
    trip_id: str
    recommended_route_id: str
    routes: List[RouteOption]


# =====================================================================
# 3. HELPER & UTILITY FUNCTIONS
# =====================================================================

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


# =====================================================================
# 4. ROUTING ENGINE ENDPOINTS
# =====================================================================


@app.get("/")
def health_check():
    """Health check endpoint for Docker container orchestration."""
    return {"status": "healthy", "service": "routing_engine"}


@app.post("/api/v1/optimize-route", response_model=OptimizationResponse)
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
    )
    
    try:
        osrm_resp = requests.get(osrm_url, timeout=5.0)
        if osrm_resp.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"OSRM Routing service failed with status code {osrm_resp.status_code}"
            )
        osrm_data = osrm_resp.json()
        if "routes" not in osrm_data or len(osrm_data["routes"]) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No drivable routes found between specified origin and destination."
            )
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Routing service communication error: {str(e)}"
        )

    # Step 2: Parse raw OSRM candidates
    candidate_routes = []
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

    # Step 3: Query ML Model API for live prediction (NO FAKE FALLBACKS)
    evaluated_routes = []
    for candidate in candidate_routes:
        ml_payload = {
            "vehicle_type": req.vehicle_type,
            "traffic_conditions": candidate["traffic_level"], # Must match 'traffic_conditions' in app.py
            "distance_km": candidate["distance_km"],
            "package_weight_kg": req.cargo_weight_kg         # Must match 'package_weight_kg' in app.py
        }
        try:
            ml_resp = requests.post(ML_SERVICE_URL, json=ml_payload, timeout=3.0)
            
            if ml_resp.status_code != 200:
                # Log detailed failure to terminal stdout for debugging
                print(f"[ERROR] ML Service failed (HTTP {ml_resp.status_code}): {ml_resp.text}")
                
                if STRICT_MODE:
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=f"ML Prediction Engine returned HTTP {ml_resp.status_code}. Cannot provide verified CO2 calculation."
                    )
            
            prediction_data = ml_resp.json()
            predicted_co2 = prediction_data.get("predicted_co2_kgco2e")
            
            if predicted_co2 is None:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="ML Prediction Engine returned malformed response lacking 'predicted_co2_kgco2e' field."
                )

        except requests.exceptions.RequestException as e:
            print(f"[CRITICAL ERROR] Failed to connect to ML Service at {ML_SERVICE_URL}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Unable to reach Machine Learning backend service ({ML_SERVICE_URL}). Ensure ml_service container is running."
            )

        candidate["predicted_co2_kgco2e"] = round(float(predicted_co2), 3)
        evaluated_routes.append(candidate)

    # Step 4: Multi-objective normalization and scoring
    max_time = max(r["duration_mins"] for r in evaluated_routes) or 1.0
    max_co2 = max(r["predicted_co2_kgco2e"] for r in evaluated_routes) or 1.0

    for route in evaluated_routes:
        route["cost_score"] = calculate_cost_score(
            duration_mins=route["duration_mins"],
            co2_kg=route["predicted_co2_kgco2e"],
            priority=req.priority_weight,
            max_duration=max_time,
            max_co2=max_co2
        )

    # Sort candidates by cost_score ascending (lowest penalty wins)
    ranked_routes = sorted(evaluated_routes, key=lambda x: x["cost_score"])

    # Step 5: Format response for Frontend UI integration
    formatted_options = []
    for idx, route in enumerate(ranked_routes):
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

    return OptimizationResponse(
        status="success",
        trip_id=f"TRIP-OPT-{uuid.uuid4().hex[:8].upper()}",
        recommended_route_id=formatted_options[0].route_id,
        routes=formatted_options
    )