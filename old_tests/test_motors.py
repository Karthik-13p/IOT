#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
import sys
import os

# Motor pins - ADJUST THESE TO MATCH YOUR WIRING
MOTOR1_IN1 = 23
MOTOR1_IN2 = 24
MOTOR1_EN = 25

MOTOR2_IN1 = 17
MOTOR2_IN2 = 27
MOTOR2_EN = 22

def setup():
    # Set GPIO mode
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # Set up motor pins
    GPIO.setup(MOTOR1_IN1, GPIO.OUT)
    GPIO.setup(MOTOR1_IN2, GPIO.OUT)
    GPIO.setup(MOTOR1_EN, GPIO.OUT)
    GPIO.setup(MOTOR2_IN1, GPIO.OUT)
    GPIO.setup(MOTOR2_IN2, GPIO.OUT)
    GPIO.setup(MOTOR2_EN, GPIO.OUT)
    
    # Create PWM objects
    motor1_pwm = GPIO.PWM(MOTOR1_EN, 100)
    motor2_pwm = GPIO.PWM(MOTOR2_EN, 100)
    
    # Start PWM
    motor1_pwm.start(0)
    motor2_pwm.start(0)
    
    return motor1_pwm, motor2_pwm

def test_motor(motor_num, in1, in2, pwm, speed=70):
    print(f"Testing Motor {motor_num} Forward")
    GPIO.output(in1, GPIO.HIGH)
    GPIO.output(in2, GPIO.LOW)
    pwm.ChangeDutyCycle(speed)
    time.sleep(3)
    
    print(f"Testing Motor {motor_num} Backward")
    GPIO.output(in1, GPIO.LOW)
    GPIO.output(in2, GPIO.HIGH)
    pwm.ChangeDutyCycle(speed)
    time.sleep(3)
    
    print(f"Stopping Motor {motor_num}")
    GPIO.output(in1, GPIO.LOW)
    GPIO.output(in2, GPIO.LOW)
    pwm.ChangeDutyCycle(0)
    time.sleep(1)

def cleanup(m1_pwm, m2_pwm):
    m1_pwm.stop()
    m2_pwm.stop()
    GPIO.cleanup()

def main():
    print("Motor Test Program")
    print("------------------")
    print("Make sure your motors are connected and the power supply is on")
    print("This will test each motor individually")
    print("CTRL+C to exit\n")
    
    try:
        motor1_pwm, motor2_pwm = setup()
        
        # Test motor 1
        test_motor(1, MOTOR1_IN1, MOTOR1_IN2, motor1_pwm)
        
        # Test motor 2
        test_motor(2, MOTOR2_IN1, MOTOR2_IN2, motor2_pwm)
        
        # Test both motors together
        print("Testing both motors forward")
        GPIO.output(MOTOR1_IN1, GPIO.HIGH)
        GPIO.output(MOTOR1_IN2, GPIO.LOW)
        GPIO.output(MOTOR2_IN1, GPIO.HIGH)
        GPIO.output(MOTOR2_IN2, GPIO.LOW)
        motor1_pwm.ChangeDutyCycle(70)
        motor2_pwm.ChangeDutyCycle(70)
        time.sleep(3)
        
        print("Stopping all motors")
        motor1_pwm.ChangeDutyCycle(0)
        motor2_pwm.ChangeDutyCycle(0)
        GPIO.output(MOTOR1_IN1, GPIO.LOW)
        GPIO.output(MOTOR1_IN2, GPIO.LOW)
        GPIO.output(MOTOR2_IN1, GPIO.LOW)
        GPIO.output(MOTOR2_IN2, GPIO.LOW)
        
    except KeyboardInterrupt:
        print("\nTest stopped by user")
    finally:
        cleanup(motor1_pwm, motor2_pwm)
        print("Test complete - GPIO cleaned up")

if __name__ == "__main__":
    main()
