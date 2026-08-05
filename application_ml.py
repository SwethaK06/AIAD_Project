import os
import time
import joblib
import difflib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

print("="*60)
print("CARBON EMISSION PREDICTION SYSTEM")
print("="*60)

total_start = time.time()

# --------------------------------------------------
# STEP 1
# --------------------------------------------------

print("\n[STEP 1/8] Loading dataset...")

start = time.time()

df = pd.read_csv("processed_data.csv")

print(f"Dataset loaded in {time.time()-start:.2f} seconds")
print("Rows:", len(df))
print("Columns:", len(df.columns))

# --------------------------------------------------
# STEP 2
# --------------------------------------------------

print("\n[STEP 2/8] Preparing features...")

start = time.time()

categorical_features = [
    "origin_facility",
    "destination_city",
    "vehicle_type",
    "route_type",
    "traffic_conditions"
]

numerical_features = [
    "distance_km",
    "package_weight_kg"
]

X = df.drop(columns=[
    "transaction_id",
    "date",
    "carbon_emission_kgco2e",
    "is_eco_friendly"
])

y = df["carbon_emission_kgco2e"]

print(f"Finished in {time.time()-start:.2f} seconds")

# --------------------------------------------------
# STEP 3
# --------------------------------------------------

print("\n[STEP 3/8] Creating preprocessing pipeline...")

start = time.time()

preprocessor = ColumnTransformer([
    (
        "cat",
        OneHotEncoder(handle_unknown="ignore"),
        categorical_features
    ),
    (
        "num",
        "passthrough",
        numerical_features
    )
])

pipeline = Pipeline([
    (
        "preprocessor",
        preprocessor
    ),
    (
        "model",
        RandomForestRegressor(
            n_estimators=100,
            random_state=42,
            n_jobs=-1
        )
    )
])

print(f"Finished in {time.time()-start:.2f} seconds")

# --------------------------------------------------
# STEP 4
# --------------------------------------------------

print("\n[STEP 4/8] Splitting dataset...")

start = time.time()

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

print(f"Finished in {time.time()-start:.2f} seconds")

MODEL_FILE = "carbon_model.pkl"

# --------------------------------------------------
# STEP 5
# --------------------------------------------------

if os.path.exists(MODEL_FILE):

    print("\n[STEP 5/8] Loading saved model...")

    start = time.time()

    pipeline = joblib.load(MODEL_FILE)

    print(f"Model loaded in {time.time()-start:.2f} seconds")

else:

    print("\n[STEP 5/8] Training Random Forest...")

    start = time.time()

    pipeline.fit(X_train, y_train)

    print(f"Training completed in {time.time()-start:.2f} seconds")

    print("Saving model...")

    joblib.dump(pipeline, MODEL_FILE)

    print("Model saved.")

# --------------------------------------------------
# STEP 6
# --------------------------------------------------

print("\n[STEP 6/8] Evaluating model...")

start = time.time()

pred = pipeline.predict(X_test)

mae = mean_absolute_error(y_test, pred)

rmse = mean_squared_error(
    y_test,
    pred
) ** 0.5

r2 = r2_score(y_test, pred)

print(f"Finished in {time.time()-start:.2f} seconds")

print("\nMODEL PERFORMANCE")
print("-"*30)
print(f"MAE  : {mae:.3f}")
print(f"RMSE : {rmse:.3f}")
print(f"R²   : {r2:.4f}")
print(f"Approx Accuracy : {r2*100:.2f}%")

# --------------------------------------------------
# STEP 7
# --------------------------------------------------

print("\n[STEP 7/8] Preparing smart input...")

category_values = {}

for col in categorical_features:
    category_values[col] = list(
        df[col].astype(str).unique()
    )

default_values = {
    "origin_facility": df["origin_facility"].mode()[0],
    "destination_city": df["destination_city"].mode()[0],
    "vehicle_type": df["vehicle_type"].mode()[0],
    "route_type": df["route_type"].mode()[0],
    "traffic_conditions": df["traffic_conditions"].mode()[0],
    "distance_km": df["distance_km"].median(),
    "package_weight_kg": df["package_weight_kg"].median()
}

