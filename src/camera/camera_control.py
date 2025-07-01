#!/usr/bin/env python3
import os
import time
import requests
import json
import threading
from datetime import datetime

# Load configuration
config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'settings.json')
try:
    with open(config_path, 'r') as f:
        settings = json.load(f)
    
    # Camera settings
    CAMERA_CONFIG = settings.get('camera', {})
    IP_CAMERA_URL = CAMERA_CONFIG.get('ip_camera_url', 'http://192.168.1.3:8080')
    IP_CAMERA_SNAPSHOT_PATH = CAMERA_CONFIG.get('snapshot_path', '/shot.jpg')
except Exception as e:
    print(f"Warning: Could not load settings from {config_path}: {e}")
    # Default settings
    IP_CAMERA_URL = 'http://192.168.1.3:8080'
    IP_CAMERA_SNAPSHOT_PATH = '/shot.jpg'

# Image directory
IMAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'images')
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

# Global variables
camera_initialized = False
camera_lock = threading.Lock()
continuous_capture_thread = None
continuous_capture_running = False

def initialize_camera():
    """Initialize connection to the IP camera."""
    global camera_initialized
    
    with camera_lock:
        try:
            # Test connection to IP camera
            snapshot_url = f"{IP_CAMERA_URL}{IP_CAMERA_SNAPSHOT_PATH}"
            print(f"Testing connection to IP camera at: {snapshot_url}")
            
            # Try to get a test image
            response = requests.get(snapshot_url, timeout=5)
            
            if response.status_code == 200:
                # Just check if we got image data
                if len(response.content) > 1000:  # Basic check that we got some data
                    camera_initialized = True
                    print("IP camera connection successful")
                    return True
                else:
                    raise Exception("Received invalid or too small image data from IP camera")
            else:
                raise Exception(f"HTTP error {response.status_code}")
                
        except Exception as e:
            print(f"Error initializing IP camera: {e}")
            print("\nTroubleshooting tips:")
            print("1. Make sure your phone is on the same WiFi network as the Raspberry Pi")
            print(f"2. Verify the IP camera URL: {IP_CAMERA_URL}")
            print("3. Check if you can access the camera from a browser")
            print(f"4. Full snapshot URL being used: {IP_CAMERA_URL}{IP_CAMERA_SNAPSHOT_PATH}")
            camera_initialized = False
            return False

def take_picture(filename=None):
    """Take a picture from the IP camera."""
    global camera_initialized
    
    with camera_lock:
        if not camera_initialized:
            if not initialize_camera():
                return None
        
        try:
            # Generate filename if not provided
            if filename is None:
                filename = os.path.join(IMAGE_DIR, f'image_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg')
            
            # Get image from IP camera
            snapshot_url = f"{IP_CAMERA_URL}{IP_CAMERA_SNAPSHOT_PATH}"
            response = requests.get(snapshot_url, timeout=5)
            
            if response.status_code == 200:
                # Save the raw image data directly to a file
                with open(filename, 'wb') as f:
                    f.write(response.content)
                    
                print(f"Picture saved to: {filename}")
                return filename
            else:
                raise Exception(f"HTTP error {response.status_code}")
                
        except Exception as e:
            print(f"Error taking picture: {e}")
            camera_initialized = False  # Reset for next attempt
            return None

def start_continuous_capture(interval=5):
    """Start continuous image capture."""
    global continuous_capture_thread, continuous_capture_running
    
    if continuous_capture_running:
        print("Continuous capture already running")
        return False
    
    # Define capture loop
    def capture_loop():
        while continuous_capture_running:
            take_picture()
            time.sleep(interval)
    
    try:
        continuous_capture_running = True
        continuous_capture_thread = threading.Thread(target=capture_loop)
        continuous_capture_thread.daemon = True
        continuous_capture_thread.start()
        print(f"Continuous capture started with {interval} second interval")
        return True
        
    except Exception as e:
        print(f"Error starting continuous capture: {e}")
        continuous_capture_running = False
        return False

def stop_continuous_capture():
    """Stop continuous image capture."""
    global continuous_capture_running
    
    if not continuous_capture_running:
        print("Continuous capture not running")
        return False
    
    try:
        continuous_capture_running = False
        print("Continuous capture stopped")
        return True
        
    except Exception as e:
        print(f"Error stopping continuous capture: {e}")
        return False

def cleanup_camera():
    """Clean up camera resources."""
    global camera_initialized, continuous_capture_running
    
    with camera_lock:
        try:
            # Stop continuous capture if running
            if continuous_capture_running:
                stop_continuous_capture()
            
            camera_initialized = False
            print("Camera resources released")
            return True
            
        except Exception as e:
            print(f"Error cleaning up camera: {e}")
            return False

def get_latest_image():
    """Get the path to the most recent image."""
    try:
        if not os.path.exists(IMAGE_DIR):
            return None
            
        image_files = [os.path.join(IMAGE_DIR, f) for f in os.listdir(IMAGE_DIR) 
                      if f.endswith(('.jpg', '.jpeg', '.png'))]
        
        if not image_files:
            return None
            
        # Get the most recent file
        latest_image = max(image_files, key=os.path.getmtime)
        return latest_image
        
    except Exception as e:
        print(f"Error getting latest image: {e}")
        return None

# When run directly, test the module
if __name__ == "__main__":
    print("Testing IP camera module...")
    
    try:
        if initialize_camera():
            print("Taking test picture...")
            image_path = take_picture()
            
            if image_path:
                print(f"Test image captured: {image_path}")
                print(f"File size: {os.path.getsize(image_path) / 1024:.2f} KB")
        
        cleanup_camera()
        print("Camera test completed")
        
    except KeyboardInterrupt:
        print("\nTest interrupted")
        cleanup_camera()
        
    except Exception as e:
        print(f"Test error: {e}")
        cleanup_camera()
