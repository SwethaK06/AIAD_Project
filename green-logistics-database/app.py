import os
import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

try:
    from db import get_db_connection #trying to import the database connection function from db.py
except ImportError:
    try:
        from db_pr import get_db_connection #but if that fails, try to import from db_pr.py
    except ImportError:
        get_db_connection = None

app = FastAPI(title="Green Logistics Database Service", version="1.0.0") #creates FastAPI application with name + version, FastAPI acts as a communication layer between the ui and database 

app.add_middleware( #allows ui (which is on another port) to acccess the database service 
    CORSMiddleware,
    allow_origins=["*"],  #allow requests from any origin
    allow_credentials=True, #allow credentials
    allow_methods=["*"], #allow all HTTP methods
    allow_headers=["*"], #allow all request headers
)

# In-memory trip store fallback when PostgreSQL is offline during local testing
IN_MEMORY_TRIPS = []

class TripPayload(BaseModel): #TripPayload class defines the structure of the trip data that will be sent to the API. 
    trip_id: str = Field(..., description="Unique trip identifier") #Trip ID must be string and is a required field 

    origin: str = Field( #origin must be string and is a required field
        ...,
        description="Origin address or place name"
    )

    destination: str = Field( #destination must be string and is a required field
        ...,
        description="Destination address or place name"
    )

    geometry_polyline: Optional[str] = Field( #geometry_polyline must be string and is an optional field - stores the route shape for displaying the trip on a map
        "",
        description="Encoded route geometry polyline"
    )

    origin_coords: str = Field( #origin_coords must be string and is a required field
        ...,
        description="Origin coordinates 'lat,lng'"
    )

    dest_coords: str = Field( #dest_coords must be string and is a required field
        ...,
        description="Destination coordinates 'lat,lng'"
    )

    vehicle_type: str = Field( #vehicle_type must be string and is a required field
        ...,
        description="Selected vehicle type"
    )

    cargo_weight_kg: float = Field( #cargo_weight_kg must be a positive float and is a required field
        ...,
        gt=0,
        description="Cargo weight in kg"
    )

    route_priority: Optional[str] = Field( #route_priority must be string and is an optional field - indicates the optimization goal for the route
        "green",
        description="Optimization goal / route priority: green, fastest, or balanced"
    )

    recommended_route_id: Optional[str] = Field( #recommended_route_id must be string and is an optional field - stores the ID of the recommended route
        None,
        description="ID of the recommended route"
    )

    chosen_route_id: Optional[str] = Field( #chosen_route_id must be string and is an optional field - stores the ID of the chosen route
        None,
        description="Alias for recommended route ID"
    )

    predicted_co2_kgco2e: Optional[float] = Field( #predicted_co2_kgco2e must be a float and is an optional field - stores the predicted CO2 emissions for the trip
        None,
        description="Predicted CO2 emissions"
    )

    actual_co2_kgco2e: Optional[float] = Field( #actual_co2_kgco2e must be a float and is an optional field - stores the actual CO2 emissions for the trip
        None,
        description="Alias for predicted CO2 emissions"
    )

    distance_km: Optional[float] = Field( #distance_km must be a float and is an optional field - stores the distance of the trip in kilometers
        None,
        description="Trip distance in km"
    )

    duration_minutes: Optional[float] = Field( #duration_minutes must be a float and is an optional field - stores the duration of the trip in minutes
        None,
        description="Trip duration in minutes"
    )

