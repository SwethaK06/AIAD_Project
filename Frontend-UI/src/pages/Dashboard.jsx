import "../styles/dashboard.css";
import { useState } from "react";

import Navbar from "../components/Navbar";
import FleetMap from "../components/FleetMap";
import AIPrediction from "../components/AIPrediction";
import Recommendations from "../components/Recommendations";
import FleetTable from "../components/FleetTable";
import Analytics from "../components/Analytics";
import HeatMap from "../components/HeatMap";
import ESGReport from "../components/ESGReport";
import ServiceStatus from "../components/ServiceStatus";
import RoutePlanner from "../components/RoutePlanner";

export default function Dashboard() {
  const [optimizationResponse, setOptimizationResponse] = useState(null);

  const [selectedRouteId, setSelectedRouteId] = useState(null);

  const [selectedOrigin, setSelectedOrigin] = useState(null);

  const [selectedDestination, setSelectedDestination] = useState(null);

  return (
    <div className="dashboard">

      <Navbar />

      <RoutePlanner
        onOptimizationResponse={setOptimizationResponse}
        onRouteSelected={setSelectedRouteId}
        onLocationsSelected={(origin, destination) => {
          setSelectedOrigin(origin);
          setSelectedDestination(destination);
        }}
      />

      <FleetMap 
        optimizationResponse={optimizationResponse}
        selectedRouteId={selectedRouteId}
        selectedOrigin={selectedOrigin}
        selectedDestination={selectedDestination}
      />

      <div className="row">

        <AIPrediction />

        <Recommendations />

      </div>

      <div className="row">

        <FleetTable />

        <Analytics />

      </div>

      <div className="row">

        <HeatMap />

        <ESGReport />

      </div>

      <ServiceStatus />

    </div>
  );
}