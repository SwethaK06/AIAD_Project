import os
import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

try:
    from db_pr import get_db_connection
except ImportError:
    get_db_connection = None

app = FastAPI(title="Green Logistics Database Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory trip store fallback when PostgreSQL is offline during local testing
IN_MEMORY_TRIPS = []

class TripPayload(BaseModel):
    trip_id: str = Field(..., description="Unique trip identifier")
    origin: str = Field(..., description="Origin address or place name")
    destination: str = Field(..., description="Destination address or place name")
    origin_coords: str = Field(..., description="Origin coordinates 'lat,lng'")
    dest_coords: str = Field(..., description="Destination coordinates 'lat,lng'")
    vehicle_type: str = Field(..., description="Selected vehicle type")
    cargo_weight_kg: float = Field(..., gt=0, description="Cargo weight in kg")
    chosen_route_id: str = Field(..., description="ID of selected route option")
    actual_co2_kgco2e: Optional[float] = Field(None, description="Predicted or actual CO2 emission")
    distance_km: Optional[float] = Field(None, description="Trip distance in km")

@app.get("/health")
def health_check():
    db_online = False
    if get_db_connection is not None:
        try:
            conn = get_db_connection()
            conn.close()
            db_online = True
        except Exception:
            db_online = False

    return {
        "status": "healthy",
        "service": "database_service",
        "postgres_connected": db_online,
        "in_memory_trips_count": len(IN_MEMORY_TRIPS)
    }

@app.post("/api/v1/trips")
def log_trip(payload: TripPayload):
    """
    Logs confirmed trip into PostgreSQL 'trips' table, or in-memory fallback.
    """
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    trip_record = payload.dict()
    trip_record["timestamp"] = timestamp

    postgres_success = False
    if get_db_connection is not None:
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO trips (
                            trip_id, origin, destination, origin_coords, dest_coords,
                            vehicle_type, cargo_weight_kg, chosen_route_id, actual_co2_kgco2e, distance_km
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        payload.trip_id,
                        payload.origin,
                        payload.destination,
                        payload.origin_coords,
                        payload.dest_coords,
                        payload.vehicle_type,
                        payload.cargo_weight_kg,
                        payload.chosen_route_id,
                        payload.actual_co2_kgco2e,
                        payload.distance_km
                    ))
                    conn.commit()
                    postgres_success = True
        except Exception as e:
            print(f"[DB Service WARNING] PostgreSQL insert failed (using in-memory fallback): {e}")

    IN_MEMORY_TRIPS.append(trip_record)

    return {
        "status": "success",
        "message": "Trip record logged successfully.",
        "storage": "postgres" if postgres_success else "in_memory",
        "trip_id": payload.trip_id
    }

@app.get("/api/v1/trips")
def get_trips():
    """
    Retrieves logged trips from PostgreSQL or in-memory fallback.
    """
    if get_db_connection is not None:
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT trip_id, origin, destination, vehicle_type, cargo_weight_kg, chosen_route_id, actual_co2_kgco2e, distance_km, timestamp FROM trips ORDER BY timestamp DESC LIMIT 50")
                    rows = cur.fetchall()
                    trips = []
                    for r in rows:
                        trips.append({
                            "trip_id": r[0],
                            "origin": r[1],
                            "destination": r[2],
                            "vehicle_type": r[3],
                            "cargo_weight_kg": float(r[4]) if r[4] is not None else 0,
                            "chosen_route_id": r[5],
                            "actual_co2_kgco2e": float(r[6]) if r[6] is not None else 0,
                            "distance_km": float(r[7]) if r[7] is not None else 0,
                            "timestamp": str(r[8])
                        })
                    return {"status": "success", "source": "postgres", "trips": trips}
        except Exception as e:
            print(f"[DB Service WARNING] PostgreSQL fetch failed (using in-memory fallback): {e}")

    return {"status": "success", "source": "in_memory", "trips": list(reversed(IN_MEMORY_TRIPS))}
