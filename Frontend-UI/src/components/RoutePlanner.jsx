import { useState } from "react";
import { geocodeSingaporeAddress } from "../services/geocoding";

import {
  FaMapMarkerAlt,
  FaFlagCheckered,
  FaWeightHanging,
  FaTruck,
  FaLeaf,
  FaBolt,
  FaBalanceScale,
} from "react-icons/fa";

export default function RoutePlanner({
  onOptimizationResponse,
  onRouteSelected,
  onLocationsSelected
}) {
  const [origin, setOrigin] = useState("");
  const [destination, setDestination] = useState("");
  const [cargoWeight, setCargoWeight] = useState("");
  const [vehicleType, setVehicleType] = useState("truck");
  const [priority, setPriority] = useState("balanced");

  const [isCalculating, setIsCalculating] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [routeRequest, setRouteRequest] = useState(null);

  const [originResults, setOriginResults] = useState([]);
  const [destinationResults, setDestinationResults] = useState([]);
  const [selectedOrigin, setSelectedOrigin] = useState(null);
  const [selectedDestination, setSelectedDestination] = useState(null);

  const [optimizationResponse, setOptimizationResponse] = useState(null);
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [selectedRouteId, setSelectedRouteId] = useState(null);
  const [dbLogStatus, setDbLogStatus] = useState(null);
  const [isLoggingDb, setIsLoggingDb] = useState(false);

  /*
   * Search for possible locations
   */
  const handleCalculateRoute = async () => {
    setErrorMessage("");
    setRouteRequest(null);

    setOriginResults([]);
    setDestinationResults([]);

    setSelectedOrigin(null);
    setSelectedDestination(null);

    /*
     * Validate origin
     */
    if (!origin.trim()) {
      setErrorMessage("Please enter an origin.");
      return;
    }

    /*
     * Validate destination
     */
    if (!destination.trim()) {
      setErrorMessage("Please enter a destination.");
      return;
    }

    /*
     * Validate cargo weight
     */
    if (!cargoWeight || Number(cargoWeight) <= 0) {
      setErrorMessage(
        "Please enter a cargo weight greater than 0 kg."
      );
      return;
    }

    try {
      setIsCalculating(true);

      /*
       * Search for possible origin locations
       */
      const originMatches =
        await geocodeSingaporeAddress(origin);

      setOriginResults(originMatches);

      /*
       * Wait before making the second request.
       *
       * Nominatim's public service asks applications
       * to stay within 1 request per second.
       */
      await new Promise((resolve) =>
        setTimeout(resolve, 1100)
      );

      /*
       * Search for possible destination locations
       */
      const destinationMatches =
        await geocodeSingaporeAddress(destination);

      setDestinationResults(destinationMatches);

    } catch (error) {
      setErrorMessage(
        error.message ||
          "Unable to find the requested locations."
      );
    } finally {
      setIsCalculating(false);
    }
  };


  /*
   * When the user selects an origin,
   * store that location.
   */
  const handleSelectOrigin = (result) => {
    setSelectedOrigin(result);
    setOriginResults([]);

    /*
     * Remove any previous routing result
     */
    setRouteRequest(null);
    setErrorMessage("");
  };


  /*
   * When the user selects a destination,
   * store that location.
   */
  const handleSelectDestination = (result) => {
    setSelectedDestination(result);
    setDestinationResults([]);

    /*
     * Remove any previous routing result
     */
    setRouteRequest(null);
    setErrorMessage("");
  };


  /*
   * Sends the route request to the Routing Engine API
   * and retrieves candidate route options with ML CO2 predictions.
   */
  const handleCreateRouteRequest = async () => {
    setErrorMessage("");
    setOptimizationResponse(null);
    setDbLogStatus(null);

    if (!selectedOrigin) {
      setErrorMessage("Please select a location for the origin.");
      return;
    }

    if (!selectedDestination) {
      setErrorMessage("Please select a location for the destination.");
      return;
    }

    if (!cargoWeight || Number(cargoWeight) <= 0) {
      setErrorMessage("Please enter a cargo weight greater than 0 kg.");
      return;
    }

    const request = {
      origin: {
        lat: selectedOrigin.lat,
        lng: selectedOrigin.lng,
        address: selectedOrigin.address,
      },
      destination: {
        lat: selectedDestination.lat,
        lng: selectedDestination.lng,
        address: selectedDestination.address,
      },
      cargo_weight_kg: Number(cargoWeight),
      vehicle_type: vehicleType,
      priority_weight: priority,
    };

    setRouteRequest(request);
    setIsOptimizing(true);

    try {
      let response = await fetch("/api/v1/optimize-route", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(request),
      }).catch(() => null);

      if (!response || !response.ok) {
        response = await fetch("http://localhost:8001/api/v1/optimize-route", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(request),
        });
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Routing service error (${response.status})`);
      }

      const data = await response.json();

      setOptimizationResponse(data);

      const recommendedRouteId =
        data.recommended_route_id ||
        data.routes?.[0]?.route_id ||
        null;
      
      setSelectedRouteId(recommendedRouteId);

      // Send the routing response to Dashboard
      if (onOptimizationResponse) {
        onOptimizationResponse(data);
      }

      // Send origin and destination to Dashboard
      if (onLocationsSelected) {
        onLocationsSelected(
          selectedOrigin,
          selectedDestination
        );
      }
    } catch (err) {
      setErrorMessage(err.message || "Unable to reach Routing Engine service");
    } finally {
      setIsOptimizing(false);
    }
  };

  /*
   * Logs selected trip to the Database Service
   */
  const handleConfirmAndLogTrip = async (route) => {
    setDbLogStatus(null);
    setIsLoggingDb(true);
    setErrorMessage("");

    try {
      const uniqueTripId = (optimizationResponse && optimizationResponse.trip_id)
        ? `${optimizationResponse.trip_id}-${Date.now().toString().slice(-4)}`
        : `TRIP-${Date.now()}`;

      const tripPayload = {
        trip_id: uniqueTripId,
        origin: selectedOrigin.address,
        destination: selectedDestination.address,
        origin_coords: `${selectedOrigin.lat},${selectedOrigin.lng}`,
        dest_coords: `${selectedDestination.lat},${selectedDestination.lng}`,
        vehicle_type: vehicleType,
        cargo_weight_kg: Number(cargoWeight),
        route_priority: priority,
        recommended_route_id: route.route_id,
        chosen_route_id: route.route_id,
        predicted_co2_kgco2e: route.predicted_co2_kgco2e,
        actual_co2_kgco2e: route.predicted_co2_kgco2e,
        distance_km: route.distance_km,
        geometry_polyline: route.geometry_polyline || "",
        duration_minutes: route.duration_mins || route.duration_minutes || 0,
      };

      let response = await fetch("/api/v1/trips", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(tripPayload),
      }).catch(() => null);

      if (!response || !response.ok) {
        response = await fetch("http://localhost:8002/api/v1/trips", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(tripPayload),
        });
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const detailMsg = typeof errorData.detail === "string" ? errorData.detail : (Array.isArray(errorData.detail) ? errorData.detail.map(d => d.msg || JSON.stringify(d)).join(", ") : "");
        throw new Error(detailMsg || `Database service error (${response.status})`);
      }

      const result = await response.json();
      setDbLogStatus(result);
    } catch (err) {
      setErrorMessage(err.message || "Unable to log trip to Database service at http://localhost:8002");
    } finally {
      setIsLoggingDb(false);
    }
  };


  return (
    <div className="section route-planner">

      {/* =========================================
          HEADER
      ========================================= */}

      <div className="route-planner-header">

        <div>

          <h2 className="section-title">
            🚚 Plan a Green Route
          </h2>

          <p className="route-planner-description">
            Enter your delivery details and choose how
            the system should prioritize your route.
          </p>

        </div>

      </div>


      {/* =========================================
          ORIGIN AND DESTINATION
      ========================================= */}

      <div className="location-grid">

        {/* =====================================
            ORIGIN
        ===================================== */}

        <div className="input-group">

          <label htmlFor="origin">

            <FaMapMarkerAlt />

            Origin

          </label>


          <input
            id="origin"
            type="text"
            placeholder="e.g. Singapore Port"
            value={origin}
            onChange={(e) => {
              setOrigin(e.target.value);

              /*
               * Clear previously selected origin
               * if the user changes the input.
               */
              setSelectedOrigin(null);

              setOriginResults([]);

              setRouteRequest(null);

              setErrorMessage("");
            }}
          />


          <small>
            Enter a Singapore address or place name
          </small>


          {/* =================================
              ORIGIN SEARCH RESULTS
          ================================= */}

          {originResults.length > 0 &&
            !selectedOrigin && (

              <div className="location-results">

                <h4>
                  Select Origin
                </h4>

                <p>
                  We found these possible locations:
                </p>


                {originResults.map((result, index) => (

                  <button
                    type="button"
                    key={`${result.osmType}-${result.osmId}-${index}`}
                    className="location-result"
                    onClick={() =>
                      handleSelectOrigin(result)
                    }
                  >

                    <span className="location-result-icon">
                      📍
                    </span>


                    <span className="location-result-text">

                      <strong>
                        {result.address.split(",")[0]}
                      </strong>


                      <small>
                        {result.address}
                      </small>

                    </span>

                  </button>

                ))}

              </div>

            )}


          {/* =================================
              SELECTED ORIGIN
          ================================= */}

          {selectedOrigin && (

            <div className="selected-location">

              <span>
                ✓
              </span>


              <div>

                <strong>
                  Origin selected
                </strong>


                <small>
                  {selectedOrigin.address}
                </small>

              </div>

            </div>

          )}

        </div>


        {/* =====================================
            DESTINATION
        ===================================== */}

        <div className="input-group">

          <label htmlFor="destination">

            <FaFlagCheckered />

            Destination

          </label>


          <input
            id="destination"
            type="text"
            placeholder="e.g. Marina Bay Sands"
            value={destination}
            onChange={(e) => {
              setDestination(e.target.value);

              /*
               * Clear previously selected destination
               * if the user changes the input.
               */
              setSelectedDestination(null);

              setDestinationResults([]);

              setRouteRequest(null);

              setErrorMessage("");
            }}
          />


          <small>
            Enter a Singapore address or place name
          </small>


          {/* =================================
              DESTINATION SEARCH RESULTS
          ================================= */}

          {destinationResults.length > 0 &&
            !selectedDestination && (

              <div className="location-results">

                <h4>
                  Select Destination
                </h4>

                <p>
                  We found these possible locations:
                </p>


                {destinationResults.map(
                  (result, index) => (

                    <button
                      type="button"
                      key={`${result.osmType}-${result.osmId}-${index}`}
                      className="location-result"
                      onClick={() =>
                        handleSelectDestination(
                          result
                        )
                      }
                    >

                      <span className="location-result-icon">
                        📍
                      </span>


                      <span className="location-result-text">

                        <strong>
                          {result.address.split(",")[0]}
                        </strong>


                        <small>
                          {result.address}
                        </small>

                      </span>

                    </button>

                  )
                )}

              </div>

            )}


          {/* =================================
              SELECTED DESTINATION
          ================================= */}

          {selectedDestination && (

            <div className="selected-location">

              <span>
                ✓
              </span>


              <div>

                <strong>
                  Destination selected
                </strong>


                <small>
                  {selectedDestination.address}
                </small>

              </div>

            </div>

          )}

        </div>

      </div>


      {/* =========================================
          CARGO AND VEHICLE
      ========================================= */}

      <div className="route-details-grid">

        {/* Cargo Weight */}

        <div className="input-group">

          <label htmlFor="cargoWeight">

            <FaWeightHanging />

            Cargo Weight

          </label>


          <div className="input-with-unit">

            <input
              id="cargoWeight"
              type="number"
              min="0"
              step="0.1"
              placeholder="e.g. 1200"
              value={cargoWeight}
              onChange={(e) => {
                setCargoWeight(e.target.value);

                setRouteRequest(null);

                setErrorMessage("");
              }}
            />


            <span>
              kg
            </span>

          </div>

        </div>


        {/* Vehicle Type */}

        <div className="input-group">

          <label htmlFor="vehicleType">

            <FaTruck />

            Vehicle Type

          </label>


          <select
            id="vehicleType"
            value={vehicleType}
            onChange={(e) => {
              setVehicleType(e.target.value);

              setRouteRequest(null);
            }}
          >

            <option value="truck">
              Truck
            </option>

            <option value="van">
              Van
            </option>

            <option value="motorcycle">
              Motorcycle
            </option>

            <option value="car">
              Car
            </option>

          </select>

        </div>

      </div>


      {/* =========================================
          ROUTE PRIORITY
      ========================================= */}

      <div className="priority-section">

        <div className="priority-heading">

          <h3>
            Route Priority
          </h3>


          <p>
            Choose what the routing system should
            prioritize.
          </p>

        </div>


        <div className="priority-grid">


          {/* =====================================
              GREEN
          ===================================== */}

          <button
            type="button"
            className={`priority-card green-priority ${
              priority === "green"
                ? "selected"
                : ""
            }`}
            onClick={() => {
              setPriority("green");
              setRouteRequest(null);
            }}
          >

            <div className="priority-icon">

              <FaLeaf />

            </div>


            <div className="priority-content">

              <h3>
                Green
              </h3>


              <span>
                Strictly Eco-Friendly
              </span>


              <p>
                Prioritizes the route with the
                lowest predicted CO₂ emissions,
                even if it takes longer.
              </p>

            </div>

          </button>


          {/* =====================================
              FASTEST
          ===================================== */}

          <button
            type="button"
            className={`priority-card fastest-priority ${
              priority === "fastest"
                ? "selected"
                : ""
            }`}
            onClick={() => {
              setPriority("fastest");
              setRouteRequest(null);
            }}
          >

            <div className="priority-icon">

              <FaBolt />

            </div>


            <div className="priority-content">

              <h3>
                Fastest
              </h3>


              <span>
                Time-Sensitive Delivery
              </span>


              <p>
                Prioritizes the shortest travel
                time, even if the route produces
                more emissions.
              </p>

            </div>

          </button>


          {/* =====================================
              BALANCED
          ===================================== */}

          <button
            type="button"
            className={`priority-card balanced-priority ${
              priority === "balanced"
                ? "selected"
                : ""
            }`}
            onClick={() => {
              setPriority("balanced");
              setRouteRequest(null);
            }}
          >

            <div className="priority-icon">

              <FaBalanceScale />

            </div>


            <div className="priority-content">

              <h3>
                Balanced
              </h3>


              <span>
                Multi-Objective Optimization
              </span>


              <p>
                Balances CO₂ emissions and travel
                time to find a practical route.
              </p>

            </div>

          </button>

        </div>

      </div>


      {/* =========================================
          ERROR MESSAGE
      ========================================= */}

      {errorMessage && (

        <div className="route-error">

          {errorMessage}

        </div>

      )}


      {/* =========================================
          CALCULATE / SEARCH LOCATIONS
      ========================================= */}

      <div className="route-action">

        <button
          className="calculate-route-button"
          onClick={handleCalculateRoute}
          disabled={isCalculating}
        >

          <FaLeaf />


          {isCalculating
            ? "Finding Locations..."
            : "Find Locations"}

        </button>

      </div>


      {/* =========================================
          CREATE & OPTIMIZE ROUTE REQUEST
      ========================================= */}

      {selectedOrigin && selectedDestination && (
        <div className="route-action">
          <button
            className="calculate-route-button"
            onClick={handleCreateRouteRequest}
            disabled={isOptimizing}
          >
            <FaLeaf />
            {isOptimizing ? "Optimizing Route via AI..." : "Optimize Route via AI"}
          </button>
        </div>
      )}


      {/* =========================================
          OPTIMIZATION RESULTS & CANDIDATE ROUTES
      ========================================= */}

      {optimizationResponse && optimizationResponse.routes && (
        <div className="route-request-result" style={{ marginTop: "20px" }}>
          <div className="route-success">
            ✓ Found {optimizationResponse.routes.length} candidate route(s) (Trip ID: {optimizationResponse.trip_id})
          </div>

          <h3 style={{ marginTop: "15px", marginBottom: "10px" }}>
            Ranked Route Candidates
          </h3>

          <div className="location-results" style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
            {optimizationResponse.routes.map((route) => (
              <div
                key={route.route_id}
                style={{
                  border: route.route_id === selectedRouteId ? "2px solid #10b981" : "1px solid #e5e7eb",
                  borderRadius: "8px",
                  padding: "16px",
                  backgroundColor: route.route_id === selectedRouteId ? "#f0fdf4" : "#ffffff",
                  boxShadow: "0 2px 4px rgba(0,0,0,0.05)"
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                  <strong style={{ fontSize: "1.1rem", color: "#111827" }}>
                    {route.tag}
                  </strong>
                  <span style={{ fontSize: "0.85rem", backgroundColor: "#e0e7ff", color: "#3730a3", padding: "2px 8px", borderRadius: "12px" }}>
                    {route.route_id}
                  </span>
                </div>

                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(120px, 1fr))", gap: "10px", margin: "12px 0", fontSize: "0.9rem" }}>
                  <div><strong>Distance:</strong> {route.distance_km} km</div>
                  <div><strong>Duration:</strong> {route.duration_mins} mins</div>
                  <div><strong>Predicted CO₂:</strong> <span style={{ color: "#059669", fontWeight: "bold" }}>{route.predicted_co2_kgco2e} kg</span></div>
                  <div><strong>Traffic:</strong> {route.traffic_level}</div>
                  <div><strong>Score:</strong> {route.cost_score}</div>
                </div>

                <button
                  type="button"
                  onClick={() => {
                    setSelectedRouteId(route.route_id);

                    if (onRouteSelected) {
                      onRouteSelected(route.route_id);
                    }

                    handleConfirmAndLogTrip(route);
                  }}
                  disabled={isLoggingDb}
                  style={{
                    backgroundColor: "#059669",
                    color: "white",
                    border: "none",
                    padding: "8px 16px",
                    borderRadius: "6px",
                    cursor: "pointer",
                    fontWeight: "600",
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "6px",
                    marginTop: "8px"
                  }}
                >
                  <FaLeaf />
                  {isLoggingDb && selectedRouteId === route.route_id
                    ? "Logging to Database..."
                    : "Select & Confirm Trip"}
                </button>
              </div>
            ))}
          </div>

          {dbLogStatus && (
            <div className="route-success" style={{ marginTop: "15px", backgroundColor: "#ecfdf5", color: "#065f46", padding: "12px", borderRadius: "6px" }}>
              ✓ Trip logged to Database! (Storage: <strong>{dbLogStatus.storage}</strong>, Trip ID: {dbLogStatus.trip_id})
            </div>
          )}
        </div>
      )}

      {/* =========================================
          ROUTING REQUEST PAYLOAD DEBUG
      ========================================= */}

      {routeRequest && !optimizationResponse && (
        <div className="route-request-result">
          <div className="route-success">
            ✓ Route request created successfully
          </div>

          <h3>Routing Request Payload</h3>

          <pre>
            {JSON.stringify(routeRequest, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}