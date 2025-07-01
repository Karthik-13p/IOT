#!/usr/bin/env python3
"""
IP Webcam connector - Simple module to connect to the IP Webcam Android app.
"""
import requests
import time

# Default settings - you'll update this with your phone's IP
WEBCAM_IP = "192.168.1.100"  # Replace with your phone's IP
WEBCAM_PORT = "8080"         # Default port for IP Webcam
TIMEOUT = 3                  # Connection timeout in seconds

def get_url(endpoint=""):
    """Get full URL for a specific endpoint."""
    return f"http://{WEBCAM_IP}:{WEBCAM_PORT}/{endpoint}"

def is_connected():
    """Check if the IP Webcam is available."""
    try:
        response = requests.head(get_url(), timeout=TIMEOUT)
        return response.status_code == 200
    except:
        return False

def connect(ip=None, port=None):
    """Update connection settings and test connection."""
    global WEBCAM_IP, WEBCAM_PORT
    
    if ip:
        WEBCAM_IP = ip
    if port:
        WEBCAM_PORT = port
    
    print(f"Connecting to IP Webcam at {WEBCAM_IP}:{WEBCAM_PORT}")
    
    if is_connected():
        print("Successfully connected to IP Webcam")
        return True
    else:
        print("Failed to connect to IP Webcam. Make sure the app is running.")
        return False

def get_frame():
    """Get a single video frame from IP Webcam."""
    if not is_connected():
        return None
    
    try:
        # Try the video feed endpoint
        response = requests.get(get_url("shot.jpg"), timeout=TIMEOUT)
        
        if response.status_code == 200:
            return response.content
    except Exception as e:
        print(f"Error getting frame: {e}")
    
    return None

def take_snapshot():
    """Take a high-quality snapshot."""
    if not is_connected():
        return None
    
    try:
        # Use higher quality photo endpoint
        response = requests.get(get_url("photo.jpg"), timeout=TIMEOUT*2)
        
        if response.status_code == 200:
            return response.content
    except Exception as e:
        print(f"Error taking snapshot: {e}")
    
    # Fall back to regular frame
    return get_frame()

def control_flashlight(enabled=True):
    """Control the phone's flashlight."""
    if not is_connected():
        return False
    
    try:
        endpoint = "enabletorch" if enabled else "disabletorch"
        response = requests.get(get_url(endpoint), timeout=TIMEOUT)
        return response.status_code == 200
    except:
        return False

def control_focus():
    """Trigger camera focus."""
    if not is_connected():
        return False
    
    try:
        response = requests.get(get_url("focus"), timeout=TIMEOUT)
        return response.status_code == 200
    except:
        return False

def get_camera_info():
    """Get information about the camera."""
    if not is_connected():
        return None
    
    try:
        response = requests.get(get_url("status.json"), timeout=TIMEOUT)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    
    return None

# Test code
if __name__ == "__main__":
    print("IP Webcam Connector Test")
    print("========================")
    
    # Try to connect
    if connect():
        # Test getting a frame
        print("Getting frame...")
        frame = get_frame()
        
        if frame:
            print(f"Successfully retrieved frame: {len(frame)} bytes")
            
            # Test taking a snapshot
            print("Taking snapshot...")
            snapshot = take_snapshot()
            
            if snapshot:
                print(f"Successfully took snapshot: {len(snapshot)} bytes")
            else:
                print("Failed to take snapshot")
            
            # Test camera info
            print("Getting camera info...")
            info = get_camera_info()
            
            if info:
                print(f"Camera info: {info}")
            else:
                print("Failed to get camera info")
        else:
            print("Failed to get frame")
    else:
        print("Could not connect to IP Webcam")
    
    print("\nTroubleshooting tips:")
    print("1. Make sure IP Webcam app is running and started")
    print("2. Make sure your phone and Raspberry Pi are on the same WiFi network")
    print("3. Check the IP address shown in the app matches what you're using")
    print("4. Ensure no firewall is blocking the connection")
