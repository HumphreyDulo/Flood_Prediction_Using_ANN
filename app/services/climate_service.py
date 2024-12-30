import requests
import logging
from datetime import datetime

class ClimateService:
    def __init__(self):
        self.api_url = "https://climate-api.open-meteo.com/v1/climate"

    def get_daily_temperature(self, latitude: float, longitude: float) -> float:
        today = datetime.today().strftime('%Y-%m-%d')

        # Construct the API URL with parameters
        url = f"{self.api_url}?latitude={latitude}&longitude={longitude}&start_date={today}&end_date={today}&models=EC_Earth3P_HR&daily=temperature_2m_mean"
        
        try:
            # Make the GET request to the API
            response = requests.get(url)

            # Check if the response was successful
            if response.status_code == 200:
                data = response.json()
                return data['daily']['temperature_2m_mean'][0]  # Return the temperature value
            else:
                # Log the error if the response is not successful
                logging.error(f"Error fetching climate data from Open Meteo Climate API - Status code: {response.status_code}, Error: {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            # Log any exceptions during the request
            logging.error(f"Error fetching climate data: {e}")
            return None
