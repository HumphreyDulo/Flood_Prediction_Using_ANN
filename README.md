# **Flood Prediction Web Application**

This is a Python Flask application designed for predicting flood probabilities and providing interactive safe zone mapping.

---

### **Prerequisites**

- Python 3.8 or later
- Git
- Virtualenv
- Required Python dependencies (`Flask`, `Leaflet`, `requests`, etc.)
  
---

## **Installation**

To automate the setup, use the following `bash` script:

```bash
#!/bin/bash

# Flood Prediction App Installation Script

# Install necessary packages
echo "Installing Git..."
sleep 2
sudo apt-get install git -y

echo "Installing Python3 and Pip..."
sleep 2
sudo apt-get install python3 python3-pip -y

# Clone the repository
echo "Cloning the Flood Prediction repository..."
sleep 2
git clone https://github.com/yourusername/flood-prediction.git
cd app

# Set up a virtual environment
echo "Setting up a virtual environment..."
sleep 2
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
sleep 2
pip install -r requirements.txt

echo "Installation completed successfully!"
echo "Run 'make run' to start the application."
```
Also running the command: python app.py will work.

## Features****
Predict flood probabilities for specific locations within Nairobi.
Interactive map displaying safe zones within a 5km radius from selected location.
Automated input data retrieval using APIs.
Real-time flood risk calculations.
Dynamic safe zone list display for easy navigation.

## Contact****
For any questions, improvements or feedback, reach out:

Your Name: [humphrey.dulo@strathmore.edu]