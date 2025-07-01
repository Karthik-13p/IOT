#!/bin/bash
# This script diagnoses the web interface motor control issue

# Set text colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Motor Control Web Interface Diagnostic ===${NC}"

# 1. Check if the virtual environment is properly set up
echo -e "${YELLOW}Checking virtual environment...${NC}"
if [ -d "venv" ] && [ -f "venv/bin/python" ]; then
    echo -e "${GREEN}Virtual environment found${NC}"
    source venv/bin/activate
    echo -e "Python version: $(python --version)"
    echo -e "Pip packages installed:"
    pip list | grep -E "flask|RPi|serial|pynmea"
else
    echo -e "${RED}Virtual environment not found or incomplete${NC}"
fi

# 2. Check if the web server is running
echo -e "\n${YELLOW}Checking if web server is running...${NC}"
if pgrep -f "python.*main.py" > /dev/null; then
    echo -e "${GREEN}Web server is running${NC}"
    ps -ef | grep "python.*main.py" | grep -v grep
else
    echo -e "${RED}Web server is not running${NC}"
fi

# 3. Check if the motor module can be imported correctly
echo -e "\n${YELLOW}Testing motor module imports...${NC}"
source venv/bin/activate
python3 -c "
try:
    import sys
    print('Python path:', sys.path)
    
    from motor_control import pi_to_motor
    print('Motor module imported successfully')
    
    print('Motors initialized:', pi_to_motor.motors_initialized)
    print('PWM frequency:', pi_to_motor.PWM_FREQ)
    print('Motor pins:', pi_to_motor.MOTOR_PINS)
    
    # Try initializing motors
    if pi_to_motor.initialize_motors(timeout=3.0):
        print('Motors initialized successfully')
    else:
        print('Failed to initialize motors')
except Exception as e:
    print('Error importing or initializing motors:', e)
"

# 4. Create a direct motor test using the same path as the web app
echo -e "\n${YELLOW}Creating a direct web-style motor test...${NC}"

cat > web_motor_test.py << 'EOL'
#!/usr/bin/env python3
"""Test the motor controls directly using the same imports as the web app."""
import os
import sys
import time

# Add the correct path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from motor_control.pi_to_motor import (
        initialize_motors, cleanup_motors, move_forward, 
        move_backward, stop, set_motor_speed
    )
    print("Successfully imported motor control modules")

    # Initialize motors
    print("Initializing motors...")
    if initialize_motors(timeout=5.0):
        print("Motors initialized successfully")
        
        # Test sequence
        print("\nTesting forward motion...")
        move_forward(100)
        time.sleep(2)
        
        print("\nStopping...")
        stop()
        time.sleep(1)
        
        print("\nTesting backward motion...")
        move_backward(100)
        time.sleep(2)
        
        print("\nFinal stop...")
        stop()
        
        print("\nCleaning up...")
        cleanup_motors()
        print("Test complete!")
    else:
        print("Failed to initialize motors")
        
except Exception as e:
    print(f"Error: {e}")
EOL

chmod +x web_motor_test.py

# 5. Check if the motor pins are accessible
echo -e "\n${YELLOW}Checking GPIO access...${NC}"
if [ $(id -u) -ne 0 ]; then
    echo -e "${RED}This script is not running as root. GPIO access may be restricted.${NC}"
    echo -e "Try running with sudo for GPIO access."
else
    echo -e "${GREEN}Running with root privileges. GPIO access should be available.${NC}"
fi

echo -e "\n${YELLOW}Checking if GPIO pins are exported...${NC}"
if [ -d "/sys/class/gpio" ]; then
    for pin in 12 13 23 24 27 22; do
        if [ -d "/sys/class/gpio/gpio$pin" ]; then
            echo -e "GPIO $pin is exported"
        fi
    done
else
    echo -e "${RED}GPIO sysfs interface not available${NC}"
fi

# 6. Create a standalone motor test that doesn't rely on the main module
echo -e "\n${YELLOW}Creating standalone L298N motor test...${NC}"

cat > direct_motor_test.py << 'EOL'
#!/usr/bin/env python3
"""Direct L298N motor test without dependencies."""
import RPi.GPIO as GPIO
import time
import sys

# Motor pins - L298N controller
LEFT_PWM = 12   # ENA - PWM pin for left motor
LEFT_IN1 = 23   # Input 1 for left motor direction control
LEFT_IN2 = 24   # Input 2 for left motor direction control

RIGHT_PWM = 13  # ENB - PWM pin for right motor
RIGHT_IN1 = 27  # Input 3 for right motor direction control
RIGHT_IN2 = 22  # Input 4 for right motor direction control

