import {
MapContainer,
TileLayer,
Marker,
Popup,
Polyline
} from "react-leaflet";

import L from "leaflet";

import "leaflet/dist/leaflet.css";

delete L.Icon.Default.prototype._getIconUrl;

L.Icon.Default.mergeOptions({

iconRetinaUrl:
"https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",

iconUrl:
"https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",

shadowUrl:
"https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",

});

const trucks = [

{
id:"Truck A",

driver:"John",

cargo:"850 kg",

co2:"6.4 kg",

position:[1.3521,103.8198],

destination:[1.3400,103.9000],

status:"Normal"

},

{
id:"Truck B",

driver:"Sarah",

cargo:"620 kg",

co2:"4.1 kg",

position:[1.3105,103.8660],

destination:[1.3300,103.7800],

status:"Moderate"

},

{
id:"Truck C",

driver:"David",

cargo:"950 kg",

co2:"8.3 kg",

position:[1.3000,103.7900],

destination:[1.3900,103.8300],

status:"High"

}

];

export default function FleetMap(){

return(

<div className="section">

<h2 className="section-title">
Live Fleet Map
</h2>

<MapContainer

center={[1.3521,103.8198]}

zoom={11}

scrollWheelZoom={true}

className="fleet-map"

>

<TileLayer

url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"

/>

{trucks.map((truck)=>(

<Marker

key={truck.id}

position={truck.position}

>

<Polyline

positions={[

truck.position,

truck.destination

]}

pathOptions={{

color:"green",

weight:5

}}

/>

<Marker position={truck.destination}>

<Popup>

<h3>{truck.id}</h3>

<hr/>

<p><b>Driver</b>: {truck.driver}</p>

<p><b>Cargo</b>: {truck.cargo}</p>

<p><b>Predicted CO₂</b>: {truck.co2}</p>

<p><b>Status</b>: {truck.status}</p>

<button>

Re-route Truck

</button>

</Popup>

</Marker>

<Popup>

<h3>{truck.id}</h3>

<p><b>Driver:</b> {truck.driver}</p>

<p><b>Cargo:</b> {truck.cargo}</p>

<p><b>CO₂:</b> {truck.co2}</p>

</Popup>

</Marker>

))}

</MapContainer>

</div>

);

}