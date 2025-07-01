#!/usr/bin/env python3
"""
Web Motor Interface Fix

This script fixes the issue with motors working in test scripts but not in the web interface.
The main problems are:

1. Thread safety issues when the web app accesses motor control
2. Ensuring motors are properly initialized in the web context
3. PWM frequency consistency between test and web app
4. Cleanup handling differences between test and web app

Apply the fix by running: sudo python3 apply_web_motor_fix.py
"""
import os
import sys
import time
import re
import shutil
from datetime import datetime

def print_section(title):
    """Print a formatted section title."""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def backup_file(filepath):
    """Create a backup of a file."""
    if os.path.exists(filepath):
        backup_path = f"{filepath}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
        shutil.copy2(filepath, backup_path)
        print(f"Created backup: {backup_path}")
        return backup_path
    return None

def fix_web_app():
    """Fix the web app motor control."""
    print_section("Fixing Web App Motor Control")
    
    web_app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'web', 'app.py')
    
    if not os.path.exists(web_app_path):
        print(f"Error: Web app file not found at {web_app_path}")
        return False
    
    # Backup the file
    backup_path = backup_file(web_app_path)
    if not backup_path:
        print("Error: Failed to create backup")
        return False
    
    try:
        # Read the file
        with open(web_app_path, 'r') as f:
            content = f.read()
        
        # Create a modified content with fixes
        modified_content = content
        
        # Fix 1: Add a thread lock for motor access
        thread_lock_imports = """import threading
import time
import os
import sys
import requests
import json
import logging
import atexit

# Create a thread lock for motor access to ensure thread safety
motor_lock = threading.Lock()

# Set up logging"""

        modified_content = modified_content.replace("""import threading
import time
import os
import sys
import requests
import json
import logging
import atexit

# Set up logging""", thread_lock_imports)
        
        # Fix 2: Fix the motor initialization in the web app
        initialization_code = """# Initialize motors when app starts
try:
    if initialize_motors(timeout=10.0):  # Increased timeout for better reliability
        print("Motors initialized successfully in web app with 1kHz PWM frequency")
        # Set all motors to LOW state to ensure they're ready for commands
        from motor_control.pi_to_motor import stop
        stop()
        print("Motors set to initial stopped state")
    else:
        print("Failed to initialize motors in web app")
except Exception as e:
    print(f"Error initializing motors in web app: {e}")"""

        improved_initialization = """# Initialize motors when app starts - with thread safety and explicit cleanup first
try:
    # First ensure any previous motor instances are cleaned up
    from motor_control.pi_to_motor import cleanup_motors
    cleanup_motors(reset_gpio=True)
    time.sleep(0.2)  # Small delay to ensure cleanup completes
    
    # Then initialize motors with thread safety
    with motor_lock:
        if initialize_motors(timeout=10.0):  # Increased timeout for better reliability
            print("Motors initialized successfully in web app with 1kHz PWM frequency")
            # Set all motors to LOW state to ensure they're ready for commands
            from motor_control.pi_to_motor import stop
            stop()
            print("Motors set to initial stopped state")
        else:
            print("Failed to initialize motors in web app")
except Exception as e:
    print(f"Error initializing motors in web app: {e}")"""
        
        modified_content = modified_content.replace(initialization_code, improved_initialization)
        
        # Fix 3: Use thread lock in motor control endpoints        control_motors_original = """@app.route(\'/api/motors/control\', methods=[\'POST\'])
