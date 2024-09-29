#!/bin/bash

# Install Homebrew if not installed
which -s brew
if [[ $? != 0 ]] ; then
    echo "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    # git -C /opt/homebrew/Library/Taps/homebrew/homebrew-core fetch --unshallow
    # git -C /opt/homebrew/Library/Taps/homebrew/homebrew-cask fetch --unshallow
    brew update
fi 

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

echo "Setup complete for macOS."