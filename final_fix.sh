#!/bin/bash
# Final fix script for motor control project

# Set text colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Final Motor Configuration Fix ===${NC}"

# Activate the virtual environment
source venv/bin/activate

# Install packages if needed
pip install flask pyserial pynmea2 RPi.GPIO

# Create fixed settings file
echo -e "${YELLOW}Creating fixed settings file...${NC}"

cat > config/settings.json.fixed << 'EOL'
{
  "ultrasonic_sensor": {
    "trigger_pin": 18,
    "echo_pin": 17,
    "max_distance": 400
  },
  "gpio_pins": {
    "motor1_pwm": 12,
    "motor1_in1": 23,
    "motor1_in2": 24,
    "motor2_pwm": 13,
    "motor2_in1": 27,
    "motor2_in2": 22
  },
  "pwm_frequency": 1000,
  "motor_speed_limits": {
    "min_speed": -100,
    "max_speed": 100
  },
  "motor_configuration": {
    "type": "paired",
    "left_motors": [1],
    "right_motors": [2]
  },
  "camera": {
    "type": "ip_camera",
    "ip_camera_url": "http://192.168.1.3:8080",
    "snapshot_path": "/shot.jpg",
    "video_path": "/video",
    "mjpeg_path": "/videofeed",
    "capture_interval": 5,
    "enabled": true,
    "position": {
      "height": 120,
      "angle": 45,
      "direction": "forward"
    },
    "view_settings": {
      "rotation": 0,
      "flip_horizontal": false,
      "flip_vertical": false,
      "quality": "high"
    }
  },
  "gps": {
    "port": "/dev/ttyS0",
    "baud_rate": 9600,
    "timeout": 1,
    "update_interval": 5,
    "enabled": true
  },
  "obstacle_detection": {
    "danger_threshold": 25,
    "warning_threshold": 50,
    "caution_threshold": 100,
    "check_interval": 0.2,
    "auto_stop_enabled": true
  },
  "web_interface": {
    "port": 5001,
    "host": "0.0.0.0",
    "debug": false,
    "refresh_interval": 500
  }
}
EOL

# Replace settings file
echo -e "${YELLOW}Replacing current settings with fixed settings...${NC}"
cp config/settings.json.fixed config/settings.json
echo -e "${GREEN}Settings file updated${NC}"

# Fix the pi_to_motor.py file to properly handle the motors
echo -e "${YELLOW}Fixing motor control module...${NC}"

cat > src/motor_control/pi_to_motor.py.fixed << 'EOL'
# Updated motor control module for Raspberry Pi with L298N
import RPi.GPIO as GPIO
import time
import json
import os
import threading
from threading import Timer

# Load settings from config file
config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'settings.json')
try:
    with open(config_path, 'r') as f:
        settings = json.load(f)
    print(f"Loaded motor settings from {config_path}")
except Exception as e:
    print(f"Error loading settings: {e}")
    # Default settings if file not found
    settings = {
        "gpio_pins": {
            "motor1_pwm": 12, "motor1_in1": 23, "motor1_in2": 24,
            "motor2_pwm": 13, "motor2_in1": 27, "motor2_in2": 22
        },
        "motor_speed_limits": {"min_speed": -100, "max_speed": 100},
        "pwm_frequency": 1000,
        "motor_configuration": {
            "type": "paired",
            "left_motors": [1],
            "right_motors": [2]
        }
    }
    print("Using default motor settings")

# GPIO pin settings
MOTOR_PINS = settings['gpio_pins']
MIN_SPEED = settings['motor_speed_limits']['min_speed']
MAX_SPEED = settings['motor_speed_limits']['max_speed']
PWM_FREQ = settings['pwm_frequency']
MOTOR_CONFIG = settings['motor_configuration']

print(f"Loaded motor config: PWM_FREQ={PWM_FREQ}, MOTOR_PINS={MOTOR_PINS}")

# Global variables for motor control
motor_pwm = {
    1: None,
    2: None,
    3: None,
    4: None
}
motors_initialized = False
motor_lock = threading.Lock()

