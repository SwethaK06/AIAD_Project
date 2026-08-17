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

print("=" * 60)
print("CARBON EMISSION PREDICTION SYSTEM")
print("=" * 60)

total_start = time.time()

# --------------------------------------------------
# STEP 1 - Load dataset
# --------------------------------------------------

print("\n[STEP 1/7] Loading dataset...")

start = time.time()

df = pd.read_csv("processed_data.csv")

print(f"Dataset loaded in {time.time()-start:.2f} seconds")
print("Rows:", len(df))
print("Columns:", len(df.columns))

# --------------------------------------------------
# STEP 2 - Prepare features
# --------------------------------------------------

print("\n[STEP 2/7] Preparing features...")

start = time.time()

categorical_features = [
    "vehicle_type",
    "traffic_conditions"
]

numerical_features = [
    "distance_km",
    "package_weight_kg"
]

X = df[
    categorical_features +
    numerical_features
]

y = df["carbon_emission_kgco2e"]

print(f"Finished in {time.time()-start:.2f} seconds")

# --------------------------------------------------
# STEP 3 - Create pipeline
# --------------------------------------------------

print("\n[STEP 3/7] Creating preprocessing pipeline...")

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
# STEP 4 - Split data
# --------------------------------------------------

print("\n[STEP 4/7] Splitting dataset...")

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
# STEP 5 - Train or load model
# --------------------------------------------------

if os.path.exists(MODEL_FILE):

    print("\n[STEP 5/7] Loading saved model...")

    start = time.time()

    pipeline = joblib.load(MODEL_FILE)

    print(f"Model loaded in {time.time()-start:.2f} seconds")

else:

    print("\n[STEP 5/7] Training Random Forest...")

    start = time.time()

    pipeline.fit(X_train, y_train)

    print(f"Training completed in {time.time()-start:.2f} seconds")

    print("Saving model...")

    joblib.dump(pipeline, MODEL_FILE)

    print("Model saved.")
    # --------------------------------------------------
# STEP 6 - Evaluate model
# --------------------------------------------------

print("\n[STEP 6/7] Evaluating model...")

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
print("-" * 30)
print(f"MAE  : {mae:.3f}")
print(f"RMSE : {rmse:.3f}")
print(f"R²   : {r2:.4f}")
print(f"Approx Accuracy : {r2*100:.2f}%")

# --------------------------------------------------
# STEP 7 - Smart input preparation
# --------------------------------------------------

print("\n[STEP 7/7] Preparing smart input...")

category_values = {}

for col in categorical_features:
    category_values[col] = list(
        df[col].astype(str).unique()
    )

default_values = {
    "vehicle_type": df["vehicle_type"].mode()[0],
    "traffic_conditions": df["traffic_conditions"].mode()[0],
    "distance_km": df["distance_km"].median(),
    "package_weight_kg": df["package_weight_kg"].median()
}


def smart_match(column, value):

    value = value.strip().lower()

    if value == "none":
        return default_values[column]

    # -----------------------------
    # Vehicle Type Synonyms
    # -----------------------------
    if column == "vehicle_type":

        mapping = {

            "truck": "Truck",
            "lorry": "Truck",
            "heavy truck": "Truck",
            "cargo truck": "Truck",
            "semi": "Truck",
            "semi truck": "Truck",

            "van": "Van",
            "delivery van": "Van",
            "mini van": "Van",

            "motorbike": "Motorcycle",
            "bike": "Motorcycle",
            "motorcycle": "Motorcycle",

            "car": "Car",
            "sedan": "Car"
        }

        if value in mapping:
            print(f"Interpreted as '{mapping[value]}'")
            return mapping[value]

    # -----------------------------
    # Traffic Synonyms
    # -----------------------------
    elif column == "traffic_conditions":

        if any(word in value for word in [
            "heavy",
            "busy",
            "congested",
            "jam",
            "traffic jam",
            "very busy"
        ]):

            print("Interpreted as 'High'")
            return "High"

        if any(word in value for word in [
            "medium",
            "moderate",
            "average",
            "normal"
        ]):

            print("Interpreted as 'Medium'")
            return "Medium"

        if any(word in value for word in [
            "light",
            "low",
            "clear",
            "free",
            "empty",
            "no traffic"
        ]):

            print("Interpreted as 'Low'")
            return "Low"

    # Fuzzy matching
    choices = category_values[column]

    match = difflib.get_close_matches(
        value,
        choices,
        n=1,
        cutoff=0.5
    )

    if match:
        return match[0]

    print(f"Unknown {column}. Using default.")

    return default_values[column]
    print(f"\nTotal startup time: {time.time()-total_start:.2f} seconds")

print("\n" + "=" * 60)
print("CARBON EMISSION PREDICTOR")
print("=" * 60)

while True:

    print("\nType 'exit' at any prompt to quit.")
    print("Type 'none' if you don't know the value.\n")

    # Vehicle
    vehicle = input("Vehicle Type: ").strip()

    if vehicle.lower() == "exit":
        break

    vehicle = smart_match(
        "vehicle_type",
        vehicle
    )

    # Traffic
    traffic = input("Traffic Conditions: ").strip()

    if traffic.lower() == "exit":
        break

    traffic = smart_match(
        "traffic_conditions",
        traffic
    )

    # Distance
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

    # Weight
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

    # Create DataFrame
    sample = pd.DataFrame({

        "vehicle_type": [vehicle],
        "traffic_conditions": [traffic],
        "distance_km": [distance],
        "package_weight_kg": [weight]

    })

    print("\nPredicting...")

    prediction = pipeline.predict(sample)[0]

    # Eco friendly
    eco_threshold = df["carbon_emission_kgco2e"].median()

    eco = "YES ✅" if prediction <= eco_threshold else "NO ❌"

    # Results
    print("\n" + "=" * 60)
    print("PREDICTION RESULT")
    print("=" * 60)

    print("\nInterpreted Inputs")

    print(sample.to_string(index=False))

    print("\nPredicted Carbon Emission")
    print(f"{prediction:.2f} kgCO₂e")

    print(f"\nEco Friendly: {eco}")

    print("=" * 60)

print("\nProgram closed successfully.")