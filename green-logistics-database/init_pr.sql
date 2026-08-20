CREATE TABLE vehicles (
    vehicle_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    registration_number VARCHAR(20) UNIQUE NOT NULL,
    vehicle_type VARCHAR(50) NOT NULL,
    fuel_type VARCHAR(30) NOT NULL,
    vehicle_weight_kg DECIMAL(10, 2),
    maximum_load_kg DECIMAL(10, 2),
    status VARCHAR(30) DEFAULT 'Active',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE deliveries (
    delivery_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vehicle_id BIGINT NOT NULL,
    origin VARCHAR(255) NOT NULL,
    destination VARCHAR(255) NOT NULL,
    load_weight_kg DECIMAL(10, 2),
    delivery_status VARCHAR(30) DEFAULT 'Pending',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_delivery_vehicle
        FOREIGN KEY (vehicle_id)
        REFERENCES vehicles(vehicle_id)
        ON DELETE CASCADE
);

CREATE TABLE routes (
    route_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    delivery_id BIGINT NOT NULL,
    route_name VARCHAR(100),
    distance_km DECIMAL(10, 2) NOT NULL,
    estimated_duration_minutes DECIMAL(10, 2),
    traffic_level VARCHAR(30),
    road_type VARCHAR(50),
    is_recommended BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_route_delivery
        FOREIGN KEY (delivery_id)
        REFERENCES deliveries(delivery_id)
        ON DELETE CASCADE
);

CREATE TABLE traffic_data (
    traffic_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    route_id BIGINT NOT NULL,
    congestion_level VARCHAR(30),
    average_speed_kmh DECIMAL(8, 2),
    delay_minutes DECIMAL(8, 2),
    recorded_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_traffic_route
        FOREIGN KEY (route_id)
        REFERENCES routes(route_id)
        ON DELETE CASCADE
);

CREATE TABLE emission_predictions (
    prediction_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    route_id BIGINT NOT NULL,
    predicted_emission_g_km DECIMAL(12, 4) NOT NULL,
    predicted_total_emission_g DECIMAL(12, 4),
    model_name VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_prediction_route
        FOREIGN KEY (route_id)
        REFERENCES routes(route_id)
        ON DELETE CASCADE
);

CREATE TABLE vehicle_readings (
    reading_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vehicle_id BIGINT NOT NULL,
    speed_kmh DECIMAL(8, 2),
    fuel_consumption_litres DECIMAL(10, 3),
    actual_emission_g_km DECIMAL(12, 4),
    idling_duration_minutes DECIMAL(10, 2),
    engine_temperature_c DECIMAL(8, 2),
    recorded_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_reading_vehicle
        FOREIGN KEY (vehicle_id)
        REFERENCES vehicles(vehicle_id)
        ON DELETE CASCADE
);

CREATE TABLE maintenance_alerts (
    alert_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vehicle_id BIGINT NOT NULL,
    alert_type VARCHAR(100) NOT NULL,
    alert_description TEXT,
    severity VARCHAR(20),
    alert_status VARCHAR(30) DEFAULT 'Open',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_alert_vehicle
        FOREIGN KEY (vehicle_id)
        REFERENCES vehicles(vehicle_id)
        ON DELETE CASCADE
);

CREATE TABLE carbon_savings (
    saving_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    delivery_id BIGINT NOT NULL,
    original_emission_g DECIMAL(12, 4),
    optimised_emission_g DECIMAL(12, 4),
    emission_saved_g DECIMAL(12, 4),
    estimated_cost_saved DECIMAL(12, 2),
    calculated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_saving_delivery
        FOREIGN KEY (delivery_id)
        REFERENCES deliveries(delivery_id)
        ON DELETE CASCADE
);

-- Stores the route selected by the user from the UI
CREATE TABLE trips (
    trip_id VARCHAR(36) PRIMARY KEY,

    timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    origin VARCHAR(255) NOT NULL,
    destination VARCHAR(255) NOT NULL,

    origin_coords VARCHAR(100) NOT NULL,
    dest_coords VARCHAR(100) NOT NULL,

    vehicle_type VARCHAR(50) NOT NULL,
    cargo_weight_kg DECIMAL(10, 2) NOT NULL,

    chosen_route_id VARCHAR(50) NOT NULL,

    actual_co2_kgco2e DECIMAL(12, 4),
    distance_km DECIMAL(10, 2)
);

INSERT INTO vehicles (
    registration_number,
    vehicle_type,
    fuel_type,
    vehicle_weight_kg,
    maximum_load_kg
)
VALUES (
    'SGB1234A',
    'Delivery Van',
    'Diesel',
    1800,
    700
);