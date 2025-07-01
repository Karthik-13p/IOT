import RPi.GPIO as GPIO
import time
import json
import os

# Load settings from config file
config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'settings.json')
with open(config_path, 'r') as f:
    settings = json.load(f)

# Get ultrasonic sensor settings
TRIGGER_PIN = settings['ultrasonic_sensor']['trigger_pin']
ECHO_PIN = settings['ultrasonic_sensor']['echo_pin']
MAX_DISTANCE = settings['ultrasonic_sensor']['max_distance']

sensor_initialized = False

def setup_distance_sensor():
    """Set up the ultrasonic distance sensor."""
    global sensor_initialized
    
    # Important: Set the GPIO mode first!
    GPIO.setmode(GPIO.BCM)  # Use BCM numbering
    
    # Set up the pins
    GPIO.setup(TRIGGER_PIN, GPIO.OUT)
    GPIO.setup(ECHO_PIN, GPIO.IN)
    
    # Ensure trigger is low
    GPIO.output(TRIGGER_PIN, False)
    time.sleep(0.5)  # Wait for sensor to settle
    
    sensor_initialized = True
    print(f"Distance sensor initialized with trigger pin {TRIGGER_PIN} and echo pin {ECHO_PIN}")
    return True

def read_distance():
    """Read distance from the ultrasonic sensor in cm."""
    try:
        # Set trigger high for 10 microseconds
        GPIO.output(TRIGGER_PIN, True)
        time.sleep(0.00001)  # 10 microseconds
        GPIO.output(TRIGGER_PIN, False)
        
        # Wait for echo to go high
        start_time = time.time()
        while GPIO.input(ECHO_PIN) == 0:
            if time.time() - start_time > 0.1:  # timeout after 100ms
                return MAX_DISTANCE  # Return max distance if timeout
            
        # Record time when echo goes high
        pulse_start = time.time()
        
        # Wait for echo to go low
        start_time = time.time()
        while GPIO.input(ECHO_PIN) == 1:
            if time.time() - start_time > 0.1:  # timeout after 100ms
                return MAX_DISTANCE  # Return max distance if timeout
            
        # Record time when echo goes low
        pulse_end = time.time()
        
        # Calculate pulse duration
        pulse_duration = pulse_end - pulse_start
        
        # Convert to distance (speed of sound = 34300 cm/s)
        # Divide by 2 because sound travels there and back
        distance = pulse_duration * 34300 / 2
        
        # Cap at max distance
        distance = min(distance, MAX_DISTANCE)
        
        return distance
    except Exception as e:
        print(f"Error reading distance sensor: {e}")
        return MAX_DISTANCE  # Return max distance on error

def cleanup_distance_sensor():
    """Clean up GPIO resources."""
    global sensor_initialized
    
    try:
        if sensor_initialized:
            # Always set mode before cleanup
            try:
                current_mode = GPIO.getmode()
                if current_mode is None:
                    GPIO.setmode(GPIO.BCM)  # Default to BCM if no mode set
            except:
                GPIO.setmode(GPIO.BCM)  # Set mode if getting current mode fails
            
            # Clean up pins
            GPIO.setup(TRIGGER_PIN, GPIO.IN)
            GPIO.setup(ECHO_PIN, GPIO.IN)
            sensor_initialized = False
            print("Distance sensor cleaned up")
    except Exception as e:
        print(f"Error cleaning up distance sensor: {e}")