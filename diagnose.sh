#!/bin/bash

# Define project path explicitly
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SRC_DIR="$PROJECT_DIR/src"

echo "===================================="
echo "Smart Wheelchair Diagnostic Utility"
echo "===================================="
echo "Project directory: $PROJECT_DIR"

# Check if source directory exists
if [ ! -d "$SRC_DIR" ]; then
    echo "❌ Source directory not found at $SRC_DIR"
    echo "Please check your installation"
    exit 1
else
    echo "✅ Source directory found"
fi

# Check if main.py exists
if [ ! -f "$SRC_DIR/main.py" ]; then
    echo "❌ Main program not found at $SRC_DIR/main.py"
    exit 1
else
    echo "✅ Main program found"
fi

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
else
    PYTHON_VERSION=$(python3 --version)
    echo "✅ Python installed: $PYTHON_VERSION"
fi

# Check for key Python modules
echo ""
echo "Checking Python modules..."
MODULES=("RPi.GPIO" "flask" "serial" "pynmea2")
MISSING_MODULES=()

for MODULE in "${MODULES[@]}"; do
    if python3 -c "import $MODULE" &> /dev/null; then
        echo "  ✅ $MODULE installed"
    else
        echo "  ❌ $MODULE not installed"
        MISSING_MODULES+=("$MODULE")
    fi
done

# Check GPIO access
echo ""
echo "Checking GPIO access..."
if sudo python3 -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); GPIO.setup(21, GPIO.OUT); GPIO.cleanup()" &> /dev/null; then
    echo "  ✅ GPIO access working"
else
    echo "  ❌ GPIO access failed"
fi

# Check for hardware interfaces
echo ""
echo "Checking hardware interfaces..."

# Check for serial ports
if ls /dev/ttyAMA0 &> /dev/null || ls /dev/ttyS0 &> /dev/null; then
    echo "  ✅ Serial ports found:"
    ls /dev/tty* | grep -E "AMA|S0|USB" | sed 's/^/     /'
else
    echo "  ❌ Serial ports not found"
fi

# Summary and auto-fix offer
echo ""
if [ ${#MISSING_MODULES[@]} -gt 0 ]; then
    echo "Missing modules: ${MISSING_MODULES[*]}"
    echo ""
    echo "Would you like to install missing dependencies? (y/n)"
    read -r ANSWER
    
    if [ "$ANSWER" == "y" ]; then
        echo "Installing required packages..."
        sudo apt-get update
        sudo apt-get install -y python3-pip python3-serial
        sudo pip3 install pyserial pynmea2 flask --force-reinstall
        echo "Dependencies installed!"
    fi
fi

echo ""
echo "Diagnostic complete. To start the wheelchair system, run:"
echo "  sudo $PROJECT_DIR/start_wheelchair.sh"
echo ""
echo "For more options:"
echo "  sudo $PROJECT_DIR/start_wheelchair.sh --help"
echo ""
