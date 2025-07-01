#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

# Motor pins
LEFT_PWM = 12   # ENA
LEFT_IN1 = 23
LEFT_IN2 = 24

RIGHT_PWM = 13  # ENB
RIGHT_IN1 = 27
RIGHT_IN2 = 22

PWM_FREQ = 1000
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
    
    print("GPIO setup complete")
    return left_pwm, right_pwm

def forward(left_pwm, right_pwm):
    """Move both motors forward."""
    print("\nMoving Forward")
    
    # Left motor forward
    GPIO.output(LEFT_IN1, GPIO.HIGH)
    GPIO.output(LEFT_IN2, GPIO.LOW)
    left_pwm.ChangeDutyCycle(DUTY_CYCLE)
    
    # Right motor forward
    GPIO.output(RIGHT_IN1, GPIO.HIGH)
    GPIO.output(RIGHT_IN2, GPIO.LOW)
    right_pwm.ChangeDutyCycle(DUTY_CYCLE)

def backward(left_pwm, right_pwm):
    """Move both motors backward."""
    print("\nMoving Backward")
    
    # Left motor backward
    GPIO.output(LEFT_IN1, GPIO.LOW)
    GPIO.output(LEFT_IN2, GPIO.HIGH)
    left_pwm.ChangeDutyCycle(DUTY_CYCLE)
    
    # Right motor backward
    GPIO.output(RIGHT_IN1, GPIO.LOW)
    GPIO.output(RIGHT_IN2, GPIO.HIGH)
    right_pwm.ChangeDutyCycle(DUTY_CYCLE)

def stop(left_pwm, right_pwm):
    """Stop both motors."""
    print("\nStopping")
    
    # Stop left motor
    GPIO.output(LEFT_IN1, GPIO.LOW)
    GPIO.output(LEFT_IN2, GPIO.LOW)
    left_pwm.ChangeDutyCycle(0)
    
    # Stop right motor
    GPIO.output(RIGHT_IN1, GPIO.LOW)
    GPIO.output(RIGHT_IN2, GPIO.LOW)
    right_pwm.ChangeDutyCycle(0)

def cleanup(left_pwm, right_pwm):
    """Clean up GPIO resources."""
    print("\nCleaning up")
    stop(left_pwm, right_pwm)
    left_pwm.stop()
    right_pwm.stop()
    GPIO.cleanup()

def test_motors():
    """Test motor functionality."""
    print("L298N Motor Control Test")
    print("=======================")
    print(f"PWM Frequency: {PWM_FREQ} Hz")
    print(f"Duty Cycle: {DUTY_CYCLE}%")
    
    try:
        # Initialize GPIO and get PWM objects
        left_pwm, right_pwm = setup()
        
        # Test sequence
        for direction in ["forward", "backward"]:
            print(f"\nTesting {direction} movement for 3 seconds...")
            if direction == "forward":
                forward(left_pwm, right_pwm)
            else:
                backward(left_pwm, right_pwm)
            
            time.sleep(3)
            
            print("Stopping for 1 second...")
            stop(left_pwm, right_pwm)
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nError occurred: {e}")
    finally:
        cleanup(left_pwm, right_pwm)
        print("\nTest complete")

if __name__ == "__main__":
    test_motors()