def control_motors():
    \"\"\"API endpoint to control motors.\"\"\""
    try:
        data = request.get_json()
        command = data.get('command')
        speed = int(data.get('speed', motor_state["speed"]))
        
        # Optimize for full speed operation when speed is near maximum
        if speed > 95:
            speed = 100
        
        print(f"Motor control: Command={command}, Speed={speed}")
        
        motor_state["speed"] = speed
        
        # Use thread lock for thread safety
        with motor_lock:
            if command == 'start':
                # Make sure motors are initialized
                if not hasattr(sys.modules['motor_control.pi_to_motor'], 'motors_initialized') or not sys.modules['motor_control.pi_to_motor'].motors_initialized:
                    if not initialize_motors(timeout=10.0):  # Increased timeout for reliability
                        return jsonify({"status": "error", "message": "Failed to initialize motors"})
                
                motor_state["running"] = True
                stop()  # Ensure motors are stopped before changing state
                print("Motors started")
                return jsonify({"status": "success", "message": "Motors started"})"""

        modified_content = modified_content.replace(control_motors_original, control_motors_fixed)
        
        # Fix 4: Add thread safety to other motor control blocks in the same function
        moving_forward_original = """elif command == 'forward':
            motor_state["direction"] = "forward"
            result = move_forward(speed)
            print(f"Moving forward at speed {speed}, result: {result}")
            
        elif command == 'backward':
            motor_state["direction"] = "backward"
            result = move_backward(speed)
            print(f"Moving backward at speed {speed}, result: {result}")"""
        
        moving_forward_fixed = """elif command == 'forward':
            motor_state["direction"] = "forward"
            # Make sure motors are initialized when running movement commands
            if not hasattr(sys.modules['motor_control.pi_to_motor'], 'motors_initialized') or not sys.modules['motor_control.pi_to_motor'].motors_initialized:
                print("Motors not initialized, initializing now...")
                if not initialize_motors(timeout=5.0):
                    return jsonify({"status": "error", "message": "Failed to initialize motors for forward movement"})
            
            result = move_forward(speed)
            print(f"Moving forward at speed {speed}, result: {result}")
            
        elif command == 'backward':
            motor_state["direction"] = "backward"
            # Make sure motors are initialized when running movement commands
            if not hasattr(sys.modules['motor_control.pi_to_motor'], 'motors_initialized') or not sys.modules['motor_control.pi_to_motor'].motors_initialized:
                print("Motors not initialized, initializing now...")
                if not initialize_motors(timeout=5.0):
                    return jsonify({"status": "error", "message": "Failed to initialize motors for backward movement"})
            
            result = move_backward(speed)
            print(f"Moving backward at speed {speed}, result: {result}")"""
        
        modified_content = modified_content.replace(moving_forward_original, moving_forward_fixed)
        
        # Fix 5: Fix the cleanup function to ensure proper order of operations
        cleanup_original = """# Register cleanup function to run when app exits
@atexit.register
def cleanup_app():
    """Clean up resources when app exits."""
    try:
        print("Cleaning up motor resources in web app...")
        # First stop all motors
        try:
            stop()
            print("Motors stopped")
            time.sleep(0.1)  # Small delay to ensure motors have time to stop
        except Exception as e:
            print(f"Warning: Error stopping motors: {e}")
            
        # Then clean up GPIO resources - don't reset GPIO as main process will do that
        cleanup_motors(reset_gpio=False)
        print("Motor resources cleaned up")
    except Exception as e:
        print(f"Error during web app cleanup: {e}")"""

        cleanup_fixed = """# Register cleanup function to run when app exits
@atexit.register
def cleanup_app():
    """Clean up resources when app exits."""
    try:
        print("Cleaning up motor resources in web app...")
        # Use thread lock for safety
        with motor_lock:
            # First stop all motors
            try:
                stop()
                print("Motors stopped")
                time.sleep(0.2)  # Increased delay to ensure motors have time to stop
            except Exception as e:
                print(f"Warning: Error stopping motors: {e}")
                
            # Then clean up GPIO resources with explicit reset to ensure clean state
            try:
                cleanup_motors(reset_gpio=True)
                print("Motor resources cleaned up")
            except Exception as e:
                print(f"Warning: Error cleaning up motor resources: {e}")
    except Exception as e:
        print(f"Error during web app cleanup: {e}")"""
                
        modified_content = modified_content.replace(cleanup_original, cleanup_fixed)

        # Fix 6: Add thread safety to the emergency stop endpoint
        emergency_stop_original = """@app.route('/api/emergency_stop')
