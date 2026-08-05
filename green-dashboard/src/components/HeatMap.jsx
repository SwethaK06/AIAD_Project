const zones = [

{
name:"Jurong East",
level:"Low",
color:"green"
},

{
name:"Orchard",
level:"Moderate",
color:"yellow"
},

{
name:"PIE Expressway",
level:"High",
color:"red"
},

{
name:"Changi",
level:"Low",
color:"green"
},

{
name:"Tuas Port",
level:"High",
color:"red"
},

{
name:"Woodlands",
level:"Moderate",
color:"yellow"
}

];

export default function HeatMap(){

return(

<div className="section">

<h2 className="section-title">

🌍 Carbon Hotspots

</h2>

<div className="heatmap-grid">

{zones.map((zone,index)=>(

<div
key={index}
className={`heat-card ${zone.color}`}
>

<h3>{zone.name}</h3>

<p>{zone.level} Emissions</p>

</div>

))}

</div>

</div>

);

}