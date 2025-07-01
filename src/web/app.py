from flask import Flask, render_template, jsonify, Response, request
import threading
import time
import os
import sys
import requests
import json
import logging
import atexit

# Set up logging
logger = logging.getLogger('wheelchair.web')

# Add parent directory to path to import project modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import motor control functions
from motor_control.pi_to_motor import (
    initialize_motors, cleanup_motors, move_forward, 
    move_backward, stop, set_motor_speed
)
from sensors.distance_sensor import read_distance
from sensors import gps_module

# Import camera utils
import camera_utils

# Weight sensor disabled
WEIGHT_SENSOR_AVAILABLE = False

# Enable camera functionality
CAMERA_AVAILABLE = True

app = Flask(__name__)

# Global state variables
motor_state = {
    "running": False,
    "speed": 100,  # Set default speed to 100% for optimal performance
    "direction": "stop"
}

# Initialize motors when app starts
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
    print(f"Error initializing motors in web app: {e}")

# Start GPS when app starts
if os.path.exists('/dev/ttyAMA0') or os.path.exists('/dev/ttyS0'):
    try:
        gps_module.start_gps_monitoring()
    except Exception as e:
        print(f"Error starting GPS monitoring: {e}")

@app.route('/')
def index():
    """Main dashboard page."""
    # Check camera availability
    camera_status = camera_utils.is_camera_available()
    
    return render_template('index.html', 
                          camera_available=camera_status,
                          ip_camera_url=camera_utils.IP_CAMERA_URL)

@app.route('/camera_stream')
def camera_stream():
    """Show IP webcam live stream."""
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'settings.json')
        with open(config_path, 'r') as f:
            settings = json.load(f)
        
        ip_camera_url = settings.get('camera', {}).get('ip_camera_url', 'http://192.168.1.3:8080')
        
        return render_template('camera_stream.html', ip_camera_url=ip_camera_url)
    except Exception as e:
        return f"Error loading camera settings: {e}"

