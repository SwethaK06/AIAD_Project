import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

import {
  Line,
  Bar,
  Doughnut,
} from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const lineData = {
  labels: ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],
  datasets: [{
    label: "CO₂ Emissions (kg)",
    data: [420,390,370,350,330,310,295],
    borderColor: "#16a34a",
    backgroundColor: "#16a34a",
    tension: 0.4
  }]
};

const fuelData = {
  labels: ["Truck A","Truck B","Truck C"],
  datasets: [{
    label:"Fuel Used (L)",
    data:[120,170,145],
    backgroundColor:[
      "#2563eb",
      "#16a34a",
      "#f59e0b"
    ]
  }]
};

const doughnutData = {
  labels:["Normal","Moderate","High"],
  datasets:[{
    data:[8,3,1],
    backgroundColor:[
      "#16a34a",
      "#f59e0b",
      "#dc2626"
    ]
  }]
};

const savingsData = {
  labels:["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],
  datasets:[{
    label:"Carbon Saved (kg)",
    data:[12,16,18,21,24,28,31],
    borderColor:"#2563eb",
    backgroundColor:"#2563eb",
    tension:0.4
  }]
};

export default function Analytics(){

return(

<div className="section">

<h2 className="section-title">

📊 Fleet Performance Analytics

</h2>

<div className="chart-grid">

<div className="chart-card">

<h3>CO₂ Emissions Trend</h3>

<Line data={lineData}/>

</div>

<div className="chart-card">

<h3>Fuel Consumption</h3>

<Bar data={fuelData}/>

</div>

<div className="chart-card">

<h3>Carbon Saved</h3>

<Line data={savingsData}/>

</div>

<div className="chart-card">

<h3>Fleet Status</h3>

<Doughnut data={doughnutData}/>

</div>

</div>

</div>

);

}