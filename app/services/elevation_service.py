import logging
import requests

class ElevationService:
    def __init__(self):
        self.api_url = "https://api.open-meteo.com/v1/elevation"

    def get_elevation(self, lat: float, lng: float) -> float:
        url = f"{self.api_url}?latitude={lat}&longitude={lng}"

        try:
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                return data['elevation'][0]  # Return the elevation value
            else:
                return None  # Return None if the API call fails
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching elevation data: {e}")
            return None
