-- Stores the route selected by the user from the UI
CREATE TABLE trips (
    trip_id VARCHAR(36) PRIMARY KEY,

    timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    origin VARCHAR(255) NOT NULL,
    destination VARCHAR(255) NOT NULL,

    geometry_polyline TEXT NOT NULL,

    origin_coords VARCHAR(100) NOT NULL,
    dest_coords VARCHAR(100) NOT NULL,

    vehicle_type VARCHAR(50) NOT NULL,
    cargo_weight_kg DECIMAL(10, 2) NOT NULL,

    recommended_route_id VARCHAR(50) NOT NULL,

    predicted_co2_kgco2e DECIMAL(12, 4),
    distance_km DECIMAL(10, 2),

    duration_minutes DECIMAL(10, 2)
);