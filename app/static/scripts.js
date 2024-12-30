document.addEventListener('DOMContentLoaded', function () {
    console.log('DOM fully loaded and parsed.');

    // Initialize the map and set its view
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

    // Variable to store the selected coordinates
    let selectedCoordinates = null;

    // Function to check if a location is within Nairobi bounds
    function isWithinNairobiBounds(lat, lon) {
        return lat >= nairobiBounds.latMin && lat <= nairobiBounds.latMax &&
            lon >= nairobiBounds.lonMin && lon <= nairobiBounds.lonMax;
    }

    // Function to show and hide the loading indicator
    function showLoading() {
        document.getElementById('loading').style.display = 'block';
    }

    function hideLoading() {
        document.getElementById('loading').style.display = 'none';
    }

    // Event listener for map click to get coordinates and location name
    map.on('click', function (e) {
        const lat = e.latlng.lat;
        const lon = e.latlng.lng;

        // Check if the clicked location is within Nairobi bounds
        if (!isWithinNairobiBounds(lat, lon)) {
            alert("Selected location is outside of Nairobi. Please select a location within Nairobi.");
            return;
        }

        selectedCoordinates = { lat: lat, lon: lon }; // Store the selected coordinates

        // Fetch the location name from Nominatim
        fetch(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lon}&format=json`)
            .then(response => response.json())
            .then(data => {
                const locationName = data.display_name || "Unknown location";
                const popupContent = `<b>${locationName}</b><br>Coordinates: ${lat.toFixed(5)}, ${lon.toFixed(5)}`;
                L.popup().setLatLng(e.latlng).setContent(popupContent).openOn(map);
            })
            .catch(error => console.error("Error fetching location name:", error));
    });

    // Event listener for the "Search" button
    document.getElementById('searchButton').addEventListener('click', function () {
        const query = document.getElementById('locationSearch').value;

        fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${query}`)
            .then(response => response.json())
            .then(data => {
                if (data.length > 0) {
                    const lat = data[0].lat;
                    const lon = data[0].lon;

                    // Check if the search result is within Nairobi bounds
                    if (!isWithinNairobiBounds(lat, lon)) {
                        alert("Search result is outside of Nairobi. Please search for a location within Nairobi.");
                        return;
                    }

                    map.setView([lat, lon], 13);
                    L.marker([lat, lon]).addTo(map)
                        .bindPopup(`Search Result: ${data[0].display_name}`).openPopup();

                    selectedCoordinates = { lat: lat, lon: lon };
                } else {
                    alert('Location not found.');
                }
            })
            .catch(error => console.error("Error during search:", error));
    });

    document.getElementById('calculateButton').addEventListener('click', function () {
        if (selectedCoordinates) {
            showLoading(); // Show loading indicator
            fetch(`/flood-prediction?lat=${selectedCoordinates.lat}&lng=${selectedCoordinates.lon}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    hideLoading(); // Hide loading indicator
                    console.log('API Response:', data); // Debug: Log the response
                    if (data.hasOwnProperty('prediction')) {
                        const predictionValue = (data['prediction'] * 100).toFixed(2); // Convert to percentage
                        let riskLevel;

                        // Determine risk level based on prediction value
                        if (predictionValue < 40) {
                            riskLevel = "Very Low Risk";
                        } else if (predictionValue < 70) {
                            riskLevel = "Low Risk";
                        } else if (predictionValue < 80) {
                            riskLevel = "Medium Risk";
                        } else if (predictionValue < 86) {
                            riskLevel = "High Risk";
                        } else {
                            riskLevel = "Very High Risk";
                        }

                        // Update the UI
                        const predictionDisplay = document.getElementById('prediction-display');
                        if (predictionDisplay) {
                            predictionDisplay.textContent = `Flood Risk: ${predictionValue}% (${riskLevel})`;
                        } else {
                            console.error("Prediction display element not found.");
                        }
                    } else if (data.hasOwnProperty('error')) {
                        alert(`Error: ${data.error}`);
                    } else {
                        alert('Unexpected response from server.');
                    }
                })
                .catch(error => {
                    hideLoading(); // Hide loading indicator
                    console.error("Error fetching data from API:", error);
                });
        } else {
            alert('Please select a location on the map or search for a place first.');
        }
    });

    // Event listener for "My Location" button to show current location
    document.getElementById('currentLocationButton').addEventListener('click', function () {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function (position) {
                var lat = position.coords.latitude;
                var lon = position.coords.longitude;
                map.setView([lat, lon], 13);
                L.marker([lat, lon]).addTo(map)
                    .bindPopup("You are here!").openPopup();
                selectedCoordinates = { lat: lat, lon: lon }; // Set coordinates from current location
            }, function () {
                alert("Geolocation service failed. Please allow location access.");
            });
        } else {
            alert("Geolocation is not supported by this browser.");
        }
    });

    // Event Listener for "View Safezones" Button
    document.getElementById('safezonesButton').addEventListener('click', function () {
        if (selectedCoordinates) {
            // Pass coordinates to the next page via query parameters
            const { lat, lon } = selectedCoordinates;
            window.location.href = `/safezones?lat=${lat}&lon=${lon}`;
        } else {
            alert('Please select a location on the map or search for a place first.');
        }
    });

    // Back Button Functionality
    const backButton = document.getElementById('backButton');
    console.log("Back Button:", backButton); // Log to check if the button exists
    if (backButton) {
        backButton.addEventListener('click', function () {
            console.log('Back button clicked');
            window.location.href = '/';  
        });
    } else {
        console.log('Back button not found.');
    }
});
