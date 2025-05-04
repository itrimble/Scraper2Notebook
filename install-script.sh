#!/bin/bash

# Ensure script stops on any error
set -e

# Check for Python 3.8+
if ! python3 -c 'import sys; assert sys.version_info >= (3,8)' &> /dev/null
then
    echo "Error: Python 3.8 or higher is required."
    exit 1
fi

# Create virtual environment if not exists
if [ ! -d "scraper_env" ]; then
    python3 -m venv scraper_env
fi

# Activate virtual environment
source scraper_env/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Install Ollama (if not already installed)
if ! command -v ollama &> /dev/null
then
    echo "Ollama not found. Installing..."
    curl https://ollama.ai/install.sh | sh
fi

# Pull default model (replace with your preferred model)
ollama pull llama2

echo "Installation complete!"
echo "Activate the environment with: source scraper_env/bin/activate"
echo "Default model llama2 pulled."

# Deactivate virtual environment
deactivate