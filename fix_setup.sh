#!/bin/bash
# Fix permissions and install dependencies

# Set text colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Raspberry Pi Motor Control Project Setup ===${NC}"
echo -e "${YELLOW}This script will fix permissions and install dependencies${NC}"
echo ""

# Create logs directory with proper permissions
echo -e "${YELLOW}Creating logs directory with correct permissions...${NC}"
mkdir -p logs
sudo chmod 777 logs

# Install Python dependencies
echo -e "${YELLOW}Installing required Python packages...${NC}"
sudo pip3 install flask pyserial pynmea2 RPi.GPIO

# Additional hardware-related packages
echo -e "${YELLOW}Installing hardware support packages...${NC}"
sudo apt-get update
sudo apt-get install -y python3-rpi.gpio python3-pigpio

# Set executable permissions for scripts
echo -e "${YELLOW}Setting executable permissions for scripts...${NC}"
chmod +x *.py
chmod +x *.sh
chmod +x src/*.py
chmod +x src/*/*.py

# Create systemd service file
echo -e "${YELLOW}Creating systemd service file...${NC}"
cat > wheelchair.service << 'EOL'
[Unit]
Description=Motor Control Web Interface
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/pi-motor-control-project
ExecStart=/usr/bin/python3 src/main.py
Restart=always
RestartSec=5
StandardOutput=inherit
StandardError=inherit

[Install]
WantedBy=multi-user.target
EOL

# Ask if service should be installed
echo -e "${YELLOW}Do you want to install the service to start automatically on boot? (y/n)${NC}"
read -r install_service

if [[ "$install_service" == "y" || "$install_service" == "Y" ]]; then
    sudo cp wheelchair.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable wheelchair.service
    echo -e "${GREEN}Service installed and enabled to start on boot${NC}"
    echo -e "${YELLOW}To start the service now, run: sudo systemctl start wheelchair.service${NC}"
fi

echo ""
echo -e "${GREEN}Setup complete!${NC}"
echo -e "${YELLOW}You can now run:${NC}"
echo -e "  sudo python3 src/main.py               ${GREEN}# To start the web interface${NC}"
echo -e "  sudo python3 test_optimized_motors.py  ${GREEN}# To test motor performance${NC}"
