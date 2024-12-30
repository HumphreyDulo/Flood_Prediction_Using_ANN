import requests
import logging

class RiverService:
    def get_river_discharge(self, latitude: float, longitude: float) -> dict:
        api_url = f"https://flood-api.open-meteo.com/v1/flood?latitude={latitude}&longitude={longitude}&daily=river_discharge&forecast_days=1"

        try:
            response = requests.get(api_url)

            if response.status_code == 200:
                data = response.json()
                return data.get('daily', {}).get('river_discharge', {})  # Extract river discharge data
            else:
                logging.error(f"Error fetching river discharge data from Open Meteo Flood API - Status: {response.status_code}, Error: {response.text}")
                return {}  # Return empty dict if failed
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching river discharge data: {e}")
            return {}  # Return empty dict on error
