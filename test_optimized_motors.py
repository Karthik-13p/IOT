#!/usr/bin/env python3
"""
Optimized L298N motor test script for full speed operation
- Left Motor: ENA=GPIO12, IN1=GPIO23, IN2=GPIO24
- Right Motor: ENB=GPIO13, IN3=GPIO27, IN4=GPIO22
"""

import RPi.GPIO as GPIO
import time
import sys
import atexit

# Motor pins
LEFT_ENA = 12   # PWM pin for left motor
LEFT_IN1 = 23   # Direction control 1 for left motor
LEFT_IN2 = 24   # Direction control 2 for left motor

RIGHT_ENB = 13  # PWM pin for right motor
RIGHT_IN1 = 27  # Direction control 1 for right motor (IN3 on L298N)
RIGHT_IN2 = 22  # Direction control 2 for right motor (IN4 on L298N)

# PWM settings for optimal performance
PWM_FREQ = 1000  # 1kHz frequency for PWM
MAX_DUTY = 100   # Maximum duty cycle

# Global variables for cleanup
left_pwm = None
right_pwm = None

def setup():
    """Set up GPIO and initialize motors."""
    global left_pwm, right_pwm
    
    # Use BCM pin numbering
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # Set up all motor pins as outputs
    pins = [LEFT_ENA, LEFT_IN1, LEFT_IN2, RIGHT_ENB, RIGHT_IN1, RIGHT_IN2]
    for pin in pins:
        GPIO.setup(pin, GPIO.OUT)
        # Initialize all pins to LOW (motors stopped)
        GPIO.output(pin, GPIO.LOW)
    
    # Create PWM objects with 1kHz frequency for optimal performance
    left_pwm = GPIO.PWM(LEFT_ENA, PWM_FREQ)
    right_pwm = GPIO.PWM(RIGHT_ENB, PWM_FREQ)
    
    # Start PWM with 0% duty cycle (motors stopped)
    left_pwm.start(0)
    right_pwm.start(0)
    
    print(f"Motor pins initialized with PWM frequency {PWM_FREQ}Hz")

def cleanup():
    """Clean up GPIO resources."""
    global left_pwm, right_pwm
    
    print("\nCleaning up GPIO resources...")
    
    # Set all direction pins to LOW first
    try:
        GPIO.output(LEFT_IN1, GPIO.LOW)
        GPIO.output(LEFT_IN2, GPIO.LOW)
        GPIO.output(RIGHT_IN1, GPIO.LOW)
        GPIO.output(RIGHT_IN2, GPIO.LOW)
    except:
        pass
    
    # Stop PWM with proper error handling
    try:
        if left_pwm:
            left_pwm.ChangeDutyCycle(0)
            left_pwm.stop()
    except:
        pass
        
    try:
        if right_pwm:
            right_pwm.ChangeDutyCycle(0)
            right_pwm.stop()
    except:
        pass
    
    # Clean up GPIO - only cleanup specific pins to avoid warnings
    try:
        pins = [LEFT_ENA, LEFT_IN1, LEFT_IN2, RIGHT_ENB, RIGHT_IN1, RIGHT_IN2]
        for pin in pins:
            GPIO.cleanup(pin)
    except:
        pass
        
    print("Cleanup complete")

def forward(speed=100, duration=2):
    """Move both motors forward at full speed."""
    print(f"\nMoving FORWARD at {speed}% speed for {duration} seconds")
    
    # Left motor forward
    GPIO.output(LEFT_IN1, GPIO.HIGH)
    GPIO.output(LEFT_IN2, GPIO.LOW)
    
    # Right motor forward
    GPIO.output(RIGHT_IN1, GPIO.HIGH)
    GPIO.output(RIGHT_IN2, GPIO.LOW)
    
    # Set speed via PWM
    left_pwm.ChangeDutyCycle(speed)
    right_pwm.ChangeDutyCycle(speed)
    
    # Wait for specified duration
    time.sleep(duration)

def backward(speed=100, duration=2):
    """Move both motors backward at full speed."""
    print(f"\nMoving BACKWARD at {speed}% speed for {duration} seconds")
    
    # Left motor backward
    GPIO.output(LEFT_IN1, GPIO.LOW)
    GPIO.output(LEFT_IN2, GPIO.HIGH)
    
    # Right motor backward
    GPIO.output(RIGHT_IN1, GPIO.LOW)
    GPIO.output(RIGHT_IN2, GPIO.HIGH)
    
    # Set speed via PWM
    left_pwm.ChangeDutyCycle(speed)
    right_pwm.ChangeDutyCycle(speed)
    
    # Wait for specified duration
    time.sleep(duration)

def stop(duration=1):
    """Stop both motors."""
    print(f"\nSTOPPING motors for {duration} seconds")
    
    # Stop all motors (by setting both control pins LOW)
    GPIO.output(LEFT_IN1, GPIO.LOW)
    GPIO.output(LEFT_IN2, GPIO.LOW)
    GPIO.output(RIGHT_IN1, GPIO.LOW)
    GPIO.output(RIGHT_IN2, GPIO.LOW)
    
    # Set PWM to 0
    left_pwm.ChangeDutyCycle(0)
    right_pwm.ChangeDutyCycle(0)
    
    # Wait for specified duration
    time.sleep(duration)

def test_full_speed():
    """Run a test focused on full speed operation."""
    print("=== OPTIMIZED L298N Motor Test for Full Speed ===")
    print("LEFT MOTOR: ENA=GPIO12, IN1=GPIO23, IN2=GPIO24")
    print("RIGHT MOTOR: ENB=GPIO13, IN3=GPIO27, IN4=GPIO22")
    print("PWM Frequency: 1kHz for optimal performance")
    print("==============================================")
    
    try:
        # Initialize pins
        setup()
        
        # Test full speed forward movement
        print("\n--- Testing FORWARD at 100% speed ---")
        forward(speed=100, duration=3)
        
        # Stop
        stop(duration=1)
        
        # Test full speed backward movement
        print("\n--- Testing BACKWARD at 100% speed ---")
        backward(speed=100, duration=3)
        
        # Stop
        stop(duration=1)
        
        # Test individual motors at full speed
        print("\n--- Testing LEFT motor at 100% ---")
        GPIO.output(LEFT_IN1, GPIO.HIGH)
        GPIO.output(LEFT_IN2, GPIO.LOW)
        left_pwm.ChangeDutyCycle(100)
        GPIO.output(RIGHT_IN1, GPIO.LOW) 
        GPIO.output(RIGHT_IN2, GPIO.LOW)
        right_pwm.ChangeDutyCycle(0)
        time.sleep(3)
        
        # Stop left motor
        GPIO.output(LEFT_IN1, GPIO.LOW)
        GPIO.output(LEFT_IN2, GPIO.LOW)
        left_pwm.ChangeDutyCycle(0)
        time.sleep(1)
        
        print("\n--- Testing RIGHT motor at 100% ---")
        GPIO.output(RIGHT_IN1, GPIO.HIGH)
        GPIO.output(RIGHT_IN2, GPIO.LOW)
        right_pwm.ChangeDutyCycle(100)
        GPIO.output(LEFT_IN1, GPIO.LOW)
        GPIO.output(LEFT_IN2, GPIO.LOW)
        left_pwm.ChangeDutyCycle(0)
        time.sleep(3)
        
        # Final stop
        stop()
        
        print("\nFull speed test completed successfully!")
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nError occurred: {e}")

if __name__ == "__main__":
    # Register cleanup function to run on exit
    atexit.register(cleanup)
    
    # Run the test
    test_full_speed()
