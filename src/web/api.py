#!/usr/bin/env python3
"""API routes for the Smart Wheelchair system."""
import os
import sys
import time
import json
from flask import jsonify, request, Response, Blueprint
from datetime import datetime

# Create a Blueprint for the API
api_bp = Blueprint('api', __name__)

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import camera utilities
import camera_utils

# ----------------- Camera API -----------------

@api_bp.route('/camera/stream', methods=['GET'])
def camera_stream():
    """Stream from IP camera - gets a frame of video."""
    try:
        # Load camera settings
        settings = camera_utils.load_settings()
        camera_settings = settings.get("camera", {})
        ip = camera_settings.get("ip", "192.168.1.100")
        port = camera_settings.get("port", "8080")
        camera_type = camera_settings.get("type", "ip_webcam")
        
        # Get snapshot
        image_data = camera_utils.get_camera_snapshot(ip, port, camera_type)
        
        if image_data:
            return Response(image_data, mimetype='image/jpeg')
        else:
            return Response("Camera not available", mimetype='text/plain')
    except Exception as e:
        return Response(f"Error: {str(e)}", mimetype='text/plain')

@api_bp.route('/camera/status', methods=['GET'])
def camera_status():
    """Get camera status."""
    try:
        # Load camera settings
        settings = camera_utils.load_settings()
        camera_settings = settings.get("camera", {})
        ip = camera_settings.get("ip", "192.168.1.100")
        port = camera_settings.get("port", "8080")
        camera_type = camera_settings.get("type", "ip_webcam")
        
        # Check if camera is available
        available = camera_utils.is_camera_available(ip, port, camera_type)
        
        return jsonify({
            'available': available,
            'url': f"http://{ip}:{port}",
            'type': camera_type,
            'settings': camera_settings
        })
    except Exception as e:
        return jsonify({'error': str(e), 'available': False})

@api_bp.route('/camera/connect', methods=['POST'])
def connect_camera():
    """Connect to camera with given IP and port."""
    try:
        data = request.get_json() or {}
        ip = data.get('ip')
        port = data.get('port')
        camera_type = data.get('type')
        
        if not ip:
            return jsonify({'success': False, 'message': 'IP address is required'})
        
        # Default port based on camera type
        if not port:
            if camera_type == 'droidcam':
                port = '4747'
            else:
                port = '8080'
        
        # Test connection
        if camera_utils.is_camera_available(ip, port, camera_type):
            # Update settings
            camera_utils.update_camera_settings(ip, port, camera_type)
            return jsonify({
                'success': True,
                'message': 'Connected to camera successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Could not connect to camera'
            })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@api_bp.route('/camera/snapshot', methods=['GET'])
def take_snapshot():
    """Take a snapshot from the camera."""
    try:
        # Load camera settings
        settings = camera_utils.load_settings()
        camera_settings = settings.get("camera", {})
        ip = camera_settings.get("ip", "192.168.1.100")
        port = camera_settings.get("port", "8080")
        camera_type = camera_settings.get("type", "ip_webcam")
        
        # Get snapshot
        image_data = camera_utils.get_camera_snapshot(ip, port, camera_type)
        
        if image_data:
            # Save snapshot
            filepath = camera_utils.save_snapshot(image_data)
            
            if filepath:
                return jsonify({
                    'success': True,
                    'path': filepath,
                    'filename': os.path.basename(filepath),
                    'size': len(image_data)
                })
        
        return jsonify({
            'success': False,
            'error': 'Failed to capture snapshot'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@api_bp.route('/camera/discover', methods=['GET'])
def discover_cameras():
    """Discover cameras on the network."""
    try:
        # Get timeout parameter
        timeout = request.args.get('timeout', default=1, type=float)
        
        # Discover cameras
        cameras = camera_utils.discover_cameras(timeout)
        
        return jsonify({
            'success': True,
            'cameras': cameras,
            'count': len(cameras)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@api_bp.route('/camera/flash', methods=['POST'])
def toggle_flash():
    """Toggle camera flash/torch."""
    try:
        # Load camera settings
        settings = camera_utils.load_settings()
        camera_settings = settings.get("camera", {})
        ip = camera_settings.get("ip", "192.168.1.100")
        port = camera_settings.get("port", "8080")
        camera_type = camera_settings.get("type", "ip_webcam")
        
        # Get flash state
        data = request.get_json() or {}
        enabled = data.get('enabled', True)
        
        # Toggle flash
        success = camera_utils.toggle_camera_flash(ip, port, enabled, camera_type)
        
        # Update settings
        if success:
            settings["camera"]["use_flash"] = enabled
            camera_utils.save_settings(settings)
        
        return jsonify({
            'success': success,
            'flash': 'on' if enabled else 'off'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@api_bp.route('/camera/focus', methods=['POST'])
def trigger_focus():
    """Trigger camera focus."""
    try:
        # Load camera settings
        settings = camera_utils.load_settings()
        camera_settings = settings.get("camera", {})
        ip = camera_settings.get("ip", "192.168.1.100")
        port = camera_settings.get("port", "8080")
        camera_type = camera_settings.get("type", "ip_webcam")
        
        # Focus camera
        success = camera_utils.focus_camera(ip, port, camera_type)
        
        return jsonify({
            'success': success
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@api_bp.route('/camera/settings', methods=['GET', 'PUT'])
def camera_settings():
    """Get or update camera settings."""
    try:
        if request.method == 'GET':
            # Get settings
            settings = camera_utils.load_settings()
            return jsonify({
                'success': True,
                'settings': settings.get('camera', {})
            })
        else:  # PUT
            # Update settings
            data = request.get_json() or {}
            settings = camera_utils.load_settings()
            
            # Update only provided settings
            for key, value in data.items():
                settings['camera'][key] = value
            
            # Save settings
            success = camera_utils.save_settings(settings)
            
            return jsonify({
                'success': success,
                'settings': settings.get('camera', {})
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ----------------- Motor Control API -----------------

@api_bp.route('/motors/forward', methods=['POST'])
def move_forward():
    """Move the wheelchair forward."""
    try:
        from motor_control import pi_to_motor as motor
        data = request.get_json() or {}
        speed = data.get('speed', 50)
        motor.forward(speed)
        return jsonify({'success': True, 'direction': 'forward', 'speed': speed})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/motors/backward', methods=['POST'])
def move_backward():
    """Move the wheelchair backward."""
    try:
        from motor_control import pi_to_motor as motor
        data = request.get_json() or {}
        speed = data.get('speed', 50)
        motor.backward(speed)
        return jsonify({'success': True, 'direction': 'backward', 'speed': speed})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/motors/left', methods=['POST'])
def turn_left():
    """Turn the wheelchair left."""
    try:
        from motor_control import pi_to_motor as motor
        data = request.get_json() or {}
        speed = data.get('speed', 50)
        motor.left(speed)
        return jsonify({'success': True, 'direction': 'left', 'speed': speed})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/motors/right', methods=['POST'])
def turn_right():
    """Turn the wheelchair right."""
    try:
        from motor_control import pi_to_motor as motor
        data = request.get_json() or {}
        speed = data.get('speed', 50)
        motor.right(speed)
        return jsonify({'success': True, 'direction': 'right', 'speed': speed})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/motors/stop', methods=['POST'])
def stop_motors():
    """Stop all motors."""
    try:
        from motor_control import pi_to_motor as motor
        motor.stop()
        return jsonify({'success': True, 'status': 'stopped'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500