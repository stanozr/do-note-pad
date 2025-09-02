#!/bin/bash

# DoNotePad Setup Script - Flet Version

echo "Setting up DoNotePad (Flet Version)..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Check if libmpv is available (required for Flet)
if ! ldconfig -p | grep -q libmpv; then
    echo "Warning: libmpv not found. Installing system dependencies..."
    echo "You may need to run: sudo apt install libmpv2 libmpv-dev"
    echo "If libmpv.so.1 is missing, you may need to create a symlink:"
    echo "sudo ln -s /usr/lib/x86_64-linux-gnu/libmpv.so.2 /usr/lib/x86_64-linux-gnu/libmpv.so.1"
fi

# Make run script executable
chmod +x run.sh

echo "Setup complete!"
echo "Run the application with: ./run.sh"
echo "The application will be available at: http://localhost:8550"
