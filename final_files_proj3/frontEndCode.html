<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EV Charging Stations Map</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
    <style>
        #map { height: 600px; width: 100%; }
    </style>
</head>
<body>
    <h1>EV Charging Stations Map</h1>
    <div id="map"></div>
    
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script>
        let myMap = L.map("map", { center: [38.01, -95.84], zoom: 5 });

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors'
        }).addTo(myMap);

        // Fetch data from the Flask backend
        let link = "http://localhost:5000/api/v1.0/chargers";
        
        d3.json(link).then(function(data) {
            // Loop through data and add markers to the map
            data.forEach(function(station) {
                let location = [station.latitude, station.longitude];
                L.circle(location, {
                    color: "blue",
                    fillColor: "purple",
                    fillOpacity: 0.6,
                    radius: 250
                }).bindPopup(`
                    <h3>${station.station_name}</h3>
                    <p>Address: ${station.street_address}, ${station.city}, ${station.state} ${station.zip}</p>
                    <p>Total Charging Ports: ${station.total_charging_ports}</p>
                ).addTo(myMap`);
            });
        });
    </script>
</body>
</html>