def smart_match(column, value):

    if value.lower() == "none":
        return default_values[column]

    choices = category_values[column]

    match = difflib.get_close_matches(
        value,
        choices,
        n=1,
        cutoff=0.40
    )

    if match:

        if match[0].lower() != value.lower():

            print(f"Interpreted '{value}' as '{match[0]}'")

        return match[0]

    print(f"No similar value found. Using default for {column}")

    return default_values[column]
    # --------------------------------------------------
# STEP 8
# --------------------------------------------------

print("\n[STEP 8/8] Ready for predictions!")
print(f"Total startup time: {time.time()-total_start:.2f} seconds")

print("\n" + "="*60)
print("CARBON EMISSION PREDICTOR")
print("="*60)

while True:

    print("\nType 'exit' at any prompt to quit.")
    print("Type 'none' if you don't know the value.\n")

    # ----------------------------
    # Origin Facility
    # ----------------------------
    origin = input("Origin Facility: ").strip()

    if origin.lower() == "exit":
        break

    origin = smart_match("origin_facility", origin)

    # ----------------------------
    # Destination
    # ----------------------------
    destination = input("Destination City: ").strip()

    if destination.lower() == "exit":
        break

    destination = smart_match(
        "destination_city",
        destination
    )

    # ----------------------------
    # Vehicle
    # ----------------------------
    vehicle = input("Vehicle Type: ").strip()

    if vehicle.lower() == "exit":
        break

    vehicle = smart_match(
        "vehicle_type",
        vehicle
    )

    # ----------------------------
    # Route
    # ----------------------------
    route = input("Route Type: ").strip()

    if route.lower() == "exit":
        break

    route = smart_match(
        "route_type",
        route
    )

    # ----------------------------
    # Traffic
    # ----------------------------
    traffic = input("Traffic Conditions: ").strip()

    if traffic.lower() == "exit":
        break

    traffic = smart_match(
        "traffic_conditions",
        traffic
    )

    # ----------------------------
    # Distance
    # ----------------------------
    while True:

        distance = input("Distance (km): ").strip()

        if distance.lower() == "exit":
            exit()

        if distance.lower() == "none":
            distance = default_values["distance_km"]
            break

        try:
            distance = float(distance)
            break

        except ValueError:
            print("Please enter a valid number.")

    # ----------------------------
    # Weight
    # ----------------------------
    while True:

        weight = input("Package Weight (kg): ").strip()

        if weight.lower() == "exit":
            exit()

        if weight.lower() == "none":
            weight = default_values["package_weight_kg"]
            break

        try:
            weight = float(weight)
            break

        except ValueError:
            print("Please enter a valid number.")

    # ----------------------------
    # Create DataFrame
    # ----------------------------

    sample = pd.DataFrame({

        "origin_facility":[origin],
        "destination_city":[destination],
        "vehicle_type":[vehicle],
        "route_type":[route],
        "distance_km":[distance],
        "package_weight_kg":[weight],
        "traffic_conditions":[traffic]

    })

    print("\nPredicting...")

    prediction = pipeline.predict(sample)[0]

    # ----------------------------
    # Eco Friendly Status
    # ----------------------------

    eco_threshold = df["carbon_emission_kgco2e"].median()

    eco = "YES ✅" if prediction <= eco_threshold else "NO ❌"

    # ----------------------------
    # Results
    # ----------------------------

    print("\n" + "="*60)
    print("PREDICTION RESULT")
    print("="*60)

    print("\nInterpreted Inputs")

    print(sample.to_string(index=False))

    print("\nPredicted Carbon Emission")
    print(f"{prediction:.2f} kgCO₂e")

    print(f"\nEco Friendly: {eco}")

    print("="*60)

print("\nProgram closed successfully.")