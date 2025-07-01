#!/bin/bash
#
# Web Motor Interface Fix Application Script
#
# This script applies the motor control fixes to the web interface,
# stops and restarts the service, and verifies the fix was applied correctly.
#
# Run as: sudo bash apply_web_motor_fix.sh
#

# Ensure script is run as root
if [ "$(id -u)" -ne 0 ]; then
   echo "This script must be run as root" 
   echo "Please run with: sudo bash apply_web_motor_fix.sh"
   exit 1
fi

echo "===== Applying Web Motor Interface Fix ====="
echo "This script will fix motor control issues in the web interface."

# Directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Stop the web service if running
echo -e "\n--- Stopping web service if running ---"
if systemctl is-active --quiet wheelchair.service; then
    echo "Stopping wheelchair.service..."
    systemctl stop wheelchair.service
    sleep 1
fi

# Apply the fix
echo -e "\n--- Applying fixes ---"
python3 "$SCRIPT_DIR/apply_web_motor_fix_final.py" || {
    echo "Error: Failed to apply fix"
    exit 1
}

# Run the test to verify fix
echo -e "\n--- Testing the fix ---"
python3 "$SCRIPT_DIR/test_motor_fixes.py" || {
    echo "Warning: Test finished with errors"
    echo "You may need to investigate further"
}

# Restart the service
echo -e "\n--- Restarting web service ---"
if [ -f /etc/systemd/system/wheelchair.service ]; then
    systemctl daemon-reload
    systemctl start wheelchair.service
    sleep 2
    if systemctl is-active --quiet wheelchair.service; then
        echo "Web service started successfully"
    else
        echo "Warning: Failed to start web service"
    fi
else
    echo "No service found - skipping service restart"
    echo "You'll need to start the web app manually"
fi

echo -e "\n===== Fix Application Complete ====="
echo "The motor control issues in the web interface should now be fixed."
echo "You can test the web interface by accessing it in your browser."

exit 0
