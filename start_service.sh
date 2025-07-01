#!/bin/bash

# Define paths explicitly
PROJECT_DIR="/home/pi/pi-motor-control-project"
SRC_DIR="$PROJECT_DIR/src"
LOG_DIR="$PROJECT_DIR/logs"
VENV_DIR="$PROJECT_DIR/.venv"
VENV_PYTHON="$VENV_DIR/bin/python"

echo "Smart Wheelchair Control System (Service Mode)"
echo "=============================================="
echo "Project directory: $PROJECT_DIR"
echo "Using virtual environment at: $VENV_DIR"

# Ensure logs directory exists
mkdir -p "$LOG_DIR"

# Log file for this run
LOG_FILE="$LOG_DIR/service_startup.log"
echo "$(date): Service starting" > "$LOG_FILE"

# Make sure we're in the expected directory structure
if [ ! -d "$SRC_DIR" ]; then
    echo "Error: src directory not found at $SRC_DIR" | tee -a "$LOG_FILE"
    exit 1
fi

# Ensure the virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Error: Virtual environment not found at $VENV_DIR" | tee -a "$LOG_FILE"
    exit 1
fi

# Check if Python exists in the virtual environment
if [ ! -f "$VENV_PYTHON" ]; then
    echo "Error: Python not found at $VENV_PYTHON" | tee -a "$LOG_FILE"
    exit 1
fi

# Clean up GPIO pins if needed
echo "Cleaning up GPIO pins from previous runs..." | tee -a "$LOG_FILE"
$VENV_PYTHON -c "import RPi.GPIO as GPIO; GPIO.cleanup()" 2>/dev/null

# Change to the source directory
cd "$SRC_DIR"
echo "Changed to directory: $(pwd)" | tee -a "$LOG_FILE"

# Run the program with the virtual environment Python
echo "Starting wheelchair control system..." | tee -a "$LOG_FILE"
$VENV_PYTHON main.py 2>&1 | tee -a "$LOG_FILE"

# Return value
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    echo "Program exited with error code $EXIT_CODE" | tee -a "$LOG_FILE"
else
    echo "Program exited successfully" | tee -a "$LOG_FILE"
fi

exit $EXIT_CODE
