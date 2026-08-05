const trucks = [
  {
    truck: "Truck A",
    driver: "John",
    cargo: "850 kg",
    speed: "52 km/h",
    traffic: "Moderate",
    co2: "6.4 kg",
    fuel: "3.6 L",
    status: "Normal"
  },
  {
    truck: "Truck B",
    driver: "Sarah",
    cargo: "620 kg",
    speed: "48 km/h",
    traffic: "Heavy",
    co2: "8.1 kg",
    fuel: "4.8 L",
    status: "Moderate"
  },
  {
    truck: "Truck C",
    driver: "David",
    cargo: "950 kg",
    speed: "30 km/h",
    traffic: "Heavy",
    co2: "10.3 kg",
    fuel: "5.9 L",
    status: "High"
  }
];

export default function FleetTable() {
  return (
    <div className="section">

      <h2 className="section-title">
        🚚 Fleet Status
      </h2>

      <table className="fleet-table">

        <thead>

          <tr>

            <th>Truck</th>

            <th>Driver</th>

            <th>Cargo</th>

            <th>Speed</th>

            <th>Traffic</th>

            <th>Predicted CO₂</th>

            <th>Fuel</th>

            <th>Status</th>

          </tr>

        </thead>

        <tbody>

          {trucks.map((truck,index)=>(

            <tr key={index}>

              <td>{truck.truck}</td>

              <td>{truck.driver}</td>

              <td>{truck.cargo}</td>

              <td>{truck.speed}</td>

              <td>{truck.traffic}</td>

              <td>{truck.co2}</td>

              <td>{truck.fuel}</td>

              <td>

                <span
                  className={`status ${truck.status.toLowerCase()}`}
                >
                  {truck.status}
                </span>

              </td>

            </tr>

          ))}

        </tbody>

      </table>

    </div>
  );
}