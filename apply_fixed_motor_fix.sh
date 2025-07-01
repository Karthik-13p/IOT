#!/bin/bash
# Apply the web motor interface fixes with the corrected script
# This script ensures that the motor control works properly in the web interface

# Set text colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Applying Web Motor Interface Fix ===${NC}"

# 1. Check if running as root
if [ $(id -u) -ne 0 ]; then
    echo -e "${RED}Error: This script must be run as root${NC}"
    echo "Please run with sudo: sudo ./apply_web_motor_fix.sh"
    exit 1
fi

# 2. Stop any running services
echo -e "${YELLOW}Stopping any running services...${NC}"
systemctl stop wheelchair 2>/dev/null || true
pkill -f "python.*main.py" 2>/dev/null || true
sleep 1

# 3. Apply the fix by running the corrected Python script
echo -e "${YELLOW}Applying fixes...${NC}"
python3 apply_web_motor_fix_corrected.py

# 4. Run the test script
echo -e "${YELLOW}Testing the fix...${NC}"
python3 test_motor_fixes.py

# 5. Complete
echo -e "${GREEN}Fix application complete!${NC}"
echo -e "You can now restart your web interface with:"
echo -e "  ${GREEN}sudo python3 src/main.py${NC}"
echo -e "Or restart the service with:"
echo -e "  ${GREEN}sudo systemctl restart wheelchair${NC}"
