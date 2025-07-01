#!/usr/bin/env python3
"""
Minimal web server to test motor control
"""
from flask import Flask, jsonify, request
import time
import os
import sys

# Add project directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import motor control functions
from motor_control.pi_to_motor import initialize_motors, move_forward, move_backward, stop, set_motor_speed, cleanup_motors

app = Flask(__name__)

# Global state variables
motor_state = {
    "running": False,
    "speed": 70,
    "direction": "stop"
}

# Initialize motors when app starts
try:
    if initialize_motors():
        print("Motors initialized successfully for test web app")
    else:
        print("Failed to initialize motors for test web app")
except Exception as e:
    print(f"Error initializing motors: {e}")

@app.route('/')
def index():
    """Simple test homepage"""
    return """
    <html>
    <head><title>Motor Control Test</title></head>
    <body>
        <h1>L298N Motor Control Test</h1>
        <p>Use the following API endpoints to test motor control:</p>
        <ul>
            <li>POST /api/motors/start - Start motors</li>
            <li>POST /api/motors/stop - Stop motors</li>
            <li>POST /api/motors/forward - Move forward</li>
            <li>POST /api/motors/backward - Move backward</li>
        </ul>
        <p>Current state: <span id="state">Loading...</span></p>
        
        <div style="margin: 20px;">
            <button onclick="controlMotor('start')">Start Motors</button>
            <button onclick="controlMotor('stop')">Stop Motors</button>
            <button onclick="controlMotor('forward')">Forward</button>
            <button onclick="controlMotor('backward')">Backward</button>
        </div>
        
        <script>
        function updateState() {
            fetch('/api/motors/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('state').textContent = 
                        JSON.stringify(data);
                });
        }
        
        function controlMotor(command) {
            fetch('/api/motors/control', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    command: command,
                    speed: 70
                })
            })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                updateState();
            });
        }
        
        // Update state on page load
        updateState();
        // Update state every 2 seconds
        setInterval(updateState, 2000);
        </script>
    </body>
    </html>
    """

@app.route('/api/motors/status')
def motor_status():
    """Get current motor status"""
    return jsonify(motor_state)

@app.route('/api/motors/control', methods=['POST'])
def control_motors():
    """Control the motors"""
    try:
        data = request.get_json()
        command = data.get('command')
        speed = int(data.get('speed', motor_state["speed"]))
        
        print(f"Motor control: Command={command}, Speed={speed}")
        motor_state["speed"] = speed
        
        if command == 'start':
            motor_state["running"] = True
            stop()  # Ensure motors are stopped
            print("Motors started")
            return jsonify({"status": "success", "message": "Motors started"})
            
        elif command == 'stop':
            motor_state["running"] = False
            motor_state["direction"] = "stop"
            stop()
            print("Motors stopped")
            return jsonify({"status": "success", "message": "Motors stopped"})
            
        # Check if motors are started
        if not motor_state["running"]:
            return jsonify({"status": "error", "message": "Motors not started"})
            
        elif command == 'forward':
            motor_state["direction"] = "forward"
            move_forward(speed)
            print(f"Moving forward at speed {speed}")
            
        elif command == 'backward':
            motor_state["direction"] = "backward"
            move_backward(speed)
            print(f"Moving backward at speed {speed}")
        
        return jsonify({
            "status": "success", 
            "state": motor_state
        })
        
    except Exception as e:
        print(f"Error in motor control: {e}")
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5001, debug=True)
    finally:
        print("Cleaning up motors...")
        stop()
        cleanup_motors()
