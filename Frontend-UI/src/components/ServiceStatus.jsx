import {
  FaDatabase,
  FaRobot,
  FaRoute,
  FaDesktop,
  FaCheckCircle
} from "react-icons/fa";

const services = [

{
name:"Database Service",
icon:<FaDatabase/>,
status:"Online",
latency:"18 ms"
},

{
name:"AI Prediction API",
icon:<FaRobot/>,
status:"Online",
latency:"32 ms"
},

{
name:"Route Optimizer",
icon:<FaRoute/>,
status:"Online",
latency:"21 ms"
},

{
name:"Dashboard API",
icon:<FaDesktop/>,
status:"Online",
latency:"14 ms"
}

];

export default function ServiceStatus(){

return(

<div className="section">

<h2 className="section-title">

⚙️ System Health Dashboard

</h2>

<div className="service-grid">

{services.map((service,index)=>(

<div
className="service-card"
key={index}
>

<div className="service-icon">

{service.icon}

</div>

<div>

<h3>{service.name}</h3>

<p className="online">

<FaCheckCircle/>

{service.status}

</p>

</div>

<div className="latency">

{service.latency}

</div>

</div>

))}

</div>

<hr/>

<div className="system-summary">

<div>

<h3>Overall Health</h3>

<h2>99%</h2>

</div>

<div>

<h3>Containers Running</h3>

<h2>4 / 4</h2>

</div>

<div>

<h3>Kubernetes Pods</h3>

<h2>Healthy</h2>

</div>

<div>

<h3>Last Sync</h3>

<h2>22:15</h2>

</div>

</div>

</div>

);

}