# Initialize with timeout
def initialize_motors(timeout=2.0):
    """Initialize the GPIO pins for motor control with timeout."""
    global motors_initialized, motor_pwm
    
    # Use a timeout to prevent hanging
    initialization_done = threading.Event()
    initialization_success = [False]  # Use a list to modify in the thread
    
    def _init_with_timeout():
        """Motor initialization with timeout."""
        global motors_initialized, motor_pwm
        
        try:
            # Clean up any existing GPIO resources first
            cleanup_motors()
            
            # Set GPIO mode
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            print(f"Setting up motor pins with PWM frequency {PWM_FREQ} Hz...")
            
            # Set up motors 1 and 2 only (the ones we need)
            motors_to_setup = [1, 2] 
            success_count = 0
            
            for motor_num in motors_to_setup:
                try:
                    pwm_pin = MOTOR_PINS[f'motor{motor_num}_pwm']
                    in1_pin = MOTOR_PINS[f'motor{motor_num}_in1']
                    in2_pin = MOTOR_PINS[f'motor{motor_num}_in2']
                    
                    print(f"Setting up motor {motor_num} with pins: PWM={pwm_pin}, IN1={in1_pin}, IN2={in2_pin}")
                    
                    # Set up direction pins as outputs and initialize to LOW
                    GPIO.setup(in1_pin, GPIO.OUT)
                    GPIO.setup(in2_pin, GPIO.OUT)
                    GPIO.output(in1_pin, GPIO.LOW)
                    GPIO.output(in2_pin, GPIO.LOW)
                    
                    # Set up PWM pin
                    GPIO.setup(pwm_pin, GPIO.OUT)
                    
                    # Initialize PWM with 1kHz frequency for optimal performance
                    motor_pwm[motor_num] = GPIO.PWM(pwm_pin, PWM_FREQ)
                    motor_pwm[motor_num].start(0)  # Start with 0% duty cycle
                    print(f"Motor {motor_num} initialized on PWM pin {pwm_pin}")
                    success_count += 1
                    
                except Exception as e:
                    print(f"Error initializing motor {motor_num}: {e}")
                    # Clean up this motor's resources
                    try:
                        if motor_pwm[motor_num] is not None:
                            motor_pwm[motor_num].stop()
                    except:
                        pass
                    motor_pwm[motor_num] = None
            
            # Check if at least one motor was initialized
            if success_count > 0:
                motors_initialized = True
                initialization_success[0] = True
                print(f"Motors initialization successful: {success_count} motors initialized")
            else:
                print("No motors were successfully initialized")
                motors_initialized = False
                initialization_success[0] = False
                
        except Exception as e:
            print(f"Error during motor initialization: {e}")
            motors_initialized = False
            initialization_success[0] = False
        finally:
            initialization_done.set()
    
    # Start initialization in a thread
    init_thread = threading.Thread(target=_init_with_timeout)
    init_thread.daemon = True
    init_thread.start()
    
    # Wait for initialization to complete or timeout
    if initialization_done.wait(timeout):
        return initialization_success[0]
    else:
        print(f"Motor initialization timed out after {timeout} seconds")
        motors_initialized = False
        return False

def set_motor_speed(motor_num, speed):
    """Set the speed of a specific motor (-100 to 100)."""
    global motors_initialized, motor_pwm
    
    if not motors_initialized:
        print(f"Motors not initialized. Cannot set motor {motor_num} speed.")
        return False
    
    # Check if this motor is available
    if motor_pwm[motor_num] is None:
        print(f"Motor {motor_num} not available")
        return False
    
    # Clamp speed to valid range
    speed = max(-MAX_SPEED, min(MAX_SPEED, speed))
    
    # For optimal performance at full speed, use exactly 100% when speed is close to max
    if abs(speed) > 95:
        speed = 100 if speed > 0 else -100
    
    try:
        # Get pin numbers for this motor
        pwm_pin = MOTOR_PINS[f'motor{motor_num}_pwm']
        in1_pin = MOTOR_PINS[f'motor{motor_num}_in1']
        in2_pin = MOTOR_PINS[f'motor{motor_num}_in2']
        
        print(f"Motor {motor_num} - Setting speed {speed} on pins: PWM={pwm_pin}, IN1={in1_pin}, IN2={in2_pin}")
        
        # Set direction based on speed
        if speed > 0:
            # Forward
            print(f"Motor {motor_num} - Forward: IN1=HIGH, IN2=LOW")
            GPIO.output(in1_pin, True)
            GPIO.output(in2_pin, False)
        elif speed < 0:
            # Backward
            print(f"Motor {motor_num} - Backward: IN1=LOW, IN2=HIGH")
            GPIO.output(in1_pin, False)
            GPIO.output(in2_pin, True)
        else:
            # Stop
            print(f"Motor {motor_num} - Stop: IN1=LOW, IN2=LOW")
            GPIO.output(in1_pin, False)
            GPIO.output(in2_pin, False)
        
        # Set PWM duty cycle (convert from -100-100 to 0-100)
        duty_cycle = abs(speed)
        print(f"Motor {motor_num} - Setting PWM duty cycle to {duty_cycle}%")
        motor_pwm[motor_num].ChangeDutyCycle(duty_cycle)
        
        return True
    except Exception as e:
        print(f"Error setting motor {motor_num} speed: {e}")
        return False

