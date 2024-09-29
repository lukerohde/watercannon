#!/bin/bash

# Update and upgrade the system
sudo apt-get update
sudo apt-get upgrade -y

# Install Python 3 and pip
sudo apt-get install -y python3 python3-pip python3-venv

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

echo "Setup complete for Raspberry Pi."