document.addEventListener('DOMContentLoaded', function () {
    console.log('Safe Zones Map Initialized.');

    // Initialize the map with a default view
    var map = L.map('map').setView([-1.267702, 36.810486], 13);

    // Add a tile layer to the map
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap'
    }).addTo(map);

    // Loosened bounding box for Nairobi
    const nairobiBounds = {
        latMin: -1.4443333,
        latMax: -1.191639,
        lonMin: 36.6653060,
        lonMax: 37.1017222
    };

    // Function to check if a location is within Nairobi bounds
    function isWithinNairobiBounds(lat, lon) {
        return lat >= nairobiBounds.latMin && lat <= nairobiBounds.latMax &&
            lon >= nairobiBounds.lonMin && lon <= nairobiBounds.lonMax;
    }

    // Safe Zones data (replace with API or dynamic data as needed)
    const safeZones = [
        { lat: -1.2989, lon: 36.8106, name: "Upper Hill" },
        { lat: -1.2921, lon: 36.7863, name: "Kilimani" },
        { lat: -1.2654, lon: 36.8057, name: "Westlands" },
        { lat: -1.2826, lon: 36.7725, name: "Lavington" },
        { lat: -1.2182, lon: 36.8126, name: "Runda" },
        { lat: -1.2522, lon: 36.8261, name: "Muthaiga" },
        { lat: -1.2372, lon: 36.8133, name: "Gigiri" },
        { lat: -1.3141, lon: 36.7280, name: "Karen" },
       
    ];


    // Function for reverse geocoding
    async function reverseGeocode(lat, lon) {
        const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`;
        try {
            const response = await fetch(url);
            const data = await response.json();
            return data.display_name || "Unknown Location";
        } catch (error) {
            console.error('Error reverse geocoding:', error);
            return "Error fetching location";
        }
    }

    // Plot Safe Zones on the map using circles
    async function plotSafeZones() {
        const bounds = L.latLngBounds();

        if (safeZones.length > 0) {
            for (const zone of safeZones) {
                const address = await reverseGeocode(zone.lat, zone.lon); // Fetch location name dynamically

                // Add a circle to represent the safe zone
                const circle = L.circle([zone.lat, zone.lon], {
                    color: 'green', // Circle border color
                    fillColor: '#32CD32', // Circle fill color
                    fillOpacity: 0.5, // Transparency
                    radius: 1000 // Radius in meters
                }).addTo(map);

                // Bind a popup to the circle
                circle.bindPopup(`Safe Zone: ${zone.name}<br>Location: ${address}`);

                bounds.extend(circle.getLatLng());
            }

            // Fit map view to include all Safe Zones
            map.fitBounds(bounds);
        } else {
            const errorMessage = document.createElement('div');
            errorMessage.textContent = 'Game over! No safe zones found.';
            errorMessage.style.color = 'red';
            document.getElementById('safezones').appendChild(errorMessage);
        }
    }

    plotSafeZones();

    // Event Listener for the "Back" button
    document.getElementById('backButton').addEventListener('click', function () {
        console.log('Back button clicked.');
        window.location.href = '/dashboard'; // Navigate back to the main page
    });
});
