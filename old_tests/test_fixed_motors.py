#!/usr/bin/env python3
"""
Test script for motor control using the pi_to_motor module
"""
import sys
import time
import os

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import motor control functions
from src.motor_control.pi_to_motor import initialize_motors, set_motor_speed, move_forward, move_backward, stop, cleanup_motors

def print_header():
    print("==================================")
    print("Motor Control Test (Updated Version)")
    print("==================================")
    print("This test will verify motor functionality")
    print("Press CTRL+C to stop the test at any time")
    print()

def test_setup():
    print("Initializing motors...")
    success = initialize_motors(timeout=5.0)
    if success:
        print("Motors initialized successfully")
        return True
    else:
        print("Failed to initialize motors")
        return False

def test_forward_backward():
    print("\nTesting FORWARD movement (3 seconds)...")
    move_forward(speed=70)
    time.sleep(3)
    
    print("\nStopping (1 second)...")
    stop()
    time.sleep(1)
    
    print("\nTesting BACKWARD movement (3 seconds)...")
    move_backward(speed=70)
    time.sleep(3)
    
    print("\nStopping...")
    stop()
    time.sleep(1)

def test_individual_motors():
    print("\nTesting individual motors...")
    
    # Test motors 1 and 2 separately (these should correspond to left and right)
    for motor_num in [1, 2]:
        print(f"\nTesting Motor {motor_num} Forward (2 seconds)...")
        set_motor_speed(motor_num, 70)
        time.sleep(2)
        
        print(f"Stopping Motor {motor_num} (1 second)...")
        set_motor_speed(motor_num, 0)
        time.sleep(1)
        
        print(f"Testing Motor {motor_num} Backward (2 seconds)...")
        set_motor_speed(motor_num, -70)
        time.sleep(2)
        
        print(f"Stopping Motor {motor_num}...")
        set_motor_speed(motor_num, 0)
        time.sleep(1)

def main():
    print_header()
    
    try:
        if not test_setup():
            return
        
        test_forward_backward()
        test_individual_motors()
        
        print("\nAll tests completed successfully!")
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nError during test: {e}")
    finally:
        print("\nCleaning up...")
        try:
            stop()
            cleanup_motors()
            print("Motors cleaned up successfully")
        except Exception as e:
            print(f"Error during cleanup: {e}")

if __name__ == "__main__":
    main()
