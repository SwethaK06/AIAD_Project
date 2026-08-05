import {
  FaTruck,
  FaLeaf,
  FaGasPump,
  FaDollarSign,
  FaExclamationTriangle,
  FaBox,
  FaGlobe,
  FaRoute
} from "react-icons/fa";

const cards = [
  {
    title: "Active Trucks",
    value: "42",
    icon: <FaTruck />,
    color: "#2563eb"
  },
  {
    title: "CO₂ Today",
    value: "387 kg",
    icon: <FaLeaf />,
    color: "#16a34a"
  },
  {
    title: "Fuel Saved",
    value: "145 L",
    icon: <FaGasPump />,
    color: "#f59e0b"
  },
  {
    title: "Cost Saved",
    value: "$1,245",
    icon: <FaDollarSign />,
    color: "#7c3aed"
  },
  {
    title: "High Alerts",
    value: "5",
    icon: <FaExclamationTriangle />,
    color: "#dc2626"
  },
  {
    title: "Deliveries",
    value: "186",
    icon: <FaBox />,
    color: "#0891b2"
  },
  {
    title: "ESG Score",
    value: "94%",
    icon: <FaGlobe />,
    color: "#10b981"
  },
  {
    title: "AI Green Routes",
    value: "63",
    icon: <FaRoute />,
    color: "#6366f1"
  }
];

export default function KPICards() {
  return (
    <div className="section">

      <h2 className="section-title">Fleet Overview</h2>

      <div className="kpi-grid">

        {cards.map((card, index) => (

          <div className="kpi-card" key={index}>

            <div
              className="kpi-icon"
              style={{ background: card.color }}
            >
              {card.icon}
            </div>

            <div>

              <h3>{card.value}</h3>

              <p>{card.title}</p>

            </div>

          </div>

        ))}

      </div>

    </div>
  );
}