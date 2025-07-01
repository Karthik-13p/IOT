#!/usr/bin/env python3
"""
Test script to verify backward motor functionality
"""
import sys
import time
import os

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import motor control functions
from src.motor_control.pi_to_motor import initialize_motors, set_motor_speed, cleanup_motors

def test_motor_backward(motor_num, speed=50, duration=2.0):
    """Test a specific motor's backward functionality"""
    print(f"\nTesting Motor {motor_num} Backward at speed {speed}")
    print("--------------------------------------------")
    
    # Set the motor to run backward (negative speed)
    set_motor_speed(motor_num, -speed)
    
    # Keep it running for the specified duration
    print(f"Motor {motor_num} running backward for {duration} seconds...")
    time.sleep(duration)
    
    # Stop the motor
    set_motor_speed(motor_num, 0)
    print(f"Motor {motor_num} stopped")

def test_motor_forward(motor_num, speed=50, duration=2.0):
    """Test a specific motor's forward functionality"""
    print(f"\nTesting Motor {motor_num} Forward at speed {speed}")
    print("--------------------------------------------")
    
    # Set the motor to run forward (positive speed)
    set_motor_speed(motor_num, speed)
    
    # Keep it running for the specified duration
    print(f"Motor {motor_num} running forward for {duration} seconds...")
    time.sleep(duration)
    
    # Stop the motor
    set_motor_speed(motor_num, 0)
    print(f"Motor {motor_num} stopped")

def main():
    """Main test function"""
    print("Motor Backward Test")
    print("==================")
    
    # Initialize motors
    print("Initializing motors...")
    if not initialize_motors():
        print("Failed to initialize motors!")
        return
    
    try:
        # Test each motor individually
        for motor_num in range(1, 5):
            # Test forward first to verify motor works
            test_motor_forward(motor_num, speed=50, duration=2.0)
            
            # Then test backward
            test_motor_backward(motor_num, speed=50, duration=2.0)
            
            # Pause between motors
            time.sleep(1.0)
    
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    finally:
        # Clean up
        cleanup_motors()
        print("\nTest complete")

if __name__ == "__main__":
    main()
