# Variables
APP_NAME := flood_prediction
VENV := venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

# Default target
all: run

# Set up the virtual environment and install dependencies
setup: $(VENV)/bin/activate

$(VENV)/bin/activate:
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt

# Run the Flask app
run: setup
	$(PYTHON) run.py

# Install a new Python package
install:
	$(PIP) install $(pkg)
	$(PIP) freeze > requirements.txt

# Format the code
format:
	black .

# Run linting checks
lint:
	flake8 .

# Clean up virtual environment and cache files
clean:
	rm -rf $(VENV) __pycache__ *.pyc .pytest_cache .coverage

.PHONY: all setup run install format lint clean
