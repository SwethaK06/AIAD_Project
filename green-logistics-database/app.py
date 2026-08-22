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

    origin: str = Field(
        ...,
        description="Origin address or place name"
    )

    destination: str = Field(
        ...,
        description="Destination address or place name"
    )

    geometry_polyline: Optional[str] = Field(
        "",
        description="Encoded route geometry polyline"
    )

    origin_coords: str = Field(
        ...,
        description="Origin coordinates 'lat,lng'"
    )

    dest_coords: str = Field(
        ...,
        description="Destination coordinates 'lat,lng'"
    )

    vehicle_type: str = Field(
        ...,
        description="Selected vehicle type"
    )

    cargo_weight_kg: float = Field(
        ...,
        gt=0,
        description="Cargo weight in kg"
    )

    recommended_route_id: Optional[str] = Field(
        None,
        description="ID of the recommended route"
    )

    chosen_route_id: Optional[str] = Field(
        None,
        description="Alias for recommended route ID"
    )

    predicted_co2_kgco2e: Optional[float] = Field(
        None,
        description="Predicted CO2 emissions"
    )

    actual_co2_kgco2e: Optional[float] = Field(
        None,
        description="Alias for predicted CO2 emissions"
    )

    distance_km: Optional[float] = Field(
        None,
        description="Trip distance in km"
    )

    duration_minutes: Optional[float] = Field(
        None,
        description="Trip duration in minutes"
    )

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

    rec_route_id = payload.recommended_route_id or payload.chosen_route_id or "N/A"
    pred_co2 = payload.predicted_co2_kgco2e if payload.predicted_co2_kgco2e is not None else (payload.actual_co2_kgco2e if payload.actual_co2_kgco2e is not None else 0.0)
    geom_poly = payload.geometry_polyline or ""
    dur_mins = payload.duration_minutes

    trip_record = payload.dict()
    trip_record["recommended_route_id"] = rec_route_id
    trip_record["chosen_route_id"] = rec_route_id
    trip_record["predicted_co2_kgco2e"] = pred_co2
    trip_record["actual_co2_kgco2e"] = pred_co2
    trip_record["geometry_polyline"] = geom_poly
    trip_record["timestamp"] = timestamp

    postgres_success = False
    if get_db_connection is not None:
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO trips (
                            trip_id,
                            origin,
                            destination,
                            geometry_polyline,
                            origin_coords,
                            dest_coords,
                            vehicle_type,
                            cargo_weight_kg,
                            recommended_route_id,
                            predicted_co2_kgco2e,
                            distance_km,
                            duration_minutes
                        )
                        VALUES (
                            %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s
                        )
                        ON CONFLICT (trip_id) DO UPDATE SET
                            origin = EXCLUDED.origin,
                            destination = EXCLUDED.destination,
                            geometry_polyline = EXCLUDED.geometry_polyline,
                            origin_coords = EXCLUDED.origin_coords,
                            dest_coords = EXCLUDED.dest_coords,
                            vehicle_type = EXCLUDED.vehicle_type,
                            cargo_weight_kg = EXCLUDED.cargo_weight_kg,
                            recommended_route_id = EXCLUDED.recommended_route_id,
                            predicted_co2_kgco2e = EXCLUDED.predicted_co2_kgco2e,
                            distance_km = EXCLUDED.distance_km,
                            duration_minutes = EXCLUDED.duration_minutes,
                            timestamp = CURRENT_TIMESTAMP
                    """, (
                        payload.trip_id,
                        payload.origin,
                        payload.destination,
                        geom_poly,
                        payload.origin_coords,
                        payload.dest_coords,
                        payload.vehicle_type,
                        payload.cargo_weight_kg,
                        rec_route_id,
                        pred_co2,
                        payload.distance_km,
                        dur_mins
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
                    cur.execute("SELECT trip_id, origin, destination, vehicle_type, cargo_weight_kg, recommended_route_id, predicted_co2_kgco2e, distance_km, timestamp FROM trips ORDER BY timestamp DESC LIMIT 50")
                    rows = cur.fetchall()
                    trips = []
                    for r in rows:
                        trips.append({
                            "trip_id": r[0],
                            "origin": r[1],
                            "destination": r[2],
                            "vehicle_type": r[3],
                            "cargo_weight_kg": float(r[4]) if r[4] is not None else 0,
                            "recommended_route_id": r[5],
                            "chosen_route_id": r[5],
                            "predicted_co2_kgco2e": float(r[6]) if r[6] is not None else 0,
                            "actual_co2_kgco2e": float(r[6]) if r[6] is not None else 0,
                            "distance_km": float(r[7]) if r[7] is not None else 0,
                            "timestamp": str(r[8])
                        })
                    return {"status": "success", "source": "postgres", "trips": trips}
        except Exception as e:
            print(f"[DB Service WARNING] PostgreSQL fetch failed (using in-memory fallback): {e}")

    return {"status": "success", "source": "in_memory", "trips": list(reversed(IN_MEMORY_TRIPS))}
