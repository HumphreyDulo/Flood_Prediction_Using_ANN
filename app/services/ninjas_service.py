import requests
import logging
import json  # Import json for pretty printing

class NinjasService:
    def __init__(self):
        self.api_url = "https://api.api-ninjas.com/v1/country"
        self.api_key = '4rQd3nJgnPUrIQ/K9WFK0Q==lmfR5CAAT1Y92rOo'  # Your Ninjas API Key

    def get_country_data(self) -> dict:
        country_name = "Kenya"
        try:
            headers = {
                'X-Api-Key': self.api_key
            }
            params = {
                'name': country_name
            }
            response = requests.get(self.api_url, headers=headers, params=params)

            if response.status_code == 200:
                country_data = response.json()
                # Extract specific fields and apply defaults as needed
                employment_agriculture = country_data[0].get('employment_agriculture', 0)
                urban_population = country_data[0].get('urban_population', 0)
                pop_density = country_data[0].get('pop_density', 0)
                forested_area = 100 - country_data[0].get('forested_area', 0)  # Apply 100 - value for forested area

                # Return the extracted data
                return {
                    'employment_agriculture': employment_agriculture,
                    'urban_population': urban_population,
                    'pop_density': pop_density,
                    'forested_area': forested_area
                }
            else:
                logging.error(f"Failed to fetch country data from Ninjas API - Country: {country_name}, Status: {response.status_code}, Error: {response.text}")
                return {}  # Return empty dictionary if failed
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching country data: {e}")
            return {}  # Return empty dictionary on error


# Example usage
ninjas_service = NinjasService()
country_data = ninjas_service.get_country_data()

# Use json.dumps() for better formatting
print(f"Country data: {json.dumps(country_data, indent=4)}")
