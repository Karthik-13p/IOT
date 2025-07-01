#!/bin/bash
# Setup script for Raspberry Pi motor control project
# This script installs system packages and Python dependencies

echo "Setting up Raspberry Pi motor control project..."

# Update package lists
echo "Updating package lists..."
sudo apt-get update

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get install -y python3-numpy python3-opencv python3-pip python3-dev

# Install Python dependencies from requirements file
echo "Installing Python dependencies..."
pip3 install --no-cache-dir -r requirements_pi.txt

# Set up the service
echo "Setting up systemd service..."
sudo cp wheelchair.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable wheelchair.service

echo "Setup complete! You can start the service with: sudo systemctl start wheelchair.service"
