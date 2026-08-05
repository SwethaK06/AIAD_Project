import "../styles/dashboard.css";

import Navbar from "../components/Navbar";
import KPICards from "../components/KPICards";
import FleetMap from "../components/FleetMap";
import AIPrediction from "../components/AIPrediction";
import Recommendations from "../components/Recommendations";
import FleetTable from "../components/FleetTable";
import Analytics from "../components/Analytics";
import HeatMap from "../components/HeatMap";
import ESGReport from "../components/ESGReport";
import ServiceStatus from "../components/ServiceStatus";

export default function Dashboard() {
  return (
    <div className="dashboard">

      <Navbar />

      <KPICards />

      <FleetMap />

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