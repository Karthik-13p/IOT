#!/bin/bash
# Script to install dependencies in the system Python environment

echo "Installing dependencies in the system Python environment..."

# Install Python dependencies
echo "Installing Python packages..."
sudo pip3 install flask pyserial pynmea2

echo "Dependencies installed successfully!"
echo "You can now run the main.py script with: sudo python src/main.py"
