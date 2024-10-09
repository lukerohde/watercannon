#!/bin/bash

# Update and upgrade the system
sudo apt-get update
sudo apt-get upgrade -y

# Install Python 3 and pip
sudo apt-get install -y python3 python3-pip python3-venv python3-kms++

# make way for rpi-lgpio on rpi5
sudo apt remove python3-rpi.gpio

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install common requirements
pip install -r requirements.txt

# Install Pi specific requirements
cp -R /usr/lib/python3/dist-packages/libcamera ./venv/lib/python3.11/site-packages/
cp -R /usr/lib/python3/dist-packages/pykms ./venv/lib/python3.11/site-packages/

pip install picamera2

echo "Setup complete for Raspberry Pi."
echo "Make sure you have these two lines in your /boot/firmware/config.txt"
echo "dtparam=i2c_arm=on"
echo "dtparam=i2c1=on"