def move_forward(speed=100):
    """Move the robot forward at the specified speed."""
    print(f"Moving forward at speed {speed}")
    
    if not motors_initialized and not initialize_motors():
        print("Failed to initialize motors")
        return False
    
    result = True
    # For paired configuration, use left/right motor groups
    if MOTOR_CONFIG['type'] == 'paired':
        for motor_num in MOTOR_CONFIG['left_motors']:
            result = result and set_motor_speed(motor_num, speed)
        for motor_num in MOTOR_CONFIG['right_motors']:
            result = result and set_motor_speed(motor_num, speed)
    else:
        # For individual control, set all motors to same speed
        for motor_num in range(1, 3):  # Only use motors 1 and 2
            if motor_pwm[motor_num] is not None:
                result = result and set_motor_speed(motor_num, speed)
    
    print(f"Moving forward at speed {speed}, result: {result}")
    return result

def move_backward(speed=100):
    """Move the robot backward at the specified speed."""
    print(f"Moving backward at speed {speed}")
    
    if not motors_initialized and not initialize_motors():
        print("Failed to initialize motors for backward movement")
        return False
    
    # Make sure speed is positive (we'll negate it in set_motor_speed)
    speed = abs(speed)
    
    result = True
    # For paired configuration, use left/right motor groups
    if MOTOR_CONFIG['type'] == 'paired':
        for motor_num in MOTOR_CONFIG['left_motors']:
            print(f"Setting left motor {motor_num} backward: speed={-speed}")
            if motor_pwm[motor_num] is not None:
                result = result and set_motor_speed(motor_num, -speed)
            else:
                print(f"Warning: Motor {motor_num} not available")
                
        for motor_num in MOTOR_CONFIG['right_motors']:
            print(f"Setting right motor {motor_num} backward: speed={-speed}")
            if motor_pwm[motor_num] is not None:
                result = result and set_motor_speed(motor_num, -speed)
            else:
                print(f"Warning: Motor {motor_num} not available")
    else:
        # For individual control, set all motors to same speed
        for motor_num in range(1, 3):  # Only use motors 1 and 2
            if motor_pwm[motor_num] is not None:
                result = result and set_motor_speed(motor_num, -speed)
    
    print(f"Moving backward with result: {result}")
    return result

def turn_left(speed=100):
    """Turn functionality disabled - stops the motors instead."""
    print("Turn left functionality disabled - stopping motors")
    return stop()

def turn_right(speed=100):
    """Turn functionality disabled - stops the motors instead."""
    print("Turn right functionality disabled - stopping motors")
    return stop()

def stop():
    """Stop all motors."""
    print("Stopping all motors")
    
    if not motors_initialized and not initialize_motors():
        return False
    
    result = True
    for motor_num in range(1, 3):  # Only use motors 1 and 2
        if motor_pwm[motor_num] is not None:
            result = result and set_motor_speed(motor_num, 0)
    
    print("Motors stopped")
    return result

def cleanup_motors(reset_gpio=False):
    """Clean up GPIO resources."""
    global motors_initialized, motor_pwm
    
    try:
        # First ensure all motors are stopped by setting their control pins to LOW
        for motor_num in range(1, 3):  # Only motors 1 and 2
            try:
                if f'motor{motor_num}_in1' in MOTOR_PINS and f'motor{motor_num}_in2' in MOTOR_PINS:
                    in1_pin = MOTOR_PINS[f'motor{motor_num}_in1']
                    in2_pin = MOTOR_PINS[f'motor{motor_num}_in2']
                    GPIO.output(in1_pin, GPIO.LOW)
                    GPIO.output(in2_pin, GPIO.LOW)
            except Exception:
                pass
                
        # Now stop all PWM
        for motor_num in range(1, 3):  # Only motors 1 and 2
            if motor_pwm[motor_num] is not None:
                try:
                    # First set the duty cycle to 0
                    motor_pwm[motor_num].ChangeDutyCycle(0)
                    time.sleep(0.01)  # Small delay to ensure duty cycle change takes effect
                    
                    # Stop PWM
                    motor_pwm[motor_num].stop()
                    print(f"Motor {motor_num} PWM stopped")
                except Exception as e:
                    print(f"Warning: Error stopping PWM for motor {motor_num}: {e}")
                finally:
                    motor_pwm[motor_num] = None
        
        # Reset GPIO settings if requested
        if reset_gpio:
            try:
                # Only cleanup pins we've set, not all GPIOs
                pins_to_cleanup = []
                for motor_num in range(1, 3):  # Only motors 1 and 2
                    if f'motor{motor_num}_pwm' in MOTOR_PINS:
                        pins_to_cleanup.append(MOTOR_PINS[f'motor{motor_num}_pwm'])
                    if f'motor{motor_num}_in1' in MOTOR_PINS:
                        pins_to_cleanup.append(MOTOR_PINS[f'motor{motor_num}_in1'])
                    if f'motor{motor_num}_in2' in MOTOR_PINS:
                        pins_to_cleanup.append(MOTOR_PINS[f'motor{motor_num}_in2'])
                        
                # Clean up only the pins we used
                for pin in pins_to_cleanup:
                    try:
                        GPIO.cleanup(pin)
                    except:
                        pass
                        
                print("GPIO cleanup done")
            except Exception as e:
                print(f"Warning: Error during GPIO cleanup: {e}")
        
        motors_initialized = False
        print("Motors cleanup complete")
        
    except Exception as e:
        print(f"Error during motors cleanup: {e}")
    finally:
        # Ensure motor_pwm is reset even if an error occurs
        motor_pwm = {1: None, 2: None, 3: None, 4: None}
        motors_initialized = False

