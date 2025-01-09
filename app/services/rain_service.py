import requests
import logging

class RainService:
    def __init__(self):
        self.api_key = 'b9df066214c147f68c1110214250901'  # Your WeatherAPI key

    def get_rain_data(self, latitude: float, longitude: float) -> float:
        url = f"https://api.weatherapi.com/v1/current.json?key={self.api_key}&q={latitude},{longitude}"

        try:
            response = requests.get(url)
            data = response.json()

            if 'current' in data and 'precip_in' in data['current']:
                return data['current']['precip_in']  # Return the rain data in inches
            else:
                logging.warning(f"Rain data not available for coordinates: {latitude}, {longitude}")
                return 0  # Return 0 if no rain data available
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching rain data for coordinates: {latitude}, {longitude}. Error: {e}")
            return 0  # Return 0 if there is an error
