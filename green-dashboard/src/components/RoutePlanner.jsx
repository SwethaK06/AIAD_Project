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

export default function RoutePlanner() {
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

  const [selectedDestination, setSelectedDestination] =
    useState(null);

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
   * Create the final routing JSON
   *
   * This happens only after the user has selected
   * both the origin and destination.
   */
  const handleCreateRouteRequest = () => {
    setErrorMessage("");

    /*
     * Make sure origin was selected
     */
    if (!selectedOrigin) {
      setErrorMessage(
        "Please select a location for the origin."
      );
      return;
    }

    /*
     * Make sure destination was selected
     */
    if (!selectedDestination) {
      setErrorMessage(
        "Please select a location for the destination."
      );
      return;
    }

    /*
     * Make sure cargo weight is valid
     */
    if (!cargoWeight || Number(cargoWeight) <= 0) {
      setErrorMessage(
        "Please enter a cargo weight greater than 0 kg."
      );
      return;
    }

    /*
     * Create the JSON object that will eventually
     * be sent to the Routing Engine.
     */
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

    /*
     * Store the request so it can be displayed
     * on the dashboard.
     */
    setRouteRequest(request);

    /*
     * Also print the JSON to the browser console
     * for testing.
     */
    console.log("Routing Request JSON:");
    console.log(request);
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
          CREATE ROUTE REQUEST
      ========================================= */}

      {selectedOrigin &&
        selectedDestination && (

          <div className="route-action">

            <button
              className="calculate-route-button"
              onClick={handleCreateRouteRequest}
            >

              <FaLeaf />

              Create Route Request

            </button>

          </div>

        )}


      {/* =========================================
          ROUTING REQUEST JSON
      ========================================= */}

      {routeRequest && (

        <div className="route-request-result">

          <div className="route-success">

            ✓ Route request created successfully

          </div>


          <h3>
            Routing Request
          </h3>


          <pre>
            {JSON.stringify(
              routeRequest,
              null,
              2
            )}
          </pre>

        </div>

      )}

    </div>
  );
}