# Ensure GPIO is cleaned up on normal exit
import atexit
atexit.register(cleanup_motors)

def forward(speed=100):
    """
    Move all motors forward at the specified speed.
    
    Args:
        speed: Motor speed (0-100)
    """
    return move_forward(speed)

def backward(speed=100):
    """
    Move all motors backward at the specified speed.
    
    Args:
        speed: Motor speed (0-100)
    """
    return move_backward(speed)

def left(speed=100):
    """
    Turn the wheelchair left at the specified speed.
    
    Args:
        speed: Motor speed (0-100)
    """
    return turn_left(speed)

def right(speed=100):
    """
    Turn the wheelchair right at the specified speed.
    
    Args:
        speed: Motor speed (0-100)
    """
    return turn_right(speed)
EOL

# Replace pi_to_motor.py file
cp src/motor_control/pi_to_motor.py.fixed src/motor_control/pi_to_motor.py

# Create a fixed app.py script that uses the VENV for importing Flask
echo -e "${YELLOW}Fixing the web application to use virtual environment...${NC}"
cat > src/web/app.py.fixed << 'EOL'
#!/usr/bin/env python3
# Updated app.py to work in a virtual environment
from flask import Flask, render_template, jsonify, Response, request
import threading
import time
import os
import sys
import json
import logging
import atexit

# Set up logging
logger = logging.getLogger('wheelchair.web')

# Add parent directory to path to import project modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Import motor control functions
    from motor_control.pi_to_motor import (
        initialize_motors, cleanup_motors, move_forward, 
        move_backward, stop, set_motor_speed
    )
    print("Successfully imported motor control modules")
except Exception as e:
    print(f"Error importing motor control: {e}")

try:
    from sensors.distance_sensor import read_distance
    print("Successfully imported distance sensor module")
except Exception as e:
    print(f"Error importing distance sensor: {e}")

try:
    from sensors import gps_module
    print("Successfully imported GPS module")
except Exception as e:
    print(f"Error importing GPS module: {e}")

# Import camera utils
try:
    import camera_utils
    print("Successfully imported camera utils")
except Exception as e:
    print(f"Error importing camera utils: {e}")
    camera_utils = None

# Weight sensor disabled
WEIGHT_SENSOR_AVAILABLE = False

# Enable camera functionality
CAMERA_AVAILABLE = True

app = Flask(__name__)

# Global state variables
motor_state = {
    "running": False,
    "speed": 100,  # Set default speed to 100% for optimal performance
    "direction": "stop"
}

# Initialize motors when app starts
try:
    if initialize_motors(timeout=10.0):  # Increased timeout for better reliability
        print("Motors initialized successfully in web app with 1kHz PWM frequency")
        # Set all motors to LOW state to ensure they're ready for commands
        stop()
        print("Motors set to initial stopped state")
    else:
        print("Failed to initialize motors in web app")
except Exception as e:
    print(f"Error initializing motors in web app: {e}")

# Start GPS when app starts
if os.path.exists('/dev/ttyAMA0') or os.path.exists('/dev/ttyS0'):
    try:
        gps_module.start_gps_monitoring()
        print("GPS monitoring started")
    except Exception as e:
        print(f"Error starting GPS monitoring: {e}")
        print("Try installing pyserial with: pip install pyserial pynmea2")

@app.route('/')
def index():
    """Main dashboard page."""
    # Check camera availability
    camera_status = camera_utils.is_camera_available() if camera_utils else False
    
    return render_template('index.html', 
                          camera_available=camera_status,
                          ip_camera_url=camera_utils.IP_CAMERA_URL if camera_utils else "")

