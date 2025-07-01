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
except Exception as e:
    print(f"Error loading settings: {e}")
    # Default settings if file not found
    settings = {
        "gpio_pins": {
            "motor1_pwm": 12, "motor1_in1": 16, "motor1_in2": 18,
            "motor2_pwm": 13, "motor2_in1": 22, "motor2_in2": 24,
            "motor3_pwm": 19, "motor3_in1": 21, "motor3_in2": 23,
            "motor4_pwm": 26, "motor4_in1": 31, "motor4_in2": 33
        },
        "motor_speed_limits": {"min_speed": 0, "max_speed": 100},
        "pwm_frequency": 100,
        "motor_configuration": {
            "type": "paired",
            "left_motors": [1, 3],
            "right_motors": [2, 4]
        }
    }

# GPIO pin settings
MOTOR_PINS = settings['gpio_pins']
MIN_SPEED = settings['motor_speed_limits']['min_speed']
MAX_SPEED = settings['motor_speed_limits']['max_speed']
PWM_FREQ = settings['pwm_frequency']
MOTOR_CONFIG = settings['motor_configuration']

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
            cleanup_motors(reset_gpio=True)
            
            # Set GPIO mode
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            print(f"Setting up motor pins with PWM frequency {PWM_FREQ} Hz...")
            
            # Set up each motor's pins
            for motor_num in range(1, 5):
                try:
                    # Check if pin numbers exist in config
                    if f'motor{motor_num}_pwm' not in MOTOR_PINS:
                        print(f"Warning: Motor {motor_num} pins not found in config")
                        continue
                        
                    pwm_pin = MOTOR_PINS[f'motor{motor_num}_pwm']
                    in1_pin = MOTOR_PINS[f'motor{motor_num}_in1']
                    in2_pin = MOTOR_PINS[f'motor{motor_num}_in2']
                    
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
                    
                except Exception as e:
                    print(f"Error initializing motor {motor_num}: {e}")
                    # Clean up this motor's resources
                    try:
                        if motor_pwm[motor_num] is not None:
                            motor_pwm[motor_num].stop()
                    except:
                        pass
                    motor_pwm[motor_num] = None
                    continue
            
            # Check if at least one motor was initialized
            if any(pwm is not None for pwm in motor_pwm.values()):
                motors_initialized = True
                initialization_success[0] = True
                print("Motors initialization successful")
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
        for motor_num in range(1, 5):
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
        for motor_num in range(1, 5):
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
    for motor_num in range(1, 5):
        if motor_pwm[motor_num] is not None:
            result = result and set_motor_speed(motor_num, 0)
    
    print("Motors stopped")
    return result

def cleanup_motors(reset_gpio=False):
    """Clean up GPIO resources."""
    global motors_initialized, motor_pwm
    
    try:
        # First ensure all motors are stopped by setting their control pins to LOW
        for motor_num in range(1, 5):
            try:
                if f'motor{motor_num}_in1' in MOTOR_PINS and f'motor{motor_num}_in2' in MOTOR_PINS:
                    in1_pin = MOTOR_PINS[f'motor{motor_num}_in1']
                    in2_pin = MOTOR_PINS[f'motor{motor_num}_in2']
                    GPIO.output(in1_pin, GPIO.LOW)
                    GPIO.output(in2_pin, GPIO.LOW)
            except Exception:
                pass
                
        # Now stop all PWM
        for motor_num in range(1, 5):
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
                for motor_num in range(1, 5):
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
