import logging
import requests

class FloodPredictionService:
    def get_flood_prediction(self, latitude: float, longitude: float):
        # Assuming your Flask app is running locally on port 5000
        url = f"http://localhost:5000/predict?lat={latitude}&lon={longitude}"

        try:
            response = requests.get(url)
            return response.json()  # Return the prediction data
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching flood prediction data: {e}")
            return None  # Return None if the API call fails
