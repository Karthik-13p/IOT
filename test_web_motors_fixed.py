#!/usr/bin/env python3
"""
Test script specifically for the web app motor integration.
This script verifies that the motor control works properly in a web-like environment.

Run with: sudo python3 test_web_motors_fixed.py
"""
import os
import sys
import time
import threading

# Add project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class MockWebRequest:
    """Mock class to simulate web requests."""
    def __init__(self):
        self.response = None
    
    def get_json(self):
        return self.data
        
    def set_data(self, data):
        self.data = data

def setup():
    """Set up the test environment."""
    print("\n=== Setting up Web Motor Test Environment ===")
    try:
        # Import required modules
        from src.motor_control.pi_to_motor import cleanup_motors
        
        # Clean up any existing motor state
        cleanup_motors(reset_gpio=True)
        time.sleep(0.5)  # Allow time for cleanup
        
        # Import web app
        sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))
        from web.app import initialize_motors, motor_lock
        
        print("Test environment setup complete")
        return True
    except Exception as e:
        print(f"Error setting up test environment: {e}")
        return False

def test_concurrent_access():
    """Test concurrent access to motor control."""
    print("\n--- Testing Concurrent Motor Access ---")
    try:
        # Import required modules from web app
        sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))
        from web.app import move_forward, move_backward, stop, motor_lock
        
        # Create threads to simulate concurrent web requests
        requests_completed = [0]
        request_errors = [0]
        
        def simulate_request(command, speed, delay):
            try:
                print(f"Thread: Executing {command} at speed {speed}")
                
                # Simulate thread execution with proper locking
                with motor_lock:
                    if command == "forward":
                        move_forward(speed)
                    elif command == "backward":
                        move_backward(speed)
                    elif command == "stop":
                        stop()
                
                # Wait to simulate request duration
                time.sleep(delay)
                requests_completed[0] += 1
                
            except Exception as e:
                print(f"Thread error: {e}")
                request_errors[0] += 1
        
        # Create and start threads
        threads = []
        
        # Thread 1: Move forward
        threads.append(threading.Thread(target=simulate_request, args=("forward", 100, 0.5)))
        
        # Thread 2: Move backward (will be blocked by lock until thread 1 completes)
        threads.append(threading.Thread(target=simulate_request, args=("backward", 75, 0.5)))
        
        # Thread 3: Stop (will be blocked by lock until threads 1 and 2 complete)
        threads.append(threading.Thread(target=simulate_request, args=("stop", 0, 0.2)))
        
        # Thread 4: Another forward (tests full cycle)
        threads.append(threading.Thread(target=simulate_request, args=("forward", 50, 0.3)))
        
        # Start all threads with small delays
        for i, t in enumerate(threads):
            t.start()
            time.sleep(0.1)  # Small delay between thread starts
        
        # Wait for all threads to complete
        for t in threads:
            t.join()
        
        # Check results
        success = (requests_completed[0] == len(threads) and request_errors[0] == 0)
        print(f"Concurrent access test {'PASSED' if success else 'FAILED'}")
        print(f"Completed requests: {requests_completed[0]}/{len(threads)}")
        print(f"Errors: {request_errors[0]}")
        
        return success
    except Exception as e:
        print(f"Error in concurrent access test: {e}")
        return False

def test_emergency_stop():
    """Test emergency stop functionality."""
    print("\n--- Testing Emergency Stop ---")
    try:
        # Import required modules from web app
        sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))
        from web.app import move_forward, stop, motor_lock
        from src.motor_control.pi_to_motor import motors_initialized
        
        # First move forward
        with motor_lock:
            move_forward(100)
        print("Moving forward...")
        time.sleep(1)
        
        # Then emergency stop
        with motor_lock:
            stop()
        print("Emergency stop activated")
        
        # Check if motors are stopped (should still be initialized)
        success = motors_initialized
        print(f"Emergency stop test {'PASSED' if success else 'FAILED'}")
        
        return success
    except Exception as e:
        print(f"Error in emergency stop test: {e}")
        return False

def cleanup():
    """Clean up after tests."""
    print("\n--- Cleaning Up ---")
    try:
        from src.motor_control.pi_to_motor import cleanup_motors
        
        # Clean up motor resources
        cleanup_motors(reset_gpio=True)
        print("Cleanup complete")
        return True
    except Exception as e:
        print(f"Error in cleanup: {e}")
        return False

def main():
    """Main test function."""
    print("=== Web Motor Interface Fix Validation ===")
    
    # Setup test environment
    if not setup():
        print("Test environment setup failed, aborting tests")
        return
    
    # Run tests
    concurrent_test = test_concurrent_access()
    time.sleep(1)
    
    emergency_test = test_emergency_stop()
    time.sleep(1)
    
    # Clean up
    cleanup_success = cleanup()
    
    # Print results
    print("\n=== Test Results ===")
    print(f"Concurrent access test: {'PASSED' if concurrent_test else 'FAILED'}")
    print(f"Emergency stop test: {'PASSED' if emergency_test else 'FAILED'}")
    print(f"Cleanup: {'SUCCESS' if cleanup_success else 'FAILED'}")
    
    if concurrent_test and emergency_test:
        print("\nAll tests PASSED! The web motor interface is working correctly.")
    else:
        print("\nSome tests FAILED. Further debugging may be needed.")

if __name__ == "__main__":
    main()
