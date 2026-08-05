import {
  FaTruck,
  FaBell,
  FaUserCircle,
  FaCircle
} from "react-icons/fa";

export default function Navbar() {

  const currentDate = new Date();

  return (

    <nav className="navbar">

      <div className="navbar-left">

        <FaTruck className="truck-icon"/>

        <div>

          <h1>Green Logistics Dashboard</h1>

          <p>AI Carbon Emission Monitoring System</p>

        </div>

      </div>

      <div className="navbar-right">

        <div className="fleet-status">

          <FaCircle className="status-dot"/>

          Fleet Online

        </div>

        <div className="current-date">

          {currentDate.toLocaleDateString("en-SG",{
            weekday:"short",
            day:"numeric",
            month:"short",
            year:"numeric"
          })}

        </div>

        <FaBell className="navbar-icon"/>

        <FaUserCircle className="navbar-icon"/>

      </div>

    </nav>

  );

}