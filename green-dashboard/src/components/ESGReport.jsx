import {
  FaLeaf,
  FaGasPump,
  FaDollarSign,
  FaCheckCircle,
  FaFilePdf,
  FaFileCsv
} from "react-icons/fa";

export default function ESGReport(){

return(

<div className="section">

<h2 className="section-title">

📄 ESG Report Centre

</h2>

<div className="esg-grid">

<div className="esg-card">

<FaLeaf className="esg-icon"/>

<h3>Weekly CO₂ Reduction</h3>

<h2>12%</h2>

</div>

<div className="esg-card">

<FaGasPump className="esg-icon"/>

<h3>Fuel Saved</h3>

<h2>285 L</h2>

</div>

<div className="esg-card">

<FaDollarSign className="esg-icon"/>

<h3>Cost Savings</h3>

<h2>$3,240</h2>

</div>

<div className="esg-card">

<FaCheckCircle className="esg-icon"/>

<h3>ESG Compliance</h3>

<h2>96%</h2>

</div>

</div>

<div className="export-buttons">

<button>

<FaFilePdf/>

Export PDF

</button>

<button>

<FaFileCsv/>

Export CSV

</button>

</div>

</div>

);

}