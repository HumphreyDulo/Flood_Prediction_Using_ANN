import sys
import joblib
import numpy as np
from tensorflow.keras.models import load_model  # type: ignore
import pandas as pd
import json

# Path to model, scaler, and features (replace with your actual paths)
model_path = r"python_model/flood_model.h5"
scaler_path = r"python_model/scaler.pkl"
features_path = r"python_model/features.pkl"

# Load model, scaler, and feature names
scaler = joblib.load(scaler_path)
model = load_model(model_path)
features = joblib.load(features_path)


def make_prediction(input_data):
    try:
        # Convert input string to list of floats
        input_data = [float(x) for x in input_data.split(',')]

        # Create a DataFrame for the input data
        input_df = pd.DataFrame([input_data], columns=features)

        # Scale the input data
        scaled_input = scaler.transform(input_df)

        # Get the model's prediction
        prediction = model.predict(scaled_input)

        print(f"Prediction from model: {prediction}")  # Debug: Print prediction before conversion

        # Convert NumPy float32 to Python float
        prediction_value = float(prediction[0][0]) 

        print(f"Prediction value: {prediction_value}")  # Debug: Print converted value

        return json.dumps({'prediction': prediction_value}) 

    except Exception as e:
        return json.dumps({'error': str(e)})


if __name__ == '__main__':
    try:
        if len(sys.argv) != 2:
            raise ValueError("Incorrect number of arguments. Please provide the input data.")

        input_str = sys.argv[1]  # Get input data from command-line arguments
        prediction = make_prediction(input_str)
        print(prediction)

    except Exception as e:
        print(json.dumps({'error': str(e)}))