def emergency_stop():
    """API endpoint for emergency stop."""
    try:
        # Make sure motors are initialized
        if not hasattr(sys.modules['motor_control.pi_to_motor'], 'motors_initialized') or not sys.modules['motor_control.pi_to_motor'].motors_initialized:
            # Try to initialize if needed
            initialize_motors(timeout=2.0)
            
        stop()
        motor_state["running"] = False
        motor_state["direction"] = "stop"
        return jsonify({"status": "success", "message": "Emergency stop activated"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})"""

        emergency_stop_fixed = """@app.route('/api/emergency_stop')
def emergency_stop():
    """API endpoint for emergency stop."""
    try:
        # Use thread lock for safety
        with motor_lock:
            # Make sure motors are initialized
            if not hasattr(sys.modules['motor_control.pi_to_motor'], 'motors_initialized') or not sys.modules['motor_control.pi_to_motor'].motors_initialized:
                # Try to initialize if needed
                initialize_motors(timeout=5.0)  # Increased timeout for reliability
                
            stop()
            motor_state["running"] = False
            motor_state["direction"] = "stop"
            return jsonify({"status": "success", "message": "Emergency stop activated"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})"""
        
        modified_content = modified_content.replace(emergency_stop_original, emergency_stop_fixed)
        
        # Write the modified content back to the file
        with open(web_app_path, 'w') as f:
            f.write(modified_content)
            
        print(f"Fixed web app file: {web_app_path}")
        return True
        
    except Exception as e:
        print(f"Error fixing web app: {e}")
        
        # Restore backup if something went wrong
        if backup_path and os.path.exists(backup_path):
            shutil.copy2(backup_path, web_app_path)
            print(f"Restored original file from backup")
            
        return False

def fix_motor_control():
    """Fix the motor control module."""
    print_section("Fixing Motor Control Module")
    
    motor_control_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                      'src', 'motor_control', 'pi_to_motor.py')
    
    if not os.path.exists(motor_control_path):
        print(f"Error: Motor control file not found at {motor_control_path}")
        return False
    
    # Backup the file
    backup_path = backup_file(motor_control_path)
    if not backup_path:
        print("Error: Failed to create backup")
        return False
    
    try:
        # Read the file
        with open(motor_control_path, 'r') as f:
            content = f.read()
        
        # Create a modified content with fixes
        modified_content = content
        
        # Fix 1: Ensure proper thread locking for motor control
        if "motor_lock = threading.Lock()" not in content:
            imports = "import RPi.GPIO as GPIO\nimport time\nimport json\nimport os\nimport threading"
            modified_imports = "import RPi.GPIO as GPIO\nimport time\nimport json\nimport os\nimport threading\nfrom threading import Timer"
            
            modified_content = modified_content.replace(imports, modified_imports)
            
            # Add thread lock declaration if it doesn't exist
            lock_declaration = "# Global variables for motor control\nmotor_pwm = {\n    1: None,\n    2: None,\n    3: None,\n    4: None\n}\nmotors_initialized = False"
            modified_lock_declaration = "# Global variables for motor control\nmotor_pwm = {\n    1: None,\n    2: None,\n    3: None,\n    4: None\n}\nmotors_initialized = False\nmotor_lock = threading.Lock()"
            
            modified_content = modified_content.replace(lock_declaration, modified_lock_declaration)
        
        # Fix 2: Ensure thread safety in the initialization function
        initialize_original = """def initialize_motors(timeout=2.0):
    """Initialize the GPIO pins for motor control with timeout."""
    global motors_initialized, motor_pwm
    
    # Use a timeout to prevent hanging
    initialization_done = threading.Event()
    initialization_success = [False]  # Use a list to modify in the thread"""
        
        initialize_fixed = """def initialize_motors(timeout=2.0):
    """Initialize the GPIO pins for motor control with timeout."""
    global motors_initialized, motor_pwm
    
    # Use thread lock for thread safety
    with motor_lock:
        # Use a timeout to prevent hanging
        initialization_done = threading.Event()
        initialization_success = [False]  # Use a list to modify in the thread"""
        
        modified_content = modified_content.replace(initialize_original, initialize_fixed)
        
        # Fix 3: Add lock to set_motor_speed function
        set_motor_speed_original = """def set_motor_speed(motor_num, speed):
    """Set the speed of a specific motor (-100 to 100)."""
    global motors_initialized, motor_pwm
    
    if not motors_initialized:
        print(f"Motors not initialized. Cannot set motor {motor_num} speed.")
        return False"""
        
        set_motor_speed_fixed = """def set_motor_speed(motor_num, speed):
    """Set the speed of a specific motor (-100 to 100)."""
    global motors_initialized, motor_pwm
    
    # Use thread lock for thread safety
    with motor_lock:
        if not motors_initialized:
            print(f"Motors not initialized. Cannot set motor {motor_num} speed.")
            return False"""
            
        modified_content = modified_content.replace(set_motor_speed_original, set_motor_speed_fixed)
        
        # Fix 4: Add lock to cleanup function
        cleanup_original = """def cleanup_motors(reset_gpio=False):
    """Clean up GPIO resources."""
    global motors_initialized, motor_pwm"""
        
        cleanup_fixed = """def cleanup_motors(reset_gpio=False):
    """Clean up GPIO resources."""
    global motors_initialized, motor_pwm
    
    # Use thread lock for thread safety
    with motor_lock:"""
        
        modified_content = modified_content.replace(cleanup_original, cleanup_fixed)
        
        # Fix 5: Ensure function calls lock properly
        move_forward_original = """def move_forward(speed=100):
    """Move the robot forward at the specified speed."""
    print(f"Moving forward at speed {speed}")
    
    if not motors_initialized and not initialize_motors():
        print("Failed to initialize motors")
        return False"""
        
        move_forward_fixed = """def move_forward(speed=100):
    """Move the robot forward at the specified speed."""
    print(f"Moving forward at speed {speed}")
    
    # Use thread lock for thread safety
    with motor_lock:
        if not motors_initialized and not initialize_motors():
            print("Failed to initialize motors")
            return False"""
            
        modified_content = modified_content.replace(move_forward_original, move_forward_fixed)

        # Also fix move_backward
        move_backward_original = """def move_backward(speed=100):
    """Move the robot backward at the specified speed."""
    print(f"Moving backward at speed {speed}")
    
    if not motors_initialized and not initialize_motors():
        print("Failed to initialize motors for backward movement")
        return False"""

        move_backward_fixed = """def move_backward(speed=100):
    """Move the robot backward at the specified speed."""
    print(f"Moving backward at speed {speed}")
    
    # Use thread lock for thread safety
    with motor_lock:
        if not motors_initialized and not initialize_motors():
            print("Failed to initialize motors for backward movement")
            return False"""
            
        modified_content = modified_content.replace(move_backward_original, move_backward_fixed)
        
        # Fix stop function
        stop_original = """def stop():
    """Stop all motors."""
    print("Stopping all motors")
    
    if not motors_initialized and not initialize_motors():
        return False"""
        
        stop_fixed = """def stop():
    """Stop all motors."""
    print("Stopping all motors")
    
    # Use thread lock for thread safety
    with motor_lock:
        if not motors_initialized and not initialize_motors():
            return False"""
            
        modified_content = modified_content.replace(stop_original, stop_fixed)

        # Fix atexit registration to ensure proper parameters
        atexit_original = "atexit.register(cleanup_motors)"
        atexit_fixed = "atexit.register(lambda: cleanup_motors(reset_gpio=False))"
        
        modified_content = modified_content.replace(atexit_original, atexit_fixed)
        
        # Write the modified content back to the file
        with open(motor_control_path, 'w') as f:
            f.write(modified_content)
            
        print(f"Fixed motor control file: {motor_control_path}")
        return True
        
    except Exception as e:
        print(f"Error fixing motor control: {e}")
        
        # Restore backup if something went wrong
        if backup_path and os.path.exists(backup_path):
            shutil.copy2(backup_path, motor_control_path)
            print(f"Restored original file from backup")
            
        return False