@app.get("/health")
def health_check(): #checks if the database is running and returns status - either online or offline 
    db_online = False #assuming the PostgreSQL database is offline
    if get_db_connection is not None:
        try:
            conn = get_db_connection() #try to open a connection
            conn.close()  #close the connection as its only a connection test
            db_online = True #if no error occurred - the database is reachable
        except Exception:
            db_online = False #if the connection fails - the database as offline

    return { #returns the current health information
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
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat() #records the current UTC date and time and stores it as a timestamp for the trip

    #takes incoming trip data and sets fault values for null values - ensure trip record is complete before storing in database 
    rec_route_id = payload.recommended_route_id or payload.chosen_route_id or "N/A" #if there is no recommended route id or chosen route id - set the value to "N/A"
    pred_co2 = payload.predicted_co2_kgco2e if payload.predicted_co2_kgco2e is not None else (payload.actual_co2_kgco2e if payload.actual_co2_kgco2e is not None else 0.0) #if there are no predicted or actual CO2 emissions - set the value to 0.0    
    geom_poly = payload.geometry_polyline or "" #if there is no geometry polyline - set the value to an empty string
    dur_mins = payload.duration_minutes #take the duration value directly from the trip data
    priority = payload.route_priority or "green" #if there is no route priority - set the value to "green"

    trip_record = payload.dict() #this creates a copy of all the trip data
    trip_record["recommended_route_id"] = rec_route_id #set the final recommended route ID
    trip_record["chosen_route_id"] = rec_route_id #set chosen_route_id to the same final route ID
    trip_record["predicted_co2_kgco2e"] = pred_co2 #set the final predicted CO2 emissions
    trip_record["actual_co2_kgco2e"] = pred_co2 #set the final actual CO2 emissions
    trip_record["geometry_polyline"] = geom_poly #set the final geometry polyline
    trip_record["route_priority"] = priority #set the final route priority
    trip_record["timestamp"] = timestamp #set the final timestamp

    postgres_success = False #start by assuming that saving to database has not worked yet
    if get_db_connection is not None: #if the database connection is available 
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    #run an SQL command to insert the trip into the 'trips' table
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
                            route_priority,
                            recommended_route_id,
                            predicted_co2_kgco2e,
                            distance_km,
                            duration_minutes
                        ) #placeholders for the values to be inserted into the database
                        VALUES ( 
                            %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s
                        ) #if trip ID already exists in the database - it will update the existing record instead of creating duplicate 
                        ON CONFLICT (trip_id) DO UPDATE SET 
                            origin = EXCLUDED.origin,
                            destination = EXCLUDED.destination,
                            geometry_polyline = EXCLUDED.geometry_polyline,
                            origin_coords = EXCLUDED.origin_coords,
                            dest_coords = EXCLUDED.dest_coords,
                            vehicle_type = EXCLUDED.vehicle_type,
                            cargo_weight_kg = EXCLUDED.cargo_weight_kg,
                            route_priority = EXCLUDED.route_priority,
                            recommended_route_id = EXCLUDED.recommended_route_id,
                            predicted_co2_kgco2e = EXCLUDED.predicted_co2_kgco2e,
                            distance_km = EXCLUDED.distance_km,
                            duration_minutes = EXCLUDED.duration_minutes,
                            timestamp = CURRENT_TIMESTAMP
                    """, (#the values to be inserted into the database
                        payload.trip_id,
                        payload.origin,
                        payload.destination,
                        geom_poly,
                        payload.origin_coords,
                        payload.dest_coords,
                        payload.vehicle_type,
                        payload.cargo_weight_kg,
                        priority,
                        rec_route_id,
                        pred_co2,
                        payload.distance_km,
                        dur_mins
                    ))
                    conn.commit()#saving the changes 
                    postgres_success = True
        except Exception as e:
            print(f"[DB Service WARNING] PostgreSQL insert failed (using in-memory fallback): {e}") #catches any errors, which is then printed for debugging - the trip details is stored in the in-memory fallback instead of the database

    IN_MEMORY_TRIPS.append(trip_record) #even if the database insert fails, the trip record is still stored in the in-memory fallback for local testing

    return {#returns a response to the UI indicating that the trip record has been logged successfully - whether it was stored in PostgreSQL or in-memory fallback   
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
                    cur.execute("SELECT trip_id, origin, destination, vehicle_type, cargo_weight_kg, route_priority, recommended_route_id, predicted_co2_kgco2e, distance_km, timestamp FROM trips ORDER BY timestamp DESC LIMIT 50") #fetches the last 50 trips from the database, ordered by timestamp in descending order
                    rows = cur.fetchall() #fetches all the rows returned by the SQL query and stores them in the variable 'rows'
                    trips = []  #create an empty list to store the trip data
                    for r in rows:
                        trips.append({ #turn each database row into a dictionary
                            "trip_id": r[0],
                            "origin": r[1],
                            "destination": r[2],
                            "vehicle_type": r[3],
                            "cargo_weight_kg": float(r[4]) if r[4] is not None else 0,
                            "route_priority": r[5] or "green",
                            "recommended_route_id": r[6],
                            "chosen_route_id": r[6],
                            "predicted_co2_kgco2e": float(r[7]) if r[7] is not None else 0,
                            "actual_co2_kgco2e": float(r[7]) if r[7] is not None else 0,
                            "distance_km": float(r[8]) if r[8] is not None else 0,
                            "timestamp": str(r[9])
                        })
                    return {"status": "success", "source": "postgres", "trips": trips} #send the trips back to the frontend
        except Exception as e:
            print(f"[DB Service WARNING] PostgreSQL fetch failed (using in-memory fallback): {e}") 

    return {"status": "success", "source": "in_memory", "trips": list(reversed(IN_MEMORY_TRIPS))} #if PostgreSQL failed, return trips details back to frontend from in-memory 
