import logging
from datetime import datetime
import requests as Http  # Assuming you're using requests module for HTTP calls

class CycloneService:
    def __init__(self):
        # Hardcoded client ID and client secret
        self.client_id = '8og8LZ6zbdDQHleusUCCj'  # Your client ID
        self.client_secret = 'sZA3Z8BHjrXAzGBEDntP2j0bVfk7AvZE4MIZY4rr'  # Your client secret
        self.api_url = "https://data.api.xweather.com/tropicalcyclones/within"

    def get_cyclone_data(self, latitude: float, longitude: float) -> float:
        try:
            # Ensure latitude and longitude are float types
            latitude = float(latitude)
            longitude = float(longitude)

            # Define buffer size
            buffer = 0.1

            # Calculate the bounds for the cyclone data request
            min_lat = latitude - buffer
            max_lat = latitude + buffer
            min_lng = longitude - buffer
            max_lng = longitude + buffer

            # Construct the API URL with parameters
            url = f"{self.api_url}?p={min_lat},{min_lng},{max_lat},{max_lng}&filter=all&limit=10&client_id={self.client_id}&client_secret={self.client_secret}"

            # Send request to the cyclone API
            response = Http.get(url)

            # Log the API response body for debugging
            logging.info(f"API Response: {response.text}")

            # Default cyclone intensity is 0.0
            cyclone_intensity = 0.0

            if response.status_code == 200:
                data = response.json()

                # Check if cyclone data exists and return intensity, else return 0.0
                if data and 'features' in data and len(data['features']) > 0:
                    # If 'intensity' exists in the data, use that value
                    cyclone_intensity = data['features'][0].get('properties', {}).get('intensity', 0.0)
                else:
                    logging.info("Cyclone data: 0.0")
            else:
                logging.error(f"Failed to fetch cyclone data. Status: {response.status_code}")
                logging.error(f"Response Body: {response.text}")

            # Return the cyclone intensity (0.0 if no data found)
            return cyclone_intensity

        except ValueError:
            logging.error("Invalid latitude or longitude values provided.")
            return 0.0
        except Exception as e:
            logging.error(f"Exception in get_cyclone_data: {str(e)}")
            return 0.0
