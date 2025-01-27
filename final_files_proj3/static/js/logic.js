// Create the 'basemap' tile layer that will be the background of our map.
// Create the map object with center and zoom options.

let myMap = L.map("map", {
  center: [38.01, -95.84],
  zoom: 5
});

// Adding the tile layer
// Then add the 'basemap' tile layer to the map.
let myDefaultMap = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(myMap);


// OPTIONAL: Step 2
// Create the 'street' tile layer as a second background of the map
let street = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {
  attribution: 'Tiles &copy; Esri &mdash; Source: Esri, DeLorme, NAVTEQ, USGS, Intermap, iPC, NRCAN, Esri Japan, METI, Esri China (Hong Kong), Esri (Thailand), TomTom, 2012'
});

// Define variables for our tile layers.

let baseMaps = {
  default: myDefaultMap,
  street: street
};

// Add a control to the map that will allow the user to change which layers are visible.
L.control.layers(baseMaps).addTo(myMap);
// Make a request that retrieves the charging station geoJSON data.

let link = "http://localhost:5000/api/v1.0/chargers";

d3.json(d3.json("http://localhost:5000/api/v1.0/chargers").then(function(data) {
  console.log(data); // Check the data structure in the console


  // This function returns the style data for each of the charging stations we plot on
  // the mapinto two separate functions
  // to calculate the color and radius.


  function markerSize(population) {
    return Math.sqrt(population) * 50;
  }

  // Loop through the cities array, and create one marker for each city object.
  data.forEach(function(station){
    let myLocation = [station.latitude, station.longitude];

    // Create a circle marker for each charging station
    L.circle(myLocation, {
      fillOpacity: 1,
      color: "blue",
      fillColor: "purple",
      // Setting our circle's radius to equal the output of our markerSize() function:
      // This will make our marker's size proportionate to its population.
      radius:'250'
    }).bindPopup(`<h1>$station.station_name}</h1> <hr> <h3>Address: ${station.street_address}, ${station.city}</h3>`).addTo(myMap);
  })
}));
