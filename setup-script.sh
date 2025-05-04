#!/bin/bash

# Exit on any error
set -e

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null
then
    echo "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv scraper_env

# Activate virtual environment
echo "Activating virtual environment..."
source scraper_env/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Copy config template if config doesn't exist
if [ ! -f config.json ]; then
    cp config.template.json config.json
    echo "Created config.json from template. Please edit with your Reddit API credentials."
fi

echo "Setup complete! Activate the virtual environment with:"
echo "source scraper_env/bin/activate"
echo "Then run the scraper with:"
echo "python scrape_reddit.py"

# Deactivate virtual environment
deactivate