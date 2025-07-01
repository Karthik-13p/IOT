#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

# Motor control pins - ADJUST THESE TO MATCH YOUR WIRING
MOTOR1_IN1 = 23
MOTOR1_IN2 = 24
MOTOR1_EN = 25  # This might need to be GPIO12 per your docs

MOTOR2_IN1 = 17
MOTOR2_IN2 = 27
MOTOR2_EN = 22  # This might need to be GPIO13 per your docs

# Ultrasonic sensor pins
TRIG_PIN = 18
ECHO_PIN = 17

def setup():
    """Set up GPIO pins."""
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # Motor pins
    GPIO.setup(MOTOR1_IN1, GPIO.OUT)
    GPIO.setup(MOTOR1_IN2, GPIO.OUT)
    GPIO.setup(MOTOR1_EN, GPIO.OUT)
    
    GPIO.setup(MOTOR2_IN1, GPIO.OUT)
    GPIO.setup(MOTOR2_IN2, GPIO.OUT)
    GPIO.setup(MOTOR2_EN, GPIO.OUT)
    
    # Ultrasonic sensor pins
    GPIO.setup(TRIG_PIN, GPIO.OUT)
    GPIO.setup(ECHO_PIN, GPIO.IN)
    
    # Create PWM objects
    motor1_pwm = GPIO.PWM(MOTOR1_EN, 100)
    motor2_pwm = GPIO.PWM(MOTOR2_EN, 100)
    
    # Start PWM
    motor1_pwm.start(0)
    motor2_pwm.start(0)
    
    return motor1_pwm, motor2_pwm

def read_distance():
    """Read distance from ultrasonic sensor."""
    # Send a 10us pulse to trigger the sensor
    GPIO.output(TRIG_PIN, False)
    time.sleep(0.1)
    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, False)
    
    # Set timeout
    timeout_start = time.time()
    timeout = 1.0  # 1 second timeout
    
    # Wait for echo start
    while GPIO.input(ECHO_PIN) == 0:
        pulse_start = time.time()
        if time.time() > timeout_start + timeout:
            return 400  # Return max distance on timeout
            
    # Wait for echo end
    while GPIO.input(ECHO_PIN) == 1:
        pulse_end = time.time()
        if time.time() > timeout_start + timeout:
            return 400  # Return max distance on timeout
    
    # Calculate distance
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)
    
    return distance

def test_motors_and_sensor():
    """Test motors and ultrasonic sensor."""
    try:
        motor1_pwm, motor2_pwm = setup()
        
        print("Starting comprehensive test...")
        print("\n1. Testing ultrasonic sensor")
        
        for i in range(5):
            distance = read_distance()
            print(f"Distance: {distance} cm")
            time.sleep(1)
        
        print("\n2. Testing Motor 1")
        # Forward
        print("Motor 1 forward")
        GPIO.output(MOTOR1_IN1, GPIO.HIGH)
        GPIO.output(MOTOR1_IN2, GPIO.LOW)
        for speed in [30, 50, 70, 90]:
            print(f"Speed: {speed}%")
            motor1_pwm.ChangeDutyCycle(speed)
            time.sleep(1)
        
        # Stop
        print("Motor 1 stop")
        GPIO.output(MOTOR1_IN1, GPIO.LOW)
        GPIO.output(MOTOR1_IN2, GPIO.LOW)
        motor1_pwm.ChangeDutyCycle(0)
        time.sleep(1)
        
        # Backward
        print("Motor 1 backward")
        GPIO.output(MOTOR1_IN1, GPIO.LOW)
        GPIO.output(MOTOR1_IN2, GPIO.HIGH)
        for speed in [30, 50, 70, 90]:
            print(f"Speed: {speed}%")
            motor1_pwm.ChangeDutyCycle(speed)
            time.sleep(1)
        
        # Stop
        print("Motor 1 stop")
        GPIO.output(MOTOR1_IN1, GPIO.LOW)
        GPIO.output(MOTOR1_IN2, GPIO.LOW)
        motor1_pwm.ChangeDutyCycle(0)
        time.sleep(1)
        
        print("\n3. Testing Motor 2")
        # Forward
        print("Motor 2 forward")
        GPIO.output(MOTOR2_IN1, GPIO.HIGH)
        GPIO.output(MOTOR2_IN2, GPIO.LOW)
        for speed in [30, 50, 70, 90]:
            print(f"Speed: {speed}%")
            motor2_pwm.ChangeDutyCycle(speed)
            time.sleep(1)
        
        # Stop
        print("Motor 2 stop")
        GPIO.output(MOTOR2_IN1, GPIO.LOW)
        GPIO.output(MOTOR2_IN2, GPIO.LOW)
        motor2_pwm.ChangeDutyCycle(0)
        time.sleep(1)
        
        # Backward
        print("Motor 2 backward")
        GPIO.output(MOTOR2_IN1, GPIO.LOW)
        GPIO.output(MOTOR2_IN2, GPIO.HIGH)
        for speed in [30, 50, 70, 90]:
            print(f"Speed: {speed}%")
            motor2_pwm.ChangeDutyCycle(speed)
            time.sleep(1)
        
        # Stop
        print("Motor 2 stop")
        GPIO.output(MOTOR2_IN1, GPIO.LOW)
        GPIO.output(MOTOR2_IN2, GPIO.LOW)
        motor2_pwm.ChangeDutyCycle(0)
        time.sleep(1)
        
        print("\n4. Testing both motors")
        # Both forward
        print("Both motors forward")
        GPIO.output(MOTOR1_IN1, GPIO.HIGH)
        GPIO.output(MOTOR1_IN2, GPIO.LOW)
        GPIO.output(MOTOR2_IN1, GPIO.HIGH)
        GPIO.output(MOTOR2_IN2, GPIO.LOW)
        motor1_pwm.ChangeDutyCycle(70)
        motor2_pwm.ChangeDutyCycle(70)
        time.sleep(2)
        
        # Both stop
        print("Both motors stop")
        GPIO.output(MOTOR1_IN1, GPIO.LOW)
        GPIO.output(MOTOR1_IN2, GPIO.LOW)
        GPIO.output(MOTOR2_IN1, GPIO.LOW)
        GPIO.output(MOTOR2_IN2, GPIO.LOW)
        motor1_pwm.ChangeDutyCycle(0)
        motor2_pwm.ChangeDutyCycle(0)
        
    finally:
        # Clean up
        motor1_pwm.stop()
        motor2_pwm.stop()
        GPIO.cleanup()
        print("\nTest complete - GPIO cleaned up")

if __name__ == "__main__":
    test_motors_and_sensor()
