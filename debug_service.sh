#!/bin/bash

# Script to help debug the wheelchair service
# This will run the start script manually and capture all output

echo "Debugging wheelchair service..."
echo "Running start_with_venv.sh with full output capture"
echo "=================================================="

# Run the script and capture all output
sudo bash -x /home/pi/pi-motor-control-project/start_with_venv.sh > /home/pi/pi-motor-control-project/debug_output.log 2>&1

# Display the output
echo "Script completed with exit code: $?"
echo "Debug output has been saved to: /home/pi/pi-motor-control-project/debug_output.log"
echo "Here's the output:"
echo "----------------"
cat /home/pi/pi-motor-control-project/debug_output.log
