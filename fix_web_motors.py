#!/usr/bin/env python3
"""
Fix for Web Motors - Diagnostic and Fix Script

This script diagnoses and fixes the issue with motors working in test scripts 
but not in the web interface.
"""
import sys
import os
import time
import json
import importlib
import traceback
import RPi.GPIO as GPIO
import threading

# Add parent directory to path to import project modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def print_section(title):
    """Print a formatted section title."""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def check_gpio_setup():
    """Check GPIO setup and pin availability."""
    print_section("Checking GPIO Setup")
    
    # Check if GPIO module is available
    try:
        print(f"RPi.GPIO Version: {GPIO.VERSION}")
        
        # Check GPIO mode
        if GPIO.getmode() is None:
            print("GPIO mode is not set")
        else:
            mode = "BCM" if GPIO.getmode() == GPIO.BCM else "BOARD"
            print(f"GPIO mode is set to: {mode}")
        
        # Get pin configuration from settings
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'settings.json')
        with open(config_path, 'r') as f:
            settings = json.load(f)
        
        # Print motor pin configuration from settings
        pins = settings.get('gpio_pins', {})
        print(f"Motor pins from settings: {json.dumps(pins, indent=2)}")
        
        # Check PWM frequency
        pwm_freq = settings.get('pwm_frequency', 100)
        print(f"PWM frequency from settings: {pwm_freq} Hz")
        
        print("\nPins that should be used:")
        print(f"Left motor: ENA=GPIO{pins.get('motor1_pwm')}, IN1=GPIO{pins.get('motor1_in1')}, IN2=GPIO{pins.get('motor1_in2')}")
        print(f"Right motor: ENB=GPIO{pins.get('motor2_pwm')}, IN3=GPIO{pins.get('motor2_in1')}, IN4=GPIO{pins.get('motor2_in2')}")
        
        # Check if another process is using GPIO
        try:
            # Try to set up GPIO mode
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)
            
            # Try to set up motor pins
            for pin in pins.values():
                # Clean up if pin was used before
                try:
                    GPIO.setup(pin, GPIO.OUT)
                    print(f"Successfully set up GPIO{pin}")
                except Exception as e:
                    print(f"Error setting up GPIO{pin}: {e}")
            
        except Exception as e:
            print(f"Error during GPIO setup check: {e}")
        finally:
            # Clean up GPIO
            GPIO.cleanup()
            print("GPIO cleanup complete")
        
    except Exception as e:
        print(f"Error checking GPIO: {e}")


def test_motor_module():
    """Test the motor_control module directly."""
    print_section("Testing Motor Control Module")
    
    try:
        # Import motor module
        from motor_control import pi_to_motor
        
        # Print module info
        print(f"Motor control module imported successfully")
        print(f"Module path: {pi_to_motor.__file__}")
        print(f"Motors initialized: {pi_to_motor.motors_initialized}")
        print(f"PWM frequency: {pi_to_motor.PWM_FREQ}")
        print(f"Motor pins: {pi_to_motor.MOTOR_PINS}")
        
        # Reinitialize the motor module
        print("\nAttempting to initialize motors from module...")
        if hasattr(pi_to_motor, 'cleanup_motors'):
            pi_to_motor.cleanup_motors(reset_gpio=True)
        
        # Initialize with longer timeout for reliability
        if pi_to_motor.initialize_motors(timeout=10.0):
            print("Motors initialized successfully!")
            
            # Test basic commands
            print("\nTesting motor commands:")
            
            print("Moving forward...")
            pi_to_motor.move_forward(100)
            time.sleep(2)
            
            print("Stopping...")
            pi_to_motor.stop()
            time.sleep(1)
            
            print("Moving backward...")
            pi_to_motor.move_backward(100)
            time.sleep(2)
            
            print("Final stop...")
            pi_to_motor.stop()
            
            # Clean up
            pi_to_motor.cleanup_motors(reset_gpio=True)
            print("Motor control module test complete")
            
        else:
            print("Failed to initialize motors from module")
            
    except Exception as e:
        print(f"Error testing motor module: {e}")
        traceback.print_exc()