@app.route('/api/camera/check')
def check_camera():
    """Check if camera is available."""
    try:
        available = camera_utils.is_camera_available()
        return jsonify({
            "status": "success",
            "available": available,
            "stream_url": camera_utils.get_video_url() if available else None,
            "mjpeg_url": camera_utils.get_mjpeg_url() if available else None
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/camera/status')
def camera_status():
    """Check if the camera is accessible."""
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'settings.json')
        with open(config_path, 'r') as f:
            settings = json.load(f)
        
        ip_camera_url = settings.get('camera', {}).get('ip_camera_url', 'http://192.168.1.3:8080')
        
        # Check if camera is responding
        import requests
        try:
            response = requests.get(f"{ip_camera_url}/status.json", timeout=2)
            available = response.status_code == 200
        except:
            try:
                # Try snapshot endpoint as fallback
                response = requests.get(f"{ip_camera_url}/shot.jpg", timeout=2)
                available = response.status_code == 200
            except:
                available = False
        
        return jsonify({
            'available': available,
            'url': ip_camera_url
        })
    except Exception as e:
        return jsonify({
            'available': False,
            'error': str(e)
        })

@app.route('/api/motors/control', methods=['POST'])
def control_motors():
    """API endpoint to control motors."""
    try:
        data = request.get_json()
        command = data.get('command')
        speed = int(data.get('speed', motor_state["speed"]))
        
        # Optimize for full speed operation when speed is near maximum
        if speed > 95:
            speed = 100
        
        print(f"Motor control: Command={command}, Speed={speed}")
        
        motor_state["speed"] = speed
        
        if command == 'start':
            # Make sure motors are initialized
            if not hasattr(sys.modules['motor_control.pi_to_motor'], 'motors_initialized') or not sys.modules['motor_control.pi_to_motor'].motors_initialized:
                if not initialize_motors(timeout=5.0):
                    return jsonify({"status": "error", "message": "Failed to initialize motors"})
            
            motor_state["running"] = True
            stop()  # Ensure motors are stopped before changing state
            print("Motors started")
            return jsonify({"status": "success", "message": "Motors started"})
            
        elif command == 'stop':
            motor_state["running"] = False
            motor_state["direction"] = "stop"
            stop()
            print("Motors stopped")
            return jsonify({"status": "success", "message": "Motors stopped"})
            
        elif not motor_state["running"]:
            print("Error: Motors not started")
            return jsonify({"status": "error", "message": "Motors not started"})
            
        elif command == 'forward':
            motor_state["direction"] = "forward"
            result = move_forward(speed)
            print(f"Moving forward at speed {speed}, result: {result}")
            
        elif command == 'backward':
            motor_state["direction"] = "backward"
            result = move_backward(speed)
            print(f"Moving backward at speed {speed}, result: {result}")
            
        elif command == 'left' or command == 'right':
            # Turning functionality disabled - just stop motors
            motor_state["direction"] = "stop"
            result = stop()
            print(f"Turning disabled - stopping motors")
            return jsonify({"status": "info", "message": "Turning functionality disabled", "state": motor_state})
        
        return jsonify({
            "status": "success", 
            "state": motor_state
        })
        
    except Exception as e:
        print(f"Error in motor control: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/motors/status')
def motor_status():
    """API endpoint to get current motor status."""
    return jsonify(motor_state)

@app.route('/api/sensors/distance')
def sensor_distance():
    """API endpoint to get current distance reading."""
    try:
        distance = read_distance()
        return jsonify({
            "distance": distance
        })
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/test')
def test():
    """Test endpoint to verify web server is working."""
    return "Web server is working!"

@app.route('/motor_test')
def motor_test():
    """Test page for direct motor control testing."""
    return render_template('motor_test.html')

# Add a simple joystick control endpoint
@app.route('/api/joystick', methods=['POST'])
def joystick_control():
    """API endpoint for joystick control."""
    try:
        data = request.get_json()
        x = float(data.get('x', 0))  # -1 to 1 (left to right)
        y = float(data.get('y', 0))  # -1 to 1 (back to forward)
        speed = int(data.get('speed', motor_state["speed"]))
        
        motor_state["speed"] = speed
        
        # Make sure motors are initialized
        if not hasattr(sys.modules['motor_control.pi_to_motor'], 'motors_initialized') or not sys.modules['motor_control.pi_to_motor'].motors_initialized:
            if not initialize_motors(timeout=5.0):
                return jsonify({"status": "error", "message": "Failed to initialize motors"})
        
        # No action if motors not running
        if not motor_state["running"]:
            return jsonify({"status": "error", "message": "Motors not started"})
        
        # Only handle forward and backward movements
        # Turning functionality disabled
        
        # Forward/backward component
        if y > 0.1:  # Forward
            # Set all motors to the same forward speed
            result = move_forward(speed)
            motor_state["direction"] = "forward"
            logger.info(f"Joystick: Moving forward at speed {speed}")
            return jsonify({
                "status": "success",
                "state": motor_state,
                "message": "Moving forward"
            })
        elif y < -0.1:  # Backward
            # Set all motors to the same backward speed
            result = move_backward(speed)
            motor_state["direction"] = "backward"
            logger.info(f"Joystick: Moving backward at speed {speed}")
            return jsonify({
                "status": "success",
                "state": motor_state,
                "message": "Moving backward"
            })
        
        # Ignore left/right movements - turning disabled
            
        # Stop if joystick is centered
        if abs(x) < 0.1 and abs(y) < 0.1:
            stop()
            motor_state["direction"] = "stop"
            return jsonify({"status": "success", "message": "Motors stopped", "state": motor_state})
            
        # Calculate motor speeds based on joystick input
        # Ensure full speed operation when needed
        left_speed = int(speed * (y - x))
        right_speed = int(speed * (y + x))
        
        # Clamp values to ensure they stay within valid range
        left_speed = max(-100, min(100, left_speed))
        right_speed = max(-100, min(100, right_speed))
        
        # Set motor speeds
        set_motor_speed(1, left_speed)
        set_motor_speed(2, right_speed)
        
        return jsonify({
            "status": "success",
            "state": motor_state,
            "motors": {
                "left": int(left_speed),
                "right": int(right_speed)
            }
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# Emergency stop endpoint
@app.route('/api/emergency_stop')
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
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/camera/update-url', methods=['POST'])
def update_camera_url():
    """Update the IP camera URL in settings."""
    try:
        data = request.get_json()
        new_url = data.get('url')
        
        if not new_url:
            return jsonify({'success': False, 'message': 'No URL provided'})
        
        # Use the camera_utils function to update the URL
        success, message = camera_utils.update_camera_url(new_url)
        
        # Log the result
        if success:
            logger.info(f"Camera URL updated to: {new_url}")
        else:
            logger.error(f"Failed to update camera URL: {message}")
        
        return jsonify({
            'success': success, 
            'message': message,
            'url': new_url if success else None
        })
    except Exception as e:
        logger.exception("Error updating camera URL")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/gps/data')
def gps_data():
    """Get current GPS data."""
    try:
        data = gps_module.get_gps_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'})

@app.route('/api/gps/formatted')
def gps_formatted():
    """Get formatted GPS data for display."""
    try:
        data = gps_module.format_gps_for_display()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'})

@app.route('/api/gps/save', methods=['POST'])
def save_gps_location():
    """Save current GPS location with optional label."""
    try:
        data = request.get_json() or {}
        label = data.get('label')
        
        success, message = gps_module.save_coordinates_to_file(label)
        
        return jsonify({
            'success': success,
            'message': message
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/api/obstacle_status')
def get_obstacle_status():
    from sensors.obstacle_detection import obstacle_data
    return jsonify(obstacle_data)

# Weight sensor endpoints removed

# Register cleanup function to run when app exits
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
        print(f"Error during web app cleanup: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)