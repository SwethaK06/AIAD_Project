import { useState, useEffect } from "react";
import {
  FaTruck,
  FaWeightHanging,
  FaRoad,
  FaLeaf,
  FaCheckCircle,
  FaClock,
  FaRoute,
} from "react-icons/fa";

export default function AIPrediction({ optimizationResponse, selectedRouteId }) {
  const [dbTrip, setDbTrip] = useState(null);

  // Fetch the latest trip from Database service if no active optimizer response is present
  useEffect(() => {
    if (!optimizationResponse) {
      const getLatestTrip = async () => {
        try {
          let res = await fetch("/api/v1/trips").catch(() => null);
          if (!res || !res.ok) {
            res = await fetch("http://localhost:8002/api/v1/trips");
          }
          if (res && res.ok) {
            const data = await res.json();
            if (data.status === "success" && data.trips && data.trips.length > 0) {
              setDbTrip(data.trips[0]);
            }
          }
        } catch (err) {
          console.log("AIPrediction DB fetch note:", err);
        }
      };
      getLatestTrip();
    }
  }, [optimizationResponse]);

  // Derive values from active optimizationResponse or latest DB trip
  let vehicleType = "Truck / Van";
  let cargoWeight = null;
  let traffic = "Normal";
  let distance = null;
  let predictedCO2 = null;
  let duration = null;
  let routePriority = "Green";

  if (optimizationResponse && optimizationResponse.routes && optimizationResponse.routes.length > 0) {
    const routes = optimizationResponse.routes;
    const activeRoute = routes.find((r) => r.route_id === selectedRouteId) || routes[0];

    vehicleType = optimizationResponse.vehicle_type || "Truck / Van";
    cargoWeight = optimizationResponse.cargo_weight_kg || activeRoute.cargo_weight_kg || null;
    traffic = activeRoute.traffic_level || "Normal";
    distance = activeRoute.distance_km;
    predictedCO2 = activeRoute.predicted_co2_kgco2e;
    duration = activeRoute.duration_mins || activeRoute.duration_minutes || null;
    routePriority = optimizationResponse.route_priority || activeRoute.tag || "Green";
  } else if (dbTrip) {
    vehicleType = dbTrip.vehicle_type || "Truck / Van";
    cargoWeight = dbTrip.cargo_weight_kg;
    traffic = dbTrip.traffic_level || "Normal";
    distance = dbTrip.distance_km;
    predictedCO2 = dbTrip.predicted_co2_kgco2e;
    duration = dbTrip.duration_minutes || null;
    routePriority = dbTrip.route_priority || "Green";
  }

  // Format priority text nicely
  const formattedPriority = typeof routePriority === "string" 
    ? routePriority.charAt(0).toUpperCase() + routePriority.slice(1)
    : "Green";

  return (
    <div className="section">
      <h2 className="section-title">🤖 AI Carbon Prediction</h2>

      <div className="prediction-card">
        <div className="prediction-header">
          <FaTruck />
          <span>{vehicleType}</span>
        </div>

        <div className="prediction-grid">
          <div className="prediction-item">
            <FaWeightHanging />
            <div>
              <label>Cargo Weight</label>
              <h3>{cargoWeight !== null ? `${cargoWeight} kg` : "--"}</h3>
            </div>
          </div>

          <div className="prediction-item">
            <FaRoad />
            <div>
              <label>Traffic</label>
              <h3>{traffic}</h3>
            </div>
          </div>

          <div className="prediction-item">
            📍
            <div>
              <label>Distance</label>
              <h3>{distance !== null ? `${distance} km` : "--"}</h3>
            </div>
          </div>

          <div className="prediction-item">
            <FaRoute />
            <div>
              <label>Route Priority</label>
              <h3>{formattedPriority}</h3>
            </div>
          </div>
        </div>

        <hr />

        <div className="prediction-results">
          <div className="result">
            <FaLeaf color="green" />
            <div>
              <label>Predicted CO₂</label>
              <h2>{predictedCO2 !== null ? `${predictedCO2} kg` : "--"}</h2>
            </div>
          </div>

          {duration !== null && (
            <div className="result">
              <FaClock color="#f59e0b" />
              <div>
                <label>Est. Duration</label>
                <h2>{duration} mins</h2>
              </div>
            </div>
          )}

          <div className="result">
            <FaCheckCircle color="#2563eb" />
            <div>
              <label>Confidence</label>
              <h2>96%</h2>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}