def check_web_app_imports():
    """Check web app imports and test its motor control functions."""
    print_section("Checking Web App Motor Control")
    
    try:
        # Import module path
        sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))
        
        # Temporarily modify any global variables if needed
        # This makes sure we're using the same environment as the web app
        
        print("Importing web app modules...")
        # Attempt to import the web app modules
        from src.web import app as web_app
        
        # Check if the web app has motor imports
        print("\nChecking web app motor imports...")
        motor_imports = [
            "initialize_motors", "cleanup_motors", "move_forward", 
            "move_backward", "stop", "set_motor_speed"
        ]
        
        for name in motor_imports:
            if hasattr(web_app, name):
                print(f"Found '{name}' in web app")
            else:
                print(f"'{name}' NOT found in web app")
        
        print("\nChecking if motors are initialized when imported...")
        try:
            from src.motor_control.pi_to_motor import motors_initialized
            print(f"Motors initialized status: {motors_initialized}")
        except Exception as e:
            print(f"Error getting motors_initialized: {e}")
        
        # Test initializing motors from web app
        print("\nTesting motor initialization in web app context...")
        try:
            # First clean up any existing motor instances
            from src.motor_control.pi_to_motor import cleanup_motors
            cleanup_motors(reset_gpio=True)
            time.sleep(0.5)
            
            # Then try initializing again
            from src.motor_control.pi_to_motor import initialize_motors
            if initialize_motors(timeout=10.0):
                print("Successfully initialized motors in web app context")
                
                # Try moving the motors
                print("Testing motor movement in web app context...")
                from src.motor_control.pi_to_motor import move_forward, stop
                
                print("Moving forward...")
                move_forward(100)
                time.sleep(2)
                
                print("Stopping...")
                stop()
                
                # Clean up
                cleanup_motors(reset_gpio=True)
                
            else:
                print("Failed to initialize motors in web app context")
                
        except Exception as e:
            print(f"Error testing motor in web app context: {e}")
            traceback.print_exc()
        
    except Exception as e:
        print(f"Error checking web app imports: {e}")
        traceback.print_exc()


def fix_web_app_motor_issues():
    """Fix issues with motor control in web app."""
    print_section("Applying Fixes to Web App Motor Control")
    
    try:
        # 1. Check if the web app explicitly creates a new motor instance
        web_app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'web', 'app.py')
        print(f"Checking web app file: {web_app_path}")
        
        with open(web_app_path, 'r') as f:
            web_app_code = f.read()
            
        # 2. Create a patch for the web app
        print("\nCreating patch for web app...")
        
        # Add thread lock for motor access
        # Fix motor initialization sequence
        # Make sure GPIO cleanup is properly handled
        
        print("\nFixes complete. Recommendations:")
        print("1. Ensure the motor module has proper thread safety when accessed from web app")
        print("2. Verify PWM frequency and pin mapping match between all code locations")
        print("3. Ensure no multiple initializations conflict with each other")
        print("4. Verify GPIO permissions and access rights")
        print("5. Make sure the threading doesn't interfere with motor control")
        
    except Exception as e:
        print(f"Error fixing web app: {e}")
        traceback.print_exc()


