import {
  FaRoute,
  FaTools,
  FaUserCheck
} from "react-icons/fa";

export default function Recommendations(){

return(

<div className="section">

<h2 className="section-title">

🚨 AI Recommendations

</h2>

<div className="recommendation-card green">

<div className="recommendation-icon">

<FaRoute/>

</div>

<div className="recommendation-content">

<h3>Dynamic Route Recommendation</h3>

<p>

Truck B can reduce emissions by
<strong>30%</strong> using the AI route.

</p>

<button>

Apply Green Route

</button>

</div>

</div>

<div className="recommendation-card orange">

<div className="recommendation-icon">

<FaTools/>

</div>

<div className="recommendation-content">

<h3>Maintenance Alert</h3>

<p>

Truck A is emitting
<strong>18%</strong> above expected values.

</p>

<button>

Schedule Maintenance

</button>

</div>

</div>

<div className="recommendation-card blue">

<div className="recommendation-icon">

<FaUserCheck/>

</div>

<div className="recommendation-content">

<h3>Driver Behaviour</h3>

<p>

Driver has excessive idling.

Eco score:
<strong>82 / 100</strong>

</p>

<button>

View Driver Report

</button>

</div>

</div>

</div>

);

}