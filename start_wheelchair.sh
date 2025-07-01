#!/bin/bash

# Define paths explicitly
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SRC_DIR="$PROJECT_DIR/src"
LOG_DIR="$PROJECT_DIR/logs"

echo "Smart Wheelchair Control System"
echo "=============================="
echo "Project directory: $PROJECT_DIR"

# Make sure we're in the expected directory structure
if [ ! -d "$SRC_DIR" ]; then
    echo "Error: src directory not found at $SRC_DIR"
    echo "Please check your installation"
    exit 1
fi

# Ensure the script is run with sudo
if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run with sudo for hardware access"
    echo "Please run: sudo $0"
    exit 1
fi

# Clean up GPIO pins if needed
echo "Cleaning up GPIO pins from previous runs..."
python3 -c "import RPi.GPIO as GPIO; GPIO.cleanup()" 2>/dev/null

# Ensure logs directory exists
echo "Setting up logs directory..."
mkdir -p "$LOG_DIR"

# Run the program with full error capture
echo "Starting wheelchair control system..."
cd "$SRC_DIR"
python3 run_with_error_capture.py "$@"

# Return value
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    echo "Program exited with error code $EXIT_CODE"
    echo "Check the logs at $LOG_DIR/error_log.txt for details"
else
    echo "Program exited successfully"
fi

exit $EXIT_CODE
