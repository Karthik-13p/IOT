# Smart Wheelchair Control System - Setup and Usage Guide

This document provides comprehensive instructions for setting up and using the Raspberry Pi-based smart wheelchair control system.

## System Overview

The Smart Wheelchair Control System is a Raspberry Pi-based solution that provides:

1. Motor control for wheelchair movement
2. Obstacle detection and avoidance using ultrasonic sensors
3. Live camera feed via IP webcam
4. Web-based control interface accessible from any device
5. GPS location tracking (optional)

## Hardware Requirements

- Raspberry Pi (3B+ or 4 recommended)
- Motor driver board (compatible with 4 motors)
- Ultrasonic distance sensors (HC-SR04)
- Power supply (adequate for motors and Pi)
- Android phone with IP Webcam app (or Raspberry Pi Camera)
- Wheelchair frame with motors

## Wiring Guide

### Motor Connections
Connect the motors to the motor driver board according to the GPIO pin configuration in `config/settings.json`:

```
Motor 1 (Left Front):
- PWM: GPIO 12
- IN1: GPIO 23
- IN2: GPIO 24

Motor 2 (Right Front):
- PWM: GPIO 13
- IN1: GPIO 27
- IN2: GPIO 22

Motor 3 (Left Rear):
- PWM: GPIO 19
- IN1: GPIO 5
- IN2: GPIO 6

Motor 4 (Right Rear):
- PWM: GPIO 26
- IN1: GPIO 16
- IN2: GPIO 20
```

### Ultrasonic Sensor Connections
Connect the ultrasonic sensor to the following GPIO pins:
- Trigger: GPIO 18
- Echo: GPIO 17



## Software Setup

### 1. Install Required Packages

```bash
# Update system packages
sudo apt update
sudo apt upgrade -y

# Install required system dependencies
sudo apt install -y python3-pip python3-dev python3-opencv

# Install Python dependencies
cd /home/pi/pi-motor-control-project
sudo pip3 install -r requirements.txt
```

### 2. Configure the System

1. Edit the `config/settings.json` file to match your hardware configuration:
   - Adjust GPIO pin assignments if needed
   - Set the IP camera URL to match your Android phone's IP Webcam app
   - Configure other parameters as needed

2. For the IP Webcam:
   - Install "IP Webcam" app on your Android phone
   - Start the server in the app
   - Note the IP address and port (typically shown as http://192.168.x.x:8080)
   - Update the camera URL in `config/settings.json`

## Running the System

### Manual Start

To start the system manually:

```bash
cd /home/pi/pi-motor-control-project
sudo ./start_wheelchair.sh
```

Optional command-line arguments:
- `--port 5000`: Change the web server port (default: 5000)
- `--debug`: Enable debug mode
- `--no-motor`: Disable motor control
- `--no-sensor`: Disable sensors
- `--no-gps`: Disable GPS module
- `--no-weight`: Disable weight sensor

### Automatic Start on Boot

To configure the system to start automatically when the Raspberry Pi boots:

1. Copy the systemd service file:
   ```bash
   sudo cp /home/pi/pi-motor-control-project/wheelchair.service /etc/systemd/system/
   ```

2. Enable and start the service:
   ```bash
   sudo systemctl enable wheelchair.service
   sudo systemctl start wheelchair.service
   ```

3. Check the service status:
   ```bash
   sudo systemctl status wheelchair.service
   ```

## Using the Web Interface

1. Access the web interface by opening a browser and navigating to:
   ```
   http://[Raspberry Pi IP]:5000
   ```
   Replace `[Raspberry Pi IP]` with your Raspberry Pi's IP address (e.g., 192.168.1.9)

2. The web interface provides:
   - Live camera feed
   - Motor controls (direction buttons and joystick)
   - Distance sensor readings
   - Weight measurements
   - GPS location (if available)
   - Settings configuration

### Control Features

- **Motor Controls**: Use the direction buttons or virtual joystick to control wheelchair movement
- **Speed Control**: Adjust the motor speed using the slider
- **Emergency Stop**: Immediately stop all motors
- **Camera View**: View the live camera feed from the IP webcam
- **Sensor Data**: Monitor distance readings from ultrasonic sensors
- **Weight Display**: View the current weight reading (if weight sensor is enabled)

## Troubleshooting

### Common Issues

1. **Motors not responding**:
   - Check GPIO pin connections
   - Verify motor driver power supply
   - Ensure the motor initialization was successful in logs

2. **Sensors not working**:
   - Check GPIO pin connections
   - Verify sensor power supply
   - Check for errors in the logs

3. **Camera not available**:
   - Ensure the IP Webcam app is running on your phone
   - Verify the IP address and port in settings.json
   - Check network connectivity between Pi and phone

4. **Web interface not accessible**:
   - Verify the Raspberry Pi is on the same network
   - Check if the Flask server is running
   - Ensure no firewall is blocking port 5000

### Logs

Check the system logs for detailed error information:

```bash
cat /home/pi/pi-motor-control-project/logs/wheelchair.log
```

## System Architecture

The system consists of the following components:

1. **Main Application** (`src/main.py`): Initializes and coordinates all system components

2. **Motor Control** (`src/motor_control/pi_to_motor.py`): Handles motor movement commands

3. **Sensors**:
   - `src/sensors/distance_sensor.py`: Ultrasonic distance measurement
   - `src/sensors/obstacle_detection.py`: Obstacle detection and avoidance
   - `src/sensors/weight_sensor.py`: Weight measurement using load cells
   - `src/sensors/gps_module.py`: GPS location tracking

4. **Camera Integration** (`src/camera_utils.py`): Interfaces with IP webcam

5. **Web Interface** (`src/web/app.py`): Flask web server providing control UI

6. **Configuration** (`config/settings.json`): System-wide settings

## Maintenance

- Regularly check and tighten all electrical connections
- Keep sensors clean for accurate readings
- Update the software as needed:
  ```bash
  cd /home/pi/pi-motor-control-project
  git pull
  sudo pip3 install -r requirements.txt
  ```

## Safety Considerations

- The system includes automatic obstacle detection and emergency stop features
- Always test in a safe environment before regular use
- Consider adding physical emergency stop buttons
- Monitor battery levels to prevent unexpected shutdowns

## Support

For issues or questions, please refer to the project documentation or contact the system administrator.