def create_test_script():
    """Create an integrated test script for the fixes."""
    print_section("Creating Integrated Test Script")
    
    test_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_motor_fixes.py')
    
    try:
        with open(test_path, 'w') as f:
            f.write('''#!/usr/bin/env python3
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
''')
            
        print(f"Created integrated test script: {test_path}")
        print("Run with: sudo python3 test_motor_fixes.py")
        return True
        
    except Exception as e:
        print(f"Error creating test script: {e}")
        return False

def create_final_fix_script():
    """Create a final fix script that users can run."""
    print_section("Creating Final Fix Script")
    
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'apply_web_motor_fix.sh')
    
    try:
        with open(script_path, 'w') as f:
            f.write('''#!/bin/bash
# Apply web motor interface fix

# Set text colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Applying Web Motor Interface Fix ===${NC}"

# 1. Check if running as root
if [ $(id -u) -ne 0 ]; then
    echo -e "${RED}Error: This script must be run as root${NC}"
    echo "Please run with sudo: sudo ./apply_web_motor_fix.sh"
    exit 1
fi

# 2. Stop any running services
echo -e "${YELLOW}Stopping any running services...${NC}"
systemctl stop wheelchair 2>/dev/null || true
pkill -f "python.*main.py" 2>/dev/null || true
sleep 1

# 3. Apply the fix by running the Python script
echo -e "${YELLOW}Applying fixes...${NC}"
python3 fix_web_motors.py

# 4. Run the test script
echo -e "${YELLOW}Testing the fix...${NC}"
python3 test_motor_fixes.py

# 5. Complete
echo -e "${GREEN}Fix application complete!${NC}"
echo -e "You can now restart your web interface with:"
echo -e "  ${GREEN}sudo python3 src/main.py${NC}"
echo -e "Or restart the service with:"
echo -e "  ${GREEN}sudo systemctl restart wheelchair${NC}"
''')

        os.chmod(script_path, 0o755)  # Make it executable
        print(f"Created final fix script: {script_path}")
        print("Run with: sudo ./apply_web_motor_fix.sh")
        return True
        
    except Exception as e:
        print(f"Error creating final fix script: {e}")
        return False

