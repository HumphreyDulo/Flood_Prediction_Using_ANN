import requests
import logging

class WeatherService:
    def __init__(self):
        self.api_key = '90c9d94b79ff4026e46958f11d7f7fd8'  # Replace with your actual API key
        self.api_url = "http://api.openweathermap.org/data/2.5/weather"

    def get_weather_data(self, lat: float, lng: float) -> dict:
        try:
            params = {
                'lat': lat,
                'lon': lng,
                'appid': self.api_key,
                'units': 'metric'  # Fetch data in metric units
            }
            response = requests.get(self.api_url, params=params)

            if response.status_code == 200:
                return response.json()  # Return the parsed JSON data
            else:
                logging.error(f"Failed to fetch weather data - Status: {response.status_code}, Error: {response.text}")
                return {}
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching weather data: {e}")
            return {}
