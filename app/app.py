from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
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
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate

# Set environment variables
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:dulo@localhost/flood_prediction'
app.config['SECRET_KEY'] = 'Pred1ct10n'

db = SQLAlchemy(app)
migrate = Migrate(app, db)  # Set up migrations
login_manager = LoginManager(app)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

login_manager.login_view = "login"  # Define the login view

# User model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Add name field
    email = db.Column(db.String(120), unique=True, nullable=False)  # Change username to email
    password = db.Column(db.String(9999), nullable=False)
    is_active = db.Column(db.Boolean, default=False)  # Account activation status
    activation_token = db.Column(db.String(200), nullable=True)  # Activation token

# Prediction model
class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    pressure = db.Column(db.Float)
    rain = db.Column(db.Float)
    wind_speed = db.Column(db.Float)
    cloudiness = db.Column(db.Float)
    elevation = db.Column(db.Float)
    employment_agriculture = db.Column(db.Float)
    urban_population = db.Column(db.Float)
    soil_moisture = db.Column(db.Float)
    pop_density = db.Column(db.Float)
    forested_area = db.Column(db.Float)
    river_discharge = db.Column(db.Float)
    cyclone_intensity = db.Column(db.Float)
    daily_temperature = db.Column(db.Float)
    deteriorating_infrastructure = db.Column(db.Float)
    stability = db.Column(db.Float)
    dams_quality = db.Column(db.Float)
    wetland_loss = db.Column(db.Float)
    ineffective_disaster_preparedness = db.Column(db.Float)
    flood_probability = db.Column(db.Float)  # The prediction result

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

from flask_mail import Mail, Message

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'humphrey.dulo@strathmore.edu'  # Replace with your Gmail address
app.config['MAIL_PASSWORD'] = 'nxza jzxm zrrl yrte'     # Replace with your App Password
app.config['MAIL_DEFAULT_SENDER'] = 'humphrey.dulo@strathmore.edu'

mail = Mail(app)


# URLSafeTimedSerializer for token generation
@app.route('/activate/<token>', methods=['GET'])
def activate_account(token):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='email-activation', max_age=86400)  # Token valid for 24 hours
        user = User.query.filter_by(email=email).first()

        if user and not user.is_active:
            user.is_active = True
            user.activation_token = None  # Invalidate the token
            db.session.commit()
            flash('Account activated successfully! You can now log in.', 'success')
            return redirect(url_for('login'))
        elif user and user.is_active:
            flash('Account already activated.', 'info')
            return redirect(url_for('login'))
        else:
            flash('Invalid activation link.', 'danger')
            return redirect(url_for('home'))

    except Exception as e:
        flash('Activation link is invalid or has expired.', 'danger')
        return redirect(url_for('home'))



@app.route('/')
def home():
    return render_template('home.html')

# login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            if not user.is_active:
                flash('Please activate your account before logging in.', 'warning')
                return redirect(url_for('login'))

            session['id'] = user.id
            session['name'] = user.name
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login unsuccessful. Check email and/or password.', 'danger')

    return render_template('login.html')


from werkzeug.security import generate_password_hash

from itsdangerous import URLSafeTimedSerializer

# Generate activation token
def generate_activation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='email-activation')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))

        # Hash the password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Create new user (inactive initially)
        new_user = User(name=name, email=email, password=hashed_password, is_active=False)
        db.session.add(new_user)
        db.session.commit()

        # Generate an activation link
        token = generate_activation_token(new_user.email)  # You can implement a token generator
        activation_link = f"{request.host_url}activate/{token}"

        # Send activation email
        send_activation_email(email, activation_link)

        flash('Your account has been created! Check your email to activate your account.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


from flask_mail import Message

def send_activation_email(email, activation_link):
    subject = "Activate Your Account"
    body = f"""
    Thank you for signing with us!
    
    Please activate your account by clicking the following link:
    {activation_link}
    
    If you did not register for this account, you can safely ignore this email.

    Regards,
    The Team
    """

    # Create a message object
    msg = Message(subject=subject,
                  recipients=[email],
                  body=body,
                  sender=("Nairobi Flood Prediction", app.config['MAIL_USERNAME']))  # Set sender name and email

    try:
        # Send the email using Flask-Mail
        mail.send(msg)
        print(f"Activation email sent to {email}.")
    except Exception as e:
        print(f"Failed to send email. Error: {e}")



# Safezones renderer
@app.route('/safezones')
def safezones():
    if 'id' in session:
        user_id = session['id']
        user_name = session['name']
        # You can now use user_name and user_id in your template or logic
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)
        return render_template('safezones.html', lat=lat, lon=lon, name=user_name, id=user_id)
    else:
        flash('You need to log in first!', 'danger')
        return redirect(url_for('login'))

# Predictions renderer
@app.route('/dashboard')
def dashboard():
    if 'id' in session:
        user_id = session['id']
        user_name = session['name']
        # Use user_name and user_id as needed
        return render_template('dashboard.html', name=user_name, id=user_id)
    else:
        flash('You need to log in first!', 'danger')
        return redirect(url_for('login'))
    
@app.route('/logout')
def logout():
    session.pop('name', None)
    session.pop('id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))


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

                    # Save the features and the prediction result into the database
                    new_prediction = Prediction(
                        temperature=features[0],
                        humidity=features[1],
                        pressure=features[2],
                        rain=features[3],
                        wind_speed=features[4],
                        cloudiness=features[5],
                        elevation=features[6],
                        employment_agriculture=features[7],
                        urban_population=features[8],
                        soil_moisture=features[9],
                        pop_density=features[10],
                        forested_area=features[11],
                        river_discharge=features[12],
                        cyclone_intensity=features[13],
                        daily_temperature=features[14],
                        deteriorating_infrastructure=features[15],
                        stability=features[16],
                        dams_quality=features[17],
                        wetland_loss=features[18],
                        ineffective_disaster_preparedness=features[19],
                        flood_probability=prediction  # The prediction result
                    )
                    db.session.add(new_prediction)
                    db.session.commit()
                    logging.info("Prediction and features successfully saved to the database.")
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
        'deteriorating_infrastructure': 3,  # Placeholder or fetch if available
        'stability': 3,  # Placeholder or fetch if available
        'dams_quality': 3,  # Placeholder or fetch if available
        'wetland_loss': 4,  # Placeholder or fetch if available
        'ineffective_disaster_preparedness': 4,  # Placeholder or fetch if available
    }

    # Return the features to be passed to the model
    return [features[key] for key in feature_mapping]


if __name__ == '__main__':
    app.run(debug=True)