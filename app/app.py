from flask import Flask, render_template, request, jsonify
import subprocess
import logging
from services.weather_service import WeatherService
from services.elevation_service import ElevationService
from services.ninjas_service import NinjasService  # Placeholder, remove if not used
from services.soil_service import SoilService
from services.cyclone_service import CycloneService
from services.river_service import RiverService
from services.climate_service import ClimateService
from services.rain_service import RainService
import os
import re
import json

# Set environment variables
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Initialize Flask app
app = Flask(__name__)

# Initialize services
weather_service = WeatherService()
elevation_service = ElevationService()
ninjas_service = NinjasService() 
soil_service = SoilService()
cyclone_service = CycloneService()
river_service = RiverService()
climate_service = ClimateService()
rain_service = RainService()

# Setup logging
logging.basicConfig(level=logging.INFO)

# Find Safe Zones Renderer
@app.route('/safezones')
def safezones():
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    return render_template('safezones.html', lat=lat, lon=lon)


@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/flood-prediction', methods=['GET'])
def flood_prediction():
    lat = request.args.get('lat')
    lng = request.args.get('lng')

    if lat and lng:
        try:
            # Fetch data from all services
            weather_data = weather_service.get_weather_data(lat, lng)
            rain_data = rain_service.get_rain_data(lat, lng)
            elevation = elevation_service.get_elevation(lat, lng)
            soil_moisture = soil_service.get_soil_moisture(lat, lng)
            river_discharge = river_service.get_river_discharge(lat, lng)
            cyclone_response = cyclone_service.get_cyclone_data(lat, lng) 
            daily_temperature = climate_service.get_daily_temperature(lat, lng)
            country_data = ninjas_service.get_country_data()  

            # Handle potential missing data
            if not weather_data:
                return jsonify({'error': "Error fetching weather data."})
            if rain_data is None:
                return jsonify({'error': "Error fetching rain data."})
            if elevation is None:
                return jsonify({'error': "Error fetching elevation data."})
            if soil_moisture is None:
                return jsonify({'error': "Error fetching soil moisture data."})
            if river_discharge is None:
                return jsonify({'error': "Error fetching river discharge data."})
            if daily_temperature is None:
                return jsonify({'error': "Error fetching climate data."})
            if country_data is None:
                return jsonify({'error': "Error fetching country data."})

            # Handle cyclone data
            if cyclone_response and "warn_no_data" in cyclone_response["error"]:
                cyclone_intensity = 0.0
            elif cyclone_response and "response" in cyclone_response: 
                try:
                    cyclone_intensity = float(cyclone_response["response"]["intensity"])
                except (KeyError, ValueError):
                    cyclone_intensity = 0.0  
            else:
                cyclone_intensity = 0.0  

            # Extract features with 2 decimal places
            features = extract_features(weather_data, rain_data, elevation, soil_moisture, river_discharge, cyclone_intensity, daily_temperature, country_data)

            # Convert features to a comma-separated string
            features_str = ",".join(map(lambda x: "{:.4f}".format(x), features)) 

            # Log the features string
            logging.info(f"Features: {features_str}") 

            # Call predict.py with features
            python_path =  "C:/Python312/python.exe"  # Replace with your Python executable path
            script_path = "C:/Users/User/Flood_Prediction_Using_ANN/app/predict.py"  # Replace with the path to your predict.py script
            command = [python_path, script_path, features_str]
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')

            # Clean the stdout to extract only the JSON part
            cleaned_stdout = result.stdout.strip()

            # Use regex to find the JSON part in the output
            json_match = re.search(r'(\{.*\})', cleaned_stdout)

            if json_match:
                cleaned_json = json_match.group(1)  # Extract the JSON part
                logging.info(f"Cleaned JSON from stdout: {cleaned_json}")

                try:
                    # Parse the cleaned JSON
                    prediction_data = json.loads(cleaned_json)
                    prediction = prediction_data['prediction']
                    return jsonify({'prediction': prediction})
                except json.JSONDecodeError:
                    logging.error(f"Error parsing JSON: {cleaned_json}")
                    return jsonify({'error': "Error parsing prediction result from predict.py"})
            else:
                logging.error(f"Failed to extract JSON from stdout: {cleaned_stdout}")
                return jsonify({'error': "Failed to extract prediction data from predict.py"})

        except Exception as e:
            return jsonify({'error': str(e)})

    else:
        return jsonify({'error': "Invalid coordinates provided."})

def extract_features(weather_data, rain_data, elevation, soil_moisture, river_discharge, cyclone_intensity, daily_temperature, country_data):
    # Feature mapping to match model names
    feature_mapping = {
        'temperature': 'Encroachments',
        'humidity': 'Watersheds',
        'pressure': 'InadequatePlanning',
        'rain': 'MonsoonIntensity',
        'wind_speed': 'Landslides',
        'cloudiness': 'DrainageSystems',
        'elevation': 'TopographyDrainage',
        'employment_agriculture': 'AgriculturalPractices',
        'urban_population': 'Urbanization',
        'soil_moisture': 'Siltation',
        'pop_density': 'PopulationScore',
        'forested_area': 'Deforestation',
        'river_discharge': 'RiverManagement',
        'cyclone_intensity': 'CoastalVulnerability',
        'daily_temperature': 'ClimateChange',
        'deteriorating_infrastructure': 'DeterioratingInfrastructure',
        'stability': 'PoliticalFactors',
        'dams_quality': 'DamsQuality',
        'wetland_loss': 'WetlandLoss',
        'ineffective_disaster_preparedness': 'IneffectiveDisasterPreparedness',
    }

    # Extract values from country_data
    employment_agriculture = country_data.get('employment_agriculture', 0)
    urban_population = country_data.get('urban_population', 0)
    pop_density = country_data.get('pop_density', 0)
    forested_area = country_data.get('forested_area', 0)

    # Mapping the fetched data to the features
    features = {
        'temperature': weather_data['main']['temp'] / 10,
        'humidity': weather_data['main']['humidity'] / 10,
        'pressure': weather_data['main']['pressure'] / 100,
        'rain': rain_data if rain_data else 0,
        'wind_speed': weather_data['wind']['speed'] / 10,
        'cloudiness': weather_data['clouds']['all'] / 10,
        'elevation': elevation / 100,
        'employment_agriculture': employment_agriculture / 10,  # Value extracted from country_data
        'urban_population': urban_population,  # Value extracted from country_data
        'soil_moisture': soil_moisture / 10,
        'pop_density': pop_density / 10,  # Value extracted from country_data
        'forested_area': 100 - forested_area,  # Correct calculation for forested_area
        'river_discharge': river_discharge[0] / 10 if river_discharge else 0,
        'cyclone_intensity': cyclone_intensity,
        'daily_temperature': daily_temperature / 10,
        'deteriorating_infrastructure': 0,  # Placeholder or fetch if available
        'stability': 0,  # Placeholder or fetch if available
        'dams_quality': 0,  # Placeholder or fetch if available
        'wetland_loss': 0,  # Placeholder or fetch if available
        'ineffective_disaster_preparedness': 0,  # Placeholder or fetch if available
    }

    # Return the features to be passed to the model
    return [features[key] for key in feature_mapping]


if __name__ == '__main__':
    app.run(debug=True)