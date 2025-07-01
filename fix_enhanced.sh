#!/bin/bash
# Enhanced fix script for motor control project

# Set text colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Raspberry Pi Motor Control Project Enhanced Setup ===${NC}"
echo -e "${YELLOW}This script will fix all remaining issues${NC}"
echo ""

# 1. Create logs directory with proper permissions
echo -e "${YELLOW}Creating logs directory with correct permissions...${NC}"
mkdir -p logs
sudo chmod 777 logs

# 2. Set up a Python virtual environment
echo -e "${YELLOW}Setting up Python virtual environment...${NC}"
sudo apt-get update
sudo apt-get install -y python3-venv python3-dev

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install required packages in the virtual environment
echo -e "${YELLOW}Installing Python packages in virtual environment...${NC}"
pip install flask pyserial pynmea2 RPi.GPIO

# 3. Fix the reset_gpio argument in main.py
echo -e "${YELLOW}Fixing the reset_gpio argument issue in main.py...${NC}"
sed -i 's/motor\.cleanup_motors(reset_gpio=True)/motor\.cleanup_motors()/g' src/main.py

# 4. Create wrapper scripts that use the virtual environment
echo -e "${YELLOW}Creating wrapper scripts...${NC}"

# Create a script to run the main application with the virtual environment
cat > run_app.sh << 'EOL'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
sudo python3 src/main.py
EOL

# Create a script to run the motor test with the virtual environment
cat > run_motor_test.sh << 'EOL'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
sudo python3 test_optimized_motors.py
EOL

# Make scripts executable
chmod +x run_app.sh run_motor_test.sh

# 5. Create an updated service file that uses the virtual environment
echo -e "${YELLOW}Creating updated systemd service file...${NC}"
cat > wheelchair_venv.service << 'EOL'
[Unit]
Description=Motor Control Web Interface with Virtual Environment
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/pi-motor-control-project
ExecStart=/home/pi/pi-motor-control-project/venv/bin/python3 src/main.py
Restart=always
RestartSec=5
StandardOutput=inherit
StandardError=inherit

[Install]
WantedBy=multi-user.target
EOL

# Ask if service should be installed
echo -e "${YELLOW}Do you want to install the updated service to start automatically on boot? (y/n)${NC}"
read -r install_service

if [[ "$install_service" == "y" || "$install_service" == "Y" ]]; then
    sudo cp wheelchair_venv.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable wheelchair_venv.service
    echo -e "${GREEN}Service installed and enabled to start on boot${NC}"
    echo -e "${YELLOW}To start the service now, run: sudo systemctl start wheelchair_venv.service${NC}"
fi

echo ""
echo -e "${GREEN}Enhanced setup complete!${NC}"
echo -e "${YELLOW}You can now run:${NC}"
echo -e "  ./run_app.sh            ${GREEN}# To start the web interface${NC}"
echo -e "  ./run_motor_test.sh     ${GREEN}# To test motor performance${NC}"
echo ""
echo -e "${YELLOW}The virtual environment is located at: ${GREEN}$(pwd)/venv${NC}"
