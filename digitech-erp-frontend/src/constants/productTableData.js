const productColumns = [

    {
        key:"sku",
        label:"SKU"
    },

    {
        key:"name",
        label:"Product Name"
    },

    {
        key:"category",
        label:"Category"
    },

    {
        key:"brand",
        label:"Brand"
    },

    {
        key:"price",
        label:"Price"
    },

    {
        key:"stock",
        label:"Stock"
    },

    {
        key:"status",
        label:"Status"
    }

];

const productData=[

{

sku:"PRD001",

name:"Kyocera MA4000WiFiX",

category:"Printer",

brand:"Kyocera",

price:"₹24,500",

stock:15,

status:"Active"

},

{

sku:"PRD002",

name:"Canon IR 3025",

category:"Photocopier",

brand:"Canon",

price:"₹45,000",

stock:8,

status:"Active"

},

{

sku:"PRD003",

name:"HP LaserJet Pro",

category:"Printer",

brand:"HP",

price:"₹18,000",

stock:20,

status:"Active"

}

];

export{

productColumns,

productData

};
const products = [

{

id:1,

name:"Kyocera MA4000WiFiX",

subtitle:"PCS • 3 Months",

brand:"Kyocera",

model:"Taskalfa 2554",

category:"Printer",

sku:"KYO4000",

dtp:24500,

retail:26500,

cost:22000,

margin:"20%",

gst:"18%",

stock:15,

status:"Active"

},

{

id:2,

name:"Canon IR Advance",

subtitle:"PCS • 1 Month",

brand:"Canon",

model:"IR3025",

category:"Photocopier",

sku:"CAN3025",

dtp:75000,

retail:85000,

cost:65000,

margin:"23%",

gst:"18%",

stock:2,

status:"Active"

}

];

export default products;