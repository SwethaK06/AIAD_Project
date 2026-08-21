import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd

app = FastAPI(title="ML Carbon Emission Prediction Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Resolve model path dynamically across local dev, parent dir, or container
POSSIBLE_MODEL_PATHS = [
    os.getenv("MODEL_PATH", ""),
    "carbon_model.pkl",
    "ML_Service/carbon_model.pkl",
    "../carbon_model.pkl"
]

pipeline = None
for path in POSSIBLE_MODEL_PATHS:
    if path and os.path.exists(path):
        try:
            pipeline = joblib.load(path)
            print(f"[ML Service] Successfully loaded model from {path}")
            break
        except Exception as e:
            print(f"[ML Service] Failed loading model from {path}: {e}")

if pipeline is None:
    print("[ML Service WARNING] carbon_model.pkl model file not found in searched locations!")

VEHICLE_MAPPING = {
    "truck": "Truck",
    "lorry": "Truck",
    "heavy truck": "Truck",
    "van": "Van",
    "delivery van": "Van",
    "motorcycle": "Motorcycle",
    "bike": "Motorcycle",
    "car": "Car",
    "sedan": "Car"
}

TRAFFIC_MAPPING = {
    "high": "High",
    "heavy": "High",
    "congested": "High",
    "normal": "Normal",
    "medium": "Normal",
    "moderate": "Normal",
    "low": "Low",
    "light": "Low",
    "clear": "Low"
}

class EmissionRequest(BaseModel):
    vehicle_type: str
    traffic_conditions: str
    distance_km: float
    package_weight_kg: float

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ml_service",
        "model_loaded": pipeline is not None
    }

@app.post("/predict")
def predict(data: EmissionRequest):
    if pipeline is None:
        raise HTTPException(status_code=500, detail="ML model is not loaded on server.")
    
    # Normalize categorical input features to match training categories
    norm_vehicle = VEHICLE_MAPPING.get(data.vehicle_type.strip().lower(), data.vehicle_type.strip().capitalize())
    norm_traffic = TRAFFIC_MAPPING.get(data.traffic_conditions.strip().lower(), data.traffic_conditions.strip().capitalize())
    
    # Construct DataFrame with exact columns expected by carbon_model.pkl
    df_input = pd.DataFrame([{
        "vehicle_type": norm_vehicle,
        "traffic_conditions": norm_traffic,
        "distance_km": float(data.distance_km),
        "package_weight_kg": float(data.package_weight_kg)
    }])
    
    try:
        pred = pipeline.predict(df_input)[0]
        return {
            "predicted_co2_kgco2e": round(float(pred), 3),
            "vehicle_type": norm_vehicle,
            "traffic_conditions": norm_traffic,
            "distance_km": data.distance_km,
            "package_weight_kg": data.package_weight_kg
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model prediction error: {str(e)}")