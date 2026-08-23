// Importing components from React-Leaflet, a library for integrating Leaflet maps with React
// react-leaflet is a React library that lets yo uuse leaflet maps inside React applications.
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Polyline,
  useMap
} from "react-leaflet";

import L from "leaflet";
import { useEffect } from "react";

import "leaflet/dist/leaflet.css";


// Fix Leaflet marker icons
delete L.Icon.Default.prototype._getIconUrl;

L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",

  iconUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",

  shadowUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});


// --------------------------------------------------
// Decode Google encoded polyline
// --------------------------------------------------

function decodePolyline(encoded) {

  let index = 0;

  let lat = 0;
  let lng = 0;

  const coordinates = [];


  while (index < encoded.length) {

    let result = 0;
    let shift = 0;

    let byte;


    do {

      byte = encoded.charCodeAt(index++) - 63;

      result |= (byte & 0x1f) << shift;

      shift += 5;

    } while (byte >= 0x20);


    const deltaLat =
      (result & 1)
        ? ~(result >> 1)
        : (result >> 1);


    lat += deltaLat;


    result = 0;
    shift = 0;


    do {

      byte = encoded.charCodeAt(index++) - 63;

      result |= (byte & 0x1f) << shift;

      shift += 5;

    } while (byte >= 0x20);


    const deltaLng =
      (result & 1)
        ? ~(result >> 1)
        : (result >> 1);


    lng += deltaLng;


    coordinates.push([
      lat / 1e5,
      lng / 1e5
    ]);

  }


  return coordinates;
}


// --------------------------------------------------
// Automatically move map to route
// --------------------------------------------------

function MapController({ routeCoordinates }) {

  const map = useMap();


  useEffect(() => {

    if (
      routeCoordinates &&
      routeCoordinates.length > 0
    ) {

      const bounds =
        L.latLngBounds(routeCoordinates);

      map.fitBounds(bounds, {
        padding: [40, 40]
      });

    }

  }, [routeCoordinates, map]);


  return null;
}


// --------------------------------------------------
// Fleet Map
// --------------------------------------------------

export default function FleetMap({
  optimizationResponse,
  selectedRouteId,
  selectedOrigin,
  selectedDestination
}) {


  // No routing data yet
  if (
    !optimizationResponse ||
    !optimizationResponse.routes ||
    optimizationResponse.routes.length === 0
  ) {

    return (

      <div className="section">

        <h2 className="section-title">
          Live Fleet Map
        </h2>

        <div
          className="fleet-map"
          style={{
            height: "500px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center"
          }}
        >

          <p>
            Enter a route and click
            "Optimize Route via AI"
            to display the route.
          </p>

        </div>

      </div>

    );

  }


  // Find the selected/recommended route
  const selectedRoute =
    optimizationResponse.routes.find(
      (route) =>
        route.route_id === selectedRouteId
    )
    ||
    optimizationResponse.routes.find(
      (route) =>
        route.route_id ===
        optimizationResponse.recommended_route_id
    )
    ||
    optimizationResponse.routes[0];


  // Decode geometry_polyline
  const routeCoordinates =
    selectedRoute.geometry_polyline
      ? decodePolyline(
          selectedRoute.geometry_polyline
        )
      : [];


  return (

    <div className="section">

      <h2 className="section-title">
        Live Fleet Map
      </h2>


      <MapContainer

        center={
          routeCoordinates.length > 0
            ? routeCoordinates[0]
            : [1.3521, 103.8198]
        }

        zoom={12}

        scrollWheelZoom={true}

        className="fleet-map"

      >

        <TileLayer

          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"

          attribution='&copy; OpenStreetMap contributors'

        />


        <MapController
          routeCoordinates={routeCoordinates}
        />


        {/* --------------------------------
            Route
        -------------------------------- */}

        {routeCoordinates.length > 0 && (

          <Polyline

            positions={routeCoordinates}

            pathOptions={{
              color: "green",
              weight: 6
            }}

          />

        )}


        {/* --------------------------------
            Origin
        -------------------------------- */}

        {selectedOrigin && (

          <Marker

            position={[
              selectedOrigin.lat,
              selectedOrigin.lng
            ]}

          >

            <Popup>

              <strong>
                Origin
              </strong>

              <br />

              {selectedOrigin.address}

            </Popup>

          </Marker>

        )}


        {/* --------------------------------
            Destination
        -------------------------------- */}

        {selectedDestination && (

          <Marker

            position={[
              selectedDestination.lat,
              selectedDestination.lng
            ]}

          >

            <Popup>

              <strong>
                Destination
              </strong>

              <br />

              {selectedDestination.address}

            </Popup>

          </Marker>

        )}


        {/* --------------------------------
            Route Information
        -------------------------------- */}

        {routeCoordinates.length > 0 && (

          <Marker
            position={routeCoordinates[0]}
          >

            <Popup>

              <h3>
                {selectedRoute.tag}
              </h3>

              <hr />

              <p>
                <strong>Route:</strong>{" "}
                {selectedRoute.route_id}
              </p>

              <p>
                <strong>Distance:</strong>{" "}
                {selectedRoute.distance_km} km
              </p>

              <p>
                <strong>Duration:</strong>{" "}
                {selectedRoute.duration_mins} mins
              </p>

              <p>
                <strong>Predicted CO₂:</strong>{" "}
                {selectedRoute.predicted_co2_kgco2e} kg
              </p>

              <p>
                <strong>Traffic:</strong>{" "}
                {selectedRoute.traffic_level}
              </p>

            </Popup>

          </Marker>

        )}

      </MapContainer>

    </div>

  );
}