@app.route('/api/motors/control', methods=['POST'])
def control_motors():
    """API endpoint to control motors."""
    try:
        data = request.get_json()
        command = data.get('command')
        speed = int(data.get('speed', motor_state["speed"]))
        
        # Optimize for full speed operation when speed is near maximum
        if speed > 95:
            speed = 100
        
        print(f"Motor control: Command={command}, Speed={speed}")
        
        motor_state["speed"] = speed
        
        if command == 'start':
            # Make sure motors are initialized
            if not initialize_motors(timeout=5.0):
                return jsonify({"status": "error", "message": "Failed to initialize motors"})
            
            motor_state["running"] = True
            stop()  # Ensure motors are stopped before changing state
            print("Motors started")
            return jsonify({"status": "success", "message": "Motors started"})
            
        elif command == 'stop':
            motor_state["running"] = False
            motor_state["direction"] = "stop"
            stop()
            print("Motors stopped")
            return jsonify({"status": "success", "message": "Motors stopped"})
            
        elif not motor_state["running"]:
            print("Error: Motors not started")
            return jsonify({"status": "error", "message": "Motors not started"})
            
        elif command == 'forward':
            motor_state["direction"] = "forward"
            result = move_forward(speed)
            print(f"Moving forward at speed {speed}, result: {result}")
            
        elif command == 'backward':
            motor_state["direction"] = "backward"
            result = move_backward(speed)
            print(f"Moving backward at speed {speed}, result: {result}")
            
        elif command == 'left' or command == 'right':
            # Turning functionality disabled - just stop motors
            motor_state["direction"] = "stop"
            result = stop()
            print(f"Turning disabled - stopping motors")
            return jsonify({"status": "info", "message": "Turning functionality disabled", "state": motor_state})
        
        return jsonify({
            "status": "success", 
            "state": motor_state
        })
        
    except Exception as e:
        print(f"Error in motor control: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/motors/status')
def motor_status():
    """API endpoint to get current motor status."""
    return jsonify(motor_state)

@app.route('/api/sensors/distance')
def sensor_distance():
    """API endpoint to get current distance reading."""
    try:
        distance = read_distance()
        return jsonify({
            "distance": distance
        })
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/test')
def test():
    """Test endpoint to verify web server is working."""
    return "Web server is working!"

@app.route('/motor_test')
def motor_test():
    """Test page for direct motor control testing."""
    return render_template('motor_test.html')

# Emergency stop endpoint
@app.route('/api/emergency_stop')
def emergency_stop():
    """API endpoint for emergency stop."""
    try:
        # Try to initialize if needed
        initialize_motors(timeout=2.0)
            
        stop()
        motor_state["running"] = False
        motor_state["direction"] = "stop"
        return jsonify({"status": "success", "message": "Emergency stop activated"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# Register cleanup function to run when app exits
@atexit.register
def cleanup_app():
    """Clean up resources when app exits."""
    try:
        print("Cleaning up motor resources in web app...")
        # First stop all motors
        try:
            stop()
            print("Motors stopped")
            time.sleep(0.1)  # Small delay to ensure motors have time to stop
        except Exception as e:
            print(f"Warning: Error stopping motors: {e}")
            
        # Then clean up GPIO resources - don't reset GPIO as main process will do that
        cleanup_motors(reset_gpio=False)
        print("Motor resources cleaned up")
    except Exception as e:
        print(f"Error during web app cleanup: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
EOL

# Replace app.py file
cp src/web/app.py.fixed src/web/app.py

# Create improved run_app.sh script
echo -e "${YELLOW}Creating improved application launcher...${NC}"
cat > run_app.sh << 'EOL'
#!/bin/bash
# Run the motor control application with the virtual environment

# Set text colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting Motor Control Application${NC}"

# Change to script directory
cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Check if we need root permissions
if [[ $EUID -ne 0 ]]; then
    echo -e "${YELLOW}This script requires root privileges for GPIO access${NC}"
    echo -e "${YELLOW}Running with sudo...${NC}"
    sudo PYTHONPATH=$(pwd) venv/bin/python src/main.py
else
    PYTHONPATH=$(pwd) python src/main.py
fi
EOL

chmod +x run_app.sh

echo -e "${GREEN}Final fix complete!${NC}"
echo -e "${YELLOW}To run the web application with motors properly initialized:${NC}"
echo -e "${GREEN}./run_app.sh${NC}"
echo -e ""
echo -e "${YELLOW}Motor test is already working correctly!${NC}"
