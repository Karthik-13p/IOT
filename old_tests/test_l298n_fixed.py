#!/usr/bin/env python3
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

PWM_FREQ = 1000  # 1 kHz PWM frequency
DUTY_CYCLE = 100  # Full speed

def setup():
    """Set up GPIO pins and PWM."""
    print("Setting up GPIO pins...")
    
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
    
    # Create PWM objects
    left_pwm = GPIO.PWM(LEFT_PWM, PWM_FREQ)
    right_pwm = GPIO.PWM(RIGHT_PWM, PWM_FREQ)
    
    # Start PWM with 0% duty cycle (motors stopped)
    left_pwm.start(0)
    right_pwm.start(0)
    
    print(f"GPIO setup complete with PWM frequency {PWM_FREQ}Hz")
    return left_pwm, right_pwm

def forward(left_pwm, right_pwm, speed=DUTY_CYCLE):
    """Move both motors forward."""
    print("\nMoving Forward")
    
    # Left motor forward
    GPIO.output(LEFT_IN1, GPIO.HIGH)
    GPIO.output(LEFT_IN2, GPIO.LOW)
    left_pwm.ChangeDutyCycle(speed)
    
    # Right motor forward
    GPIO.output(RIGHT_IN1, GPIO.HIGH)
    GPIO.output(RIGHT_IN2, GPIO.LOW)
    right_pwm.ChangeDutyCycle(speed)

def backward(left_pwm, right_pwm, speed=DUTY_CYCLE):
    """Move both motors backward."""
    print("\nMoving Backward")
    
    # Left motor backward
    GPIO.output(LEFT_IN1, GPIO.LOW)
    GPIO.output(LEFT_IN2, GPIO.HIGH)
    left_pwm.ChangeDutyCycle(speed)
    
    # Right motor backward
    GPIO.output(RIGHT_IN1, GPIO.LOW)
    GPIO.output(RIGHT_IN2, GPIO.HIGH)
    right_pwm.ChangeDutyCycle(speed)

def turn_left(left_pwm, right_pwm, speed=DUTY_CYCLE):
    """Turn left by running right motor forward and left motor backward."""
    print("\nTurning Left")
    
    # Left motor stop or reverse
    GPIO.output(LEFT_IN1, GPIO.LOW)
    GPIO.output(LEFT_IN2, GPIO.HIGH)
    left_pwm.ChangeDutyCycle(speed//2)  # Slow speed for left motor
    
    # Right motor forward
    GPIO.output(RIGHT_IN1, GPIO.HIGH)
    GPIO.output(RIGHT_IN2, GPIO.LOW)
    right_pwm.ChangeDutyCycle(speed)

def turn_right(left_pwm, right_pwm, speed=DUTY_CYCLE):
    """Turn right by running left motor forward and right motor backward."""
    print("\nTurning Right")
    
    # Left motor forward
    GPIO.output(LEFT_IN1, GPIO.HIGH)
    GPIO.output(LEFT_IN2, GPIO.LOW)
    left_pwm.ChangeDutyCycle(speed)
    
    # Right motor stop or reverse
    GPIO.output(RIGHT_IN1, GPIO.LOW)
    GPIO.output(RIGHT_IN2, GPIO.HIGH)
    right_pwm.ChangeDutyCycle(speed//2)  # Slow speed for right motor

def stop(left_pwm, right_pwm):
    """Stop both motors."""
    print("\nStopping")
    
    # Stop left motor - set both inputs LOW
    GPIO.output(LEFT_IN1, GPIO.LOW)
    GPIO.output(LEFT_IN2, GPIO.LOW)
    left_pwm.ChangeDutyCycle(0)
    
    # Stop right motor - set both inputs LOW
    GPIO.output(RIGHT_IN1, GPIO.LOW)
    GPIO.output(RIGHT_IN2, GPIO.LOW)
    right_pwm.ChangeDutyCycle(0)

def cleanup(left_pwm, right_pwm):
    """Clean up GPIO resources."""
    print("\nCleaning up GPIO resources")
    
    # First stop the motors
    stop(left_pwm, right_pwm)
    
    try:
        # Set duty cycle to 0 before stopping PWM
        left_pwm.ChangeDutyCycle(0)
        right_pwm.ChangeDutyCycle(0)
        
        # Stop PWM objects
        left_pwm.stop()
        print("Left motor PWM stopped")
        right_pwm.stop()
        print("Right motor PWM stopped")
    except Exception as e:
        print(f"Warning during PWM cleanup: {e}")
        
    # Finally clean up GPIO
    try:
        GPIO.cleanup()
        print("GPIO cleanup complete")
    except Exception as e:
        print(f"Warning during GPIO cleanup: {e}")

def test_motors():
    """Test motor functionality with proper error handling."""
    print("L298N Motor Control Test (Fixed Version)")
    print("======================================")
    print(f"PWM Frequency: {PWM_FREQ} Hz")
    print(f"Maximum Duty Cycle: {DUTY_CYCLE}%")
    print("Press Ctrl+C to exit")
    
    left_pwm = None
    right_pwm = None
    
    try:
        # Initialize GPIO and get PWM objects
        left_pwm, right_pwm = setup()
        
        # Test sequence
        print("\nTesting basic movements (2 seconds each):")
        
        # Forward
        forward(left_pwm, right_pwm)
        time.sleep(2)
        
        # Stop
        stop(left_pwm, right_pwm)
        time.sleep(1)
        
        # Backward
        backward(left_pwm, right_pwm)
        time.sleep(2)
        
        # Stop
        stop(left_pwm, right_pwm)
        time.sleep(1)
        
        # Turn left
        turn_left(left_pwm, right_pwm)
        time.sleep(2)
        
        # Stop
        stop(left_pwm, right_pwm)
        time.sleep(1)
        
        # Turn right
        turn_right(left_pwm, right_pwm)
        time.sleep(2)
        
        # Final stop
        stop(left_pwm, right_pwm)
        
        print("\nMotor test completed successfully!")
    
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nError occurred: {e}")
    finally:
        # Always clean up, even if there was an error
        if left_pwm is not None and right_pwm is not None:
            cleanup(left_pwm, right_pwm)
        print("\nTest complete")

if __name__ == "__main__":
    test_motors()
