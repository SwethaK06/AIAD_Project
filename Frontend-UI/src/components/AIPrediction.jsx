import {
  FaTruck,
  FaWeightHanging,
  FaRoad,
  FaTachometerAlt,
  FaLeaf,
  FaGasPump,
  FaCheckCircle,
} from "react-icons/fa";

export default function AIPrediction() {
  return (
    <div className="section">

      <h2 className="section-title">
        🤖 AI Carbon Prediction
      </h2>

      <div className="prediction-card">

        <div className="prediction-header">

          <FaTruck />

          <span>Truck B</span>

        </div>

        <div className="prediction-grid">

          <div className="prediction-item">
            <FaTachometerAlt />
            <div>
              <label>Current Speed</label>
              <h3>48 km/h</h3>
            </div>
          </div>

          <div className="prediction-item">
            <FaWeightHanging />
            <div>
              <label>Cargo Weight</label>
              <h3>820 kg</h3>
            </div>
          </div>

          <div className="prediction-item">
            <FaRoad />
            <div>
              <label>Traffic</label>
              <h3>Heavy</h3>
            </div>
          </div>

          <div className="prediction-item">
            📍
            <div>
              <label>Distance</label>
              <h3>18 km</h3>
            </div>
          </div>

        </div>

        <hr />

        <div className="prediction-results">

          <div className="result">

            <FaLeaf color="green"/>

            <div>

              <label>Predicted CO₂</label>

              <h2>6.42 kg</h2>

            </div>

          </div>

          <div className="result">

            <FaGasPump color="#f59e0b"/>

            <div>

              <label>Fuel Usage</label>

              <h2>3.8 L</h2>

            </div>

          </div>

          <div className="result">

            <FaCheckCircle color="#2563eb"/>

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