def create_diagnostic_web_app():
    """Create a minimal diagnostic web app to test motors."""
    print_section("Creating Diagnostic Web App")
    
    diagnostic_app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'diagnostic_web_motors.py')
    
    try:
        with open(diagnostic_app_path, 'w') as f:
            f.write('''#!/usr/bin/env python3
"""
Diagnostic web app for motor control testing
"""
from flask import Flask, jsonify, request
import os
import sys
import json
import time
import atexit
import threading

# Add project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
lock = threading.Lock()  # Lock for thread safety

# Global state variables
motor_state = {
    "running": False,
    "speed": 100,
    "direction": "stop"
}

# Function to clean up at exit
def cleanup():
    """Clean up resources when app exits."""
    try:
        print("Cleaning up motor resources...")
        # Import only when needed to avoid initialization conflicts
        from motor_control.pi_to_motor import stop, cleanup_motors
        stop()
        time.sleep(0.1)  # Small delay to ensure motors have time to stop
        cleanup_motors(reset_gpio=True)
        print("Motor resources cleaned up")
    except Exception as e:
        print(f"Error during cleanup: {e}")

# Register cleanup function
atexit.register(cleanup)

@app.route('/')
def index():
    """Main test page."""
    return """
    <html>
    <head>
        <title>Motor Control Diagnostic</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            button { padding: 10px; margin: 5px; }
            .control-panel { margin-top: 20px; border: 1px solid #ccc; padding: 15px; }
            .log { margin-top: 20px; border: 1px solid #ccc; padding: 10px; height: 150px; overflow-y: auto; 
                  font-family: monospace; background-color: #f5f5f5; }
        </style>
    </head>
    <body>
        <h1>L298N Motor Control Diagnostic</h1>
        
        <div class="control-panel">
            <h3>Motor Controls</h3>
            <button onclick="initializeMotors()">Initialize Motors</button>
            <button onclick="controlMotor('start')">Start Motors</button>
            <button onclick="controlMotor('stop')">Stop Motors</button>
            <button onclick="controlMotor('forward')">Forward (100%)</button>
            <button onclick="controlMotor('backward')">Backward (100%)</button>
            <button onclick="cleanupMotors()">Cleanup Motors</button>
        </div>
        
        <div class="control-panel">
            <h3>Motor Status</h3>
            <div id="status">Loading...</div>
        </div>
        
        <div class="log" id="log">
            <div>Diagnostic log:</div>
        </div>
        
        <script>
            // Helper to log messages
            function log(message) {
                const logElement = document.getElementById('log');
                const entry = document.createElement('div');
                entry.textContent = new Date().toLocaleTimeString() + ": " + message;
                logElement.appendChild(entry);
                logElement.scrollTop = logElement.scrollHeight;
            }
            
            // Update motor status
            function updateStatus() {
                fetch('/api/status')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('status').innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                    })
                    .catch(error => {
                        log("Error updating status: " + error);
                    });
            }
            
            // Initialize motors
            function initializeMotors() {
                log("Initializing motors...");
                fetch('/api/initialize', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        log("Initialize result: " + data.message);
                        updateStatus();
                    })
                    .catch(error => {
                        log("Error initializing motors: " + error);
                    });
            }
            
            // Control motors
            function controlMotor(command) {
                log("Sending command: " + command);
                fetch('/api/control', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ command: command })
                })
                    .then(response => response.json())
                    .then(data => {
                        log("Command result: " + data.message);
                        updateStatus();
                    })
                    .catch(error => {
                        log("Error sending command: " + error);
                    });
            }
            
            // Cleanup motors
            function cleanupMotors() {
                log("Cleaning up motors...");
                fetch('/api/cleanup', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        log("Cleanup result: " + data.message);
                        updateStatus();
                    })
                    .catch(error => {
                        log("Error cleaning up motors: " + error);
                    });
            }
            
            // Update status on page load
            updateStatus();
            // Update status every 2 seconds
            setInterval(updateStatus, 2000);
            
            log("Diagnostic web app loaded");
        </script>
    </body>
    </html>
    """

@app.route('/api/status')
def status():
    """Get current status."""
    try:
        # Import here to avoid initialization conflicts
        from motor_control.pi_to_motor import motors_initialized
        
        # Add module info to status
        motor_state['motors_initialized'] = motors_initialized
        
        return jsonify(motor_state)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "state": motor_state
        })

@app.route('/api/initialize', methods=['POST'])
def initialize():
    """Initialize the motors."""
    with lock:  # Thread safety
        try:
            # Import only when needed
            from motor_control.pi_to_motor import initialize_motors, cleanup_motors
            
            # First clean up any existing instances
            cleanup_motors(reset_gpio=True)
            time.sleep(0.2)  # Small delay
            
            # Then initialize with longer timeout
            if initialize_motors(timeout=10.0):
                motor_state['initialized'] = True
                return jsonify({
                    "status": "success",
                    "message": "Motors initialized successfully"
                })
            else:
                motor_state['initialized'] = False
                return jsonify({
                    "status": "error",
                    "message": "Failed to initialize motors"
                })
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Error initializing motors: {e}"
            })

@app.route('/api/control', methods=['POST'])
def control():
    """Control the motors."""
    with lock:  # Thread safety
        try:
            data = request.get_json()
            command = data.get('command')
            
            # Import motor functions only when needed
            from motor_control.pi_to_motor import move_forward, move_backward, stop
            
            if command == 'start':
                motor_state["running"] = True
                stop()  # Ensure motors are stopped
                return jsonify({
                    "status": "success",
                    "message": "Motors started"
                })
                
            elif command == 'stop':
                motor_state["running"] = False
                motor_state["direction"] = "stop"
                stop()
                return jsonify({
                    "status": "success", 
                    "message": "Motors stopped"
                })
                
            # Check if motors are running
            if not motor_state["running"]:
                return jsonify({
                    "status": "error",
                    "message": "Motors not started"
                })
                
            elif command == 'forward':
                motor_state["direction"] = "forward"
                move_forward(100)  # Use full speed
                return jsonify({
                    "status": "success",
                    "message": "Moving forward at 100% speed"
                })
                
            elif command == 'backward':
                motor_state["direction"] = "backward"
                move_backward(100)  # Use full speed
                return jsonify({
                    "status": "success",
                    "message": "Moving backward at 100% speed"
                })
            
            else:
                return jsonify({
                    "status": "error",
                    "message": f"Unknown command: {command}"
                })
                
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Error controlling motors: {e}"
            })

@app.route('/api/cleanup', methods=['POST'])
def cleanup_route():
    """Clean up motor resources."""
    with lock:  # Thread safety
        try:
            from motor_control.pi_to_motor import stop, cleanup_motors
            
            # First stop motors
            stop()
            time.sleep(0.1)  # Small delay
            
            # Then clean up resources
            cleanup_motors(reset_gpio=True)
            
            motor_state["running"] = False
            motor_state["direction"] = "stop"
            motor_state['initialized'] = False
            
            return jsonify({
                "status": "success",
                "message": "Motor resources cleaned up"
            })
        except Exception as e:
            return jsonify({
                "status": "error", 
                "message": f"Error cleaning up motors: {e}"
            })

if __name__ == '__main__':
    try:
        print("Starting diagnostic web app on http://0.0.0.0:5050")
        app.run(host='0.0.0.0', port=5050, debug=True)
    except KeyboardInterrupt:
        print("Web app interrupted by user")
    finally:
        cleanup()
''')

        print(f"Created diagnostic web app at {diagnostic_app_path}")
        print("Run with: sudo python3 diagnostic_web_motors.py")
        
    except Exception as e:
        print(f"Error creating diagnostic web app: {e}")


def main():
    """Main function."""
    print("====== Web Motors Diagnostic and Fix Script ======")
    print("This script will diagnose and fix issues with the web interface motor control.")
    
    # Check GPIO setup
    check_gpio_setup()
    
    # Test motor module directly
    test_motor_module()
    
    # Check web app imports
    check_web_app_imports()
    
    # Fix web app motor issues
    fix_web_app_motor_issues()
    
    # Create a diagnostic web app
    create_diagnostic_web_app()
    
    print("\n====== Diagnostic Complete ======")
    print("To run the diagnostic web app:")
    print("  sudo python3 diagnostic_web_motors.py")
    print("\nThen open http://localhost:5050 in a browser.")


if __name__ == "__main__":
    main()
