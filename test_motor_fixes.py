#!/usr/bin/env python3
"""
Test script for the web motor interface fix.
This script tests both the direct motor control and simulates web app access.

Run with: sudo python3 test_motor_fixes.py
"""
import os
import sys
import time
import threading

print("=== Testing Motor Control and Web App Integration ===")

# Add project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_direct_motor_control():
    """Test direct motor control."""
    print("\n--- Testing Direct Motor Control ---")
    try:
        from src.motor_control.pi_to_motor import (
            initialize_motors, cleanup_motors, move_forward, 
            move_backward, stop, set_motor_speed
        )
        
        print("Motor modules imported successfully")
        
        # Initialize motors
        if initialize_motors(timeout=5.0):
            print("Motors initialized successfully")
            
            # Test forward
            print("Moving forward...")
            move_forward(100)
            time.sleep(2)
            
            # Test stop
            print("Stopping...")
            stop()
            time.sleep(1)
            
            # Test backward
            print("Moving backward...")
            move_backward(100)
            time.sleep(2)
            
            # Final stop
            print("Final stop...")
            stop()
            
            # Clean up
            cleanup_motors(reset_gpio=True)
            print("Direct motor test completed successfully")
            return True
        else:
            print("Failed to initialize motors")
            return False
            
    except Exception as e:
        print(f"Error in direct motor test: {e}")
        return False

def simulate_web_app_access():
    """Simulate multiple web app motor control requests."""
    print("\n--- Simulating Web App Motor Access ---")
    
    try:
        from src.motor_control.pi_to_motor import (
            initialize_motors, cleanup_motors, move_forward, 
            move_backward, stop, set_motor_speed, motors_initialized
        )
        
        # Initialize motors
        if initialize_motors(timeout=5.0):
            print("Motors initialized for web simulation")
            
            # Create threads to simulate multiple web requests
            def forward_thread():
                print("Thread 1: Moving forward")
                move_forward(100)
                time.sleep(1)
                stop()
                
            def backward_thread():
                print("Thread 2: Moving backward")
                move_backward(100)
                time.sleep(1)
                stop()
                
            # Start threads
            t1 = threading.Thread(target=forward_thread)
            t2 = threading.Thread(target=backward_thread)
            
            t1.start()
            time.sleep(0.2)  # Small delay between thread starts
            t2.start()
            
            # Wait for threads to complete
            t1.join()
            t2.join()
            
            # Final cleanup
            cleanup_motors(reset_gpio=True)
            print("Web simulation completed successfully")
            return True
        else:
            print("Failed to initialize motors for web simulation")
            return False
            
    except Exception as e:
        print(f"Error in web simulation: {e}")
        return False

def main():
    """Main test function."""
    # Test direct motor control
    direct_result = test_direct_motor_control()
    
    # Allow time for cleanup between tests
    time.sleep(1)
    
    # Test web app simulation
    web_result = simulate_web_app_access()
    
    # Print results
    print("\n=== Test Results ===")
    print(f"Direct motor control test: {'PASSED' if direct_result else 'FAILED'}")
    print(f"Web app simulation test: {'PASSED' if web_result else 'FAILED'}")
    
    if direct_result and web_result:
        print("\nAll tests PASSED! The fix is working correctly.")
    else:
        print("\nSome tests FAILED. Further debugging may be needed.")

if __name__ == "__main__":
    main()