def main():
    """Main function."""
    print("=== Web Motor Interface Fix ===")
    print("This script will fix the issue with motors working in test scripts but not in the web interface.")
    
    # Fix the web app
    web_app_fixed = fix_web_app()
    
    # Fix motor control
    motor_control_fixed = fix_motor_control()
    
    # Create test script
    test_created = create_test_script()
    
    # Create final fix script
    script_created = create_final_fix_script()
    
    # Print results
    print("\n=== Fix Summary ===")
    print(f"Web app fixed: {'SUCCESS' if web_app_fixed else 'FAILED'}")
    print(f"Motor control fixed: {'SUCCESS' if motor_control_fixed else 'FAILED'}")
    print(f"Test script created: {'SUCCESS' if test_created else 'FAILED'}")
    print(f"Final fix script created: {'SUCCESS' if script_created else 'FAILED'}")
    
    if web_app_fixed and motor_control_fixed:
        print("\nFix was successfully applied!")
        print("You can now run the test script to verify the fix:")
        print("  sudo python3 test_motor_fixes.py")
        print("\nOr apply the fix automatically with:")
        print("  sudo ./apply_web_motor_fix.sh")
    else:
        print("\nSome errors occurred during fix application.")
        print("Please check the logs for details.")

if __name__ == "__main__":
    main()
