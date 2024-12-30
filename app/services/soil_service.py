import requests
import logging

class SoilService:
    def __init__(self):
        self.api_url = "http://api.agromonitoring.com/agro/1.0/soil"
        self.api_key = '4422e6f041e5c4bdda92edc4678f2eda'  # Replace with your API key

    def get_soil_moisture(self, lat: float, lon: float) -> float:
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key
            }
            response = requests.get(self.api_url, params=params)

            if response.status_code == 200:
                data = response.json()
                return data.get('moisture', None)  # Return soil moisture if available
            else:
                logging.error(f"Failed to fetch soil moisture data - Status: {response.status_code}, Error: {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching soil moisture data: {e}")
            return None
