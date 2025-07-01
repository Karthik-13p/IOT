#!/usr/bin/env python3
"""
Test script for the motor_control module in pi_to_motor.py
"""
import sys
import time
import os

# Add project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import motor control functions
from src.motor_control.pi_to_motor import initialize_motors, move_forward, move_backward, stop, set_motor_speed, cleanup_motors

def main():
    print("Testing pi_to_motor.py Motor Control Module")
    print("==========================================")
    
    try:
        # Initialize motors
        print("\n1. Initializing motors")
        success = initialize_motors()
        if not success:
            print("Failed to initialize motors!")
            return
        print("Motors initialized successfully")
        
        # Test motor movement
        print("\n2. Testing forward movement (2 seconds)")
        move_forward(speed=70)
        time.sleep(2)
        
        print("\n3. Stopping (1 second)")
        stop()
        time.sleep(1)
        
        print("\n4. Testing backward movement (2 seconds)")
        move_backward(speed=70)
        time.sleep(2)
        
        print("\n5. Stopping (1 second)")
        stop()
        time.sleep(1)
        
        # Test individual motors
        print("\n6. Testing motor 1 (left) forward (2 seconds)")
        set_motor_speed(1, 70)
        time.sleep(2)
        set_motor_speed(1, 0)
        
        print("\n7. Testing motor 2 (right) forward (2 seconds)")
        set_motor_speed(2, 70)
        time.sleep(2)
        set_motor_speed(2, 0)
        
        print("\nTest completed successfully!")
    
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nError occurred: {e}")
    finally:
        print("\nCleaning up...")
        stop()
        cleanup_motors()  # No parameters

if __name__ == "__main__":
    main()
