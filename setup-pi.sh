#!/bin/bash

# Update and upgrade the system
sudo apt-get update
sudo apt-get upgrade -y

# Install Python 3 and pip
sudo apt-get install -y python3 python3-pip python3-venv

# Create project directory
mkdir -p water_cannon_project
cd water_cannon_project

# Clone YOLOv10 repository
git clone https://github.com/THU-MIG/yolov10.git

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r yolov10/requirements.txt
pip install opencv-python flask

# Install PyTorch for Raspberry Pi
pip install torch torchvision

echo "Setup complete for Raspberry Pi."