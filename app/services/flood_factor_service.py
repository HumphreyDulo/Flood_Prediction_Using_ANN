import requests
import logging

class FloodFactorService:
    def __init__(self):
        self.base_url = 'https://private-7ae5e3-floods.apiary-mock.com'

    def get_politics(self):
        """Fetch data from the Politics API."""
        return self._fetch_data('/politics')

    def get_infrastructure(self):
        """Fetch data from the Infrastructure API."""
        return self._fetch_data('/infrastructure')

    def get_ineffective_disaster_preparedness(self):
        """Fetch data from the Ineffective Disaster Preparedness API."""
        return self._fetch_data('/ineffectiveDisasterPreparedness')

    def get_dams_quality(self):
        """Fetch data from the Dams Quality API."""
        return self._fetch_data('/damsQuality')

    def get_wetland_loss(self):
        """Fetch data from the Wetland Loss API."""
        return self._fetch_data('/wetLand')

    def _fetch_data(self, endpoint):
        """
        Helper function to fetch data from an API endpoint.

        Args:
            endpoint (str): The API endpoint.

        Returns:
            dict or None: The JSON response as a dictionary, or None if the request fails.
        """
        api_url = f"{self.base_url}{endpoint}"
        try:
            response = requests.get(api_url)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            return response.json()  # Parse JSON response
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching data from {api_url}: {e}")
            return None
