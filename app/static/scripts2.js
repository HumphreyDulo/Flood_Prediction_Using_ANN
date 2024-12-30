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
        { lat: -1.250, lon: 36.820, name: "Safe Zone 1" },
        { lat: -1.260, lon: 36.830, name: "Safe Zone 2" },
        { lat: -1.270, lon: 36.840, name: "Safe Zone 3" }
    ];

    // Plot Safe Zones on the map
    function plotSafeZones() {
        const bounds = L.latLngBounds();

        if (safeZones.length > 0) {
            safeZones.forEach(zone => {
                const marker = L.marker([zone.lat, zone.lon]).addTo(map)
                    .bindPopup(`Safe Zone: ${zone.name}`);
                bounds.extend(marker.getLatLng());
            });

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
        window.location.href = '/'; // Navigate back to the main page
    });

    // Export functionality
    document.getElementById('exportButton').addEventListener('click', function () {
        console.log('Export button clicked.');
        alert('Export functionality is not implemented yet.');
    });
});
