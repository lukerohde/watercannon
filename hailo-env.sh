#!/bin/bash

# Get device architecture
DEVICE_ARCH=$(hailortcli fw-control identify | tr -d '\0' | grep "Device Architecture" | awk -F": " '{print $2}')
if [ -n "$DEVICE_ARCH" ]; then
    export DEVICE_ARCHITECTURE="$DEVICE_ARCH"
    echo "DEVICE_ARCHITECTURE is set to: $DEVICE_ARCHITECTURE"
else
    echo "Warning: Could not determine device architecture"
fi

# Set post-processing directory if using Hailo's post-processing libraries
if pkg-config --exists hailo-tappas-core; then
    export TAPPAS_POST_PROC_DIR=$(pkg-config --variable=tappas_postproc_lib_dir hailo-tappas-core)
    echo "TAPPAS_POST_PROC_DIR set to $TAPPAS_POST_PROC_DIR"
fi

# Activate the Hailo virtual environment
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$SCRIPT_DIR/venv_hailo/bin/activate"
