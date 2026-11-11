import {

    DollarSign,

    ShoppingCart,

    Package,

    Users,

    Truck,

    Boxes,

    Wrench,

    TrendingUp

} from "lucide-react";

const dashboardData=[

{

title:"Today's Sales",

value:"₹2,35,000",

growth:"+12%",

color:"#22c55e",

icon:<DollarSign size={28}/>

},

{

title:"Purchase",

value:"₹98,000",

growth:"+5%",

color:"#3b82f6",

icon:<ShoppingCart size={28}/>

},

{

title:"Products",

value:"1,825",

growth:"+25",

color:"#f59e0b",

icon:<Package size={28}/>

},

{

title:"Customers",

value:"245",

growth:"+10",

color:"#06b6d4",

icon:<Users size={28}/>

},

{

title:"Suppliers",

value:"35",

growth:"+2",

color:"#ec4899",

icon:<Truck size={28}/>

},

{

title:"Inventory",

value:"15,420",

growth:"+560",

color:"#8b5cf6",

icon:<Boxes size={28}/>

},

{

title:"Service",

value:"18",

growth:"Pending",

color:"#ef4444",

icon:<Wrench size={28}/>

},

{

title:"Revenue",

value:"₹5,80,000",

growth:"+18%",

color:"#16a34a",

icon:<TrendingUp size={28}/>

}

];

export default dashboardData;