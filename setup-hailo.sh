#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Setting up Hailo-specific requirements..."

# Check if hailo-all is installed
if ! dpkg -l | grep -q hailo-all; then
    echo "Error: hailo-all package not found!"
    echo "Please install it first with: sudo apt install hailo-all"
    exit 1
fi

# Check if Hailo software is installed
if ! command -v hailortcli &> /dev/null; then
    echo "Error: Hailo software not found!"
    echo "Please install Hailo software first by following:"
    echo "https://www.raspberrypi.com/documentation/computers/ai.html#getting-started"
    exit 1
fi

# Verify Hailo device is recognized
echo "Checking Hailo device..."
if ! hailortcli fw-control identify &> /dev/null; then
    echo "Error: Hailo device not detected!"
    echo "Please check your hardware connection and drivers"
    exit 1
fi

# Check GStreamer Hailo plugins
echo "Checking GStreamer Hailo plugins..."
if ! gst-inspect-1.0 hailotools &> /dev/null; then
    echo "Error: Hailo GStreamer plugins not found!"
    echo "Please ensure TAPPAS Core is properly installed"
    exit 1
fi

# Create hailo virtual environment with access to system packages
HAILO_VENV="venv_hailo"
echo "Creating Hailo virtual environment at $HAILO_VENV..."
python3 -m venv --system-site-packages "$HAILO_VENV"

# Activate the virtual environment
source "$HAILO_VENV/bin/activate"

# Upgrade pip
pip install --upgrade pip

# Install base Python dependencies
echo "Installing base Python dependencies..."
pip install "numpy<2.0.0" setproctitle loguru pillow

# Get device architecture
echo "Getting device architecture..."
DEVICE_ARCH=$(hailortcli fw-control identify | tr -d '\0' | grep "Device Architecture" | awk -F": " '{print $2}')
if [ -n "$DEVICE_ARCH" ]; then
    export DEVICE_ARCHITECTURE="$DEVICE_ARCH"
    echo "DEVICE_ARCHITECTURE is set to: $DEVICE_ARCHITECTURE"
else
    echo "Warning: Could not determine device architecture"
fi

# Set TAPPAS environment variables
if pkg-config --exists hailo-tappas-core; then
    export TAPPAS_POST_PROC_DIR=$(pkg-config --variable=tappas_postproc_lib_dir hailo-tappas-core)
    echo "TAPPAS_POST_PROC_DIR set to $TAPPAS_POST_PROC_DIR"
else
    echo "Warning: hailo-tappas-core not found"
fi

# Clone and install hailo-apps-infra directly
echo "Installing Hailo apps infrastructure..."
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"
git clone https://github.com/hailo-ai/hailo-apps-infra.git
cd hailo-apps-infra
python3 setup.py install

# Cleanup
cd -
rm -rf "$TEMP_DIR"

echo "Hailo setup completed successfully!"
echo "To activate the Hailo environment in the future, run:"
echo "source $HAILO_VENV/bin/activate && python start.py"
