# app.py - ML Microservice
from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd

app = FastAPI(title="Carbon Emission Prediction API")

# Load pre-trained model pipeline
MODEL_PATH = "carbon_model.pkl"
pipeline = joblib.load(MODEL_PATH)

class PredictionInput(BaseModel):
    vehicle_type: str        # e.g., "Heavy Truck", "Diesel Van (Euro 6)"
    route_type: str          # e.g., "Inter-City", "Urban Last Mile"
    traffic_conditions: str  # e.g., "Low", "Normal", "High", "Severe Congestion"
    distance_km: float       # e.g., 38.4
    package_weight_kg: float # e.g., 850.0

@app.post("/predict")
def predict_emissions(data: PredictionInput):
    # Convert incoming request to DataFrame
    input_data = pd.DataFrame([{
        "vehicle_type": data.vehicle_type,
        "route_type": data.route_type,
        "traffic_conditions": data.traffic_conditions,
        "distance_km": data.distance_km,
        "package_weight_kg": data.package_weight_kg
    }])
    
    # Predict carbon output (kgCO2e)
    prediction = pipeline.predict(input_data)[0]
    
    return {
        "predicted_co2_kgco2e": round(float(prediction), 3),
        "vehicle_type": data.vehicle_type,
        "distance_km": data.distance_km
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "model_loaded": pipeline is not None}