PWM_FREQ = 1000  # 1kHz frequency for PWM
DUTY_CYCLE = 100  # Full speed

def setup():
    """Set up GPIO pins and PWM."""
    try:
        # Set GPIO mode and disable warnings
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Set up left motor pins
        GPIO.setup(LEFT_PWM, GPIO.OUT)
        GPIO.setup(LEFT_IN1, GPIO.OUT)
        GPIO.setup(LEFT_IN2, GPIO.OUT)
        
        # Set up right motor pins
        GPIO.setup(RIGHT_PWM, GPIO.OUT)
        GPIO.setup(RIGHT_IN1, GPIO.OUT)
        GPIO.setup(RIGHT_IN2, GPIO.OUT)
        
        # Create PWM objects with 1kHz frequency for optimal performance
        left_pwm = GPIO.PWM(LEFT_PWM, PWM_FREQ)
        right_pwm = GPIO.PWM(RIGHT_PWM, PWM_FREQ)
        
        # Start PWM with 0% duty cycle (motors stopped)
        left_pwm.start(0)
        right_pwm.start(0)
        
        print(f"GPIO setup complete with PWM frequency {PWM_FREQ}Hz")
        return left_pwm, right_pwm
    except Exception as e:
        print(f"Error in setup: {e}")
        GPIO.cleanup()
        sys.exit(1)

def cleanup(left_pwm, right_pwm):
    """Clean up GPIO resources."""
    try:
        # Stop PWM
        left_pwm.stop()
        right_pwm.stop()
        
        # Clean up GPIO
        GPIO.cleanup()
        print("Cleanup complete")
    except Exception as e:
        print(f"Error in cleanup: {e}")

def test_motors():
    """Test motor functionality."""
    left_pwm = None
    right_pwm = None
    
    try:
        # Initialize GPIO and get PWM objects
        left_pwm, right_pwm = setup()
        
        # Test both motors moving forward
        print("\nMoving both motors FORWARD...")
        GPIO.output(LEFT_IN1, GPIO.HIGH)
        GPIO.output(LEFT_IN2, GPIO.LOW)
        GPIO.output(RIGHT_IN1, GPIO.HIGH)
        GPIO.output(RIGHT_IN2, GPIO.LOW)
        left_pwm.ChangeDutyCycle(100)
        right_pwm.ChangeDutyCycle(100)
        time.sleep(2)
        
        # Stop
        print("Stopping motors...")
        GPIO.output(LEFT_IN1, GPIO.LOW)
        GPIO.output(LEFT_IN2, GPIO.LOW)
        GPIO.output(RIGHT_IN1, GPIO.LOW)
        GPIO.output(RIGHT_IN2, GPIO.LOW)
        left_pwm.ChangeDutyCycle(0)
        right_pwm.ChangeDutyCycle(0)
        time.sleep(1)
        
        # Test both motors moving backward
        print("\nMoving both motors BACKWARD...")
        GPIO.output(LEFT_IN1, GPIO.LOW)
        GPIO.output(LEFT_IN2, GPIO.HIGH)
        GPIO.output(RIGHT_IN1, GPIO.LOW)
        GPIO.output(RIGHT_IN2, GPIO.HIGH)
        left_pwm.ChangeDutyCycle(100)
        right_pwm.ChangeDutyCycle(100)
        time.sleep(2)
        
        # Final stop
        print("Stopping motors...")
        GPIO.output(LEFT_IN1, GPIO.LOW)
        GPIO.output(LEFT_IN2, GPIO.LOW)
        GPIO.output(RIGHT_IN1, GPIO.LOW)
        GPIO.output(RIGHT_IN2, GPIO.LOW)
        left_pwm.ChangeDutyCycle(0)
        right_pwm.ChangeDutyCycle(0)
        
        print("\nTest complete!")
    
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nError occurred: {e}")
    finally:
        if left_pwm is not None and right_pwm is not None:
            cleanup(left_pwm, right_pwm)

if __name__ == "__main__":
    test_motors()
EOL

chmod +x direct_motor_test.py

echo -e "\n${GREEN}Diagnostic setup complete!${NC}"
echo -e "${YELLOW}To directly test the motors with the web style imports, run:${NC}"
echo -e "  ${GREEN}sudo python3 web_motor_test.py${NC}"
echo -e "\n${YELLOW}To test motors with a standalone script, run:${NC}"
echo -e "  ${GREEN}sudo python3 direct_motor_test.py${NC}"
echo -e "\n${YELLOW}If the web_motor_test.py works but the web interface doesn't,${NC}"
echo -e "${YELLOW}then the issue is likely with how the web app is calling the motor functions.${NC}"
