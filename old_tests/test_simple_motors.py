#!/usr/bin/env python3
"""
Simple L298N motor test script for troubleshooting
Designed to work with the pin configuration:
- Left Motor: ENA=GPIO12, IN1=GPIO23, IN2=GPIO24
- Right Motor: ENB=GPIO13, IN3=GPIO27, IN4=GPIO22
"""

import RPi.GPIO as GPIO
import time
import sys

# Motor pins
LEFT_ENA = 12   # PWM pin for left motor
LEFT_IN1 = 23   # Direction control 1 for left motor
LEFT_IN2 = 24   # Direction control 2 for left motor

RIGHT_ENB = 13  # PWM pin for right motor
RIGHT_IN1 = 27  # Direction control 1 for right motor (IN3 on the L298N)
RIGHT_IN2 = 22  # Direction control 2 for right motor (IN4 on the L298N)

# PWM settings
PWM_FREQ = 1000  # 1kHz frequency for PWM
MAX_DUTY = 100   # Maximum duty cycle

def setup():
    """Set up GPIO and initialize motors."""
    # Use BCM pin numbering
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # Set up all motor pins as outputs
    pins = [LEFT_ENA, LEFT_IN1, LEFT_IN2, RIGHT_ENB, RIGHT_IN1, RIGHT_IN2]
    for pin in pins:
        GPIO.setup(pin, GPIO.OUT)
        # Initialize all pins to LOW (motors stopped)
        GPIO.output(pin, GPIO.LOW)
    
    # Create PWM objects
    left_pwm = GPIO.PWM(LEFT_ENA, PWM_FREQ)
    right_pwm = GPIO.PWM(RIGHT_ENB, PWM_FREQ)
    
    # Start PWM with 0% duty cycle (motors stopped)
    left_pwm.start(0)
    right_pwm.start(0)
    
    print(f"Motor pins initialized with PWM frequency {PWM_FREQ}Hz")
    return left_pwm, right_pwm

def cleanup(left_pwm, right_pwm):
    """Clean up GPIO resources."""
    print("\nCleaning up GPIO resources...")
    
    # Stop PWM
    left_pwm.stop()
    right_pwm.stop()
    
    # Set all pins to LOW
    pins = [LEFT_IN1, LEFT_IN2, RIGHT_IN1, RIGHT_IN2]
    for pin in pins:
        GPIO.output(pin, GPIO.LOW)
    
    # Clean up GPIO
    GPIO.cleanup()
    print("Cleanup complete")

def forward(left_pwm, right_pwm, speed=100, duration=2):
    """Move both motors forward."""
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

def backward(left_pwm, right_pwm, speed=100, duration=2):
    """Move both motors backward."""
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

def stop(left_pwm, right_pwm, duration=1):
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

def test_motors():
    """Run a complete motor test sequence."""
    print("=== L298N Motor Controller Test ===")
    print("LEFT MOTOR: ENA=GPIO12, IN1=GPIO23, IN2=GPIO24")
    print("RIGHT MOTOR: ENB=GPIO13, IN3=GPIO27, IN4=GPIO22")
    print("================================")
    
    try:
        # Initialize motors
        left_pwm, right_pwm = setup()
        
        # Test each motor separately first
        print("\n--- Testing LEFT motor ---")
        # Left motor forward
        GPIO.output(LEFT_IN1, GPIO.HIGH)
        GPIO.output(LEFT_IN2, GPIO.LOW)
        left_pwm.ChangeDutyCycle(70)
        GPIO.output(RIGHT_IN1, GPIO.LOW)
        GPIO.output(RIGHT_IN2, GPIO.LOW)
        right_pwm.ChangeDutyCycle(0)
        print("LEFT motor forward")
        time.sleep(2)
        
        # Left motor stop
        GPIO.output(LEFT_IN1, GPIO.LOW)
        GPIO.output(LEFT_IN2, GPIO.LOW)
        left_pwm.ChangeDutyCycle(0)
        print("LEFT motor stopped")
        time.sleep(1)
        
        print("\n--- Testing RIGHT motor ---")
        # Right motor forward
        GPIO.output(RIGHT_IN1, GPIO.HIGH)
        GPIO.output(RIGHT_IN2, GPIO.LOW)
        right_pwm.ChangeDutyCycle(70)
        GPIO.output(LEFT_IN1, GPIO.LOW)
        GPIO.output(LEFT_IN2, GPIO.LOW)
        left_pwm.ChangeDutyCycle(0)
        print("RIGHT motor forward")
        time.sleep(2)
        
        # Right motor stop
        GPIO.output(RIGHT_IN1, GPIO.LOW)
        GPIO.output(RIGHT_IN2, GPIO.LOW)
        right_pwm.ChangeDutyCycle(0)
        print("RIGHT motor stopped")
        time.sleep(1)
        
        # Test full movement sequences
        print("\n--- Testing combined movements ---")
        # Forward
        forward(left_pwm, right_pwm, speed=100, duration=2)
        
        # Stop
        stop(left_pwm, right_pwm)
        
        # Backward
        backward(left_pwm, right_pwm, speed=100, duration=2)
        
        # Stop
        stop(left_pwm, right_pwm)
        
        # Forward with different speeds
        print("\n--- Testing gradual acceleration ---")
        for speed in [25, 50, 75, 100]:
            print(f"\nSpeed: {speed}%")
            
            # Set up motor direction for forward
            GPIO.output(LEFT_IN1, GPIO.HIGH)
            GPIO.output(LEFT_IN2, GPIO.LOW)
            GPIO.output(RIGHT_IN1, GPIO.HIGH)
            GPIO.output(RIGHT_IN2, GPIO.LOW)
            
            # Set speed via PWM
            left_pwm.ChangeDutyCycle(speed)
            right_pwm.ChangeDutyCycle(speed)
            
            # Run for 1 second at each speed
            time.sleep(1)
        
        # Final stop
        stop(left_pwm, right_pwm)
        
        print("\nMotor test completed successfully!")
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nError occurred: {e}")
    finally:
        # Always clean up
        cleanup(left_pwm, right_pwm)

if __name__ == "__main__":
    test_motors()
