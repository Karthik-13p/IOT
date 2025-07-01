#!/bin/bash
# Script to install missing dependencies for the smart wheelchair project

echo "Installing missing dependencies for the smart wheelchair project..."

# Update package lists
sudo apt-get update

# Install Python dependencies
echo "Installing Python packages..."
sudo pip3 install flask pyserial pynmea2

echo "Dependencies installed successfully!"
echo "You can now run the main.py script with: sudo python src/main.py"
