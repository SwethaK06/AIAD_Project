from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd

app = FastAPI()

# Load the saved model pipeline
pipeline = joblib.load("ML_Service/carbon_model.pkl")

class EmissionRequest(BaseModel):
    vehicle_type: str
    # route_type: str
    traffic_conditions: str
    distance_km: float
    package_weight_kg: float
    # Optional parameters with default fallback values
    # origin_facility: str = "Jakarta Fulfillment Center"
    # destination_city: str = "Waynehaven"

@app.post("/predict")
def predict(data: EmissionRequest):
    # Construct DataFrame with ALL columns expected by carbon_model.pkl
    df_input = pd.DataFrame([{
        "vehicle_type": data.vehicle_type,
        "distance_km": data.distance_km,
        "package_weight_kg": data.package_weight_kg,
        "traffic_conditions": data.traffic_conditions
    }])
    
    # Run prediction
    pred = pipeline.predict(df_input)[0]
    return {"predicted_co2_kgco2e": round(float(pred), 3)}