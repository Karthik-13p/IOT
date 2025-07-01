#!/usr/bin/env python3
"""
DroidCam connector - Simplified version without OpenCV dependency.
This uses requests to get images directly from DroidCam's HTTP server.
"""
import os
import time
import subprocess
import requests

# Settings
droidcam_ip = "127.0.0.1"
droidcam_port = "4747"
droidcam_connected = False
last_frame = None
last_frame_time = 0

def is_droidcam_available():
    """Check if DroidCam is available."""
    try:
        # Try to access the DroidCam info page
        url = f"http://{droidcam_ip}:{droidcam_port}/favicon.ico"
        response = requests.head(url, timeout=1)
        return response.status_code == 200
    except:
        return False

def start_adb_forwarding():
    """Start ADB port forwarding to access DroidCam over USB."""
    try:
        # Kill any existing ADB server
        subprocess.run(['adb', 'kill-server'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(1)
        
        # Start ADB server
        subprocess.run(['adb', 'start-server'], stdout=subprocess.PIPE)
        time.sleep(1)
        
        # Check for connected devices
        result = subprocess.run(['adb', 'devices'], stdout=subprocess.PIPE, text=True)
        
        # If no devices are connected, return error
        if "device" not in result.stdout and "emulator" not in result.stdout:
            return False, "No Android device connected via USB"
        
        # Forward port 4747 from the device to localhost
        subprocess.run(['adb', 'forward', 'tcp:4747', 'tcp:4747'], stdout=subprocess.PIPE)
        
        return True, "ADB forwarding started successfully"
    except Exception as e:
        return False, f"Error setting up ADB forwarding: {e}"

def connect_droidcam(ip=None, port=None):
    """Connect to DroidCam with given IP and port."""
    global droidcam_ip, droidcam_port, droidcam_connected
    
    if ip:
        droidcam_ip = ip
    if port:
        droidcam_port = port
    
    # For USB connection, set up ADB forwarding
    if droidcam_ip == "127.0.0.1" or droidcam_ip == "localhost":
        success, message = start_adb_forwarding()
        if not success:
            return False, message
    
    # Check if DroidCam is available
    if is_droidcam_available():
        droidcam_connected = True
        return True, "Connected to DroidCam successfully"
    else:
        droidcam_connected = False
        return False, "Could not connect to DroidCam. Make sure the app is running."

def get_frame():
    """Get the latest frame from DroidCam."""
    global last_frame, last_frame_time
    
    # Check if we need to refresh the frame (no more than once every 100ms)
    current_time = time.time()
    if current_time - last_frame_time < 0.1 and last_frame is not None:
        return last_frame
    
    try:
        # Get image directly from DroidCam's video endpoint
        url = f"http://{droidcam_ip}:{droidcam_port}/video"
        response = requests.get(url, stream=True, timeout=2)
        
        if response.status_code == 200:
            # Store the frame and time
            last_frame = response.content
            last_frame_time = current_time
            return last_frame
    except Exception as e:
        print(f"Error getting frame: {e}")
    
    return None

def get_still_image():
    """Get a still image from DroidCam."""
    try:
        # Try to get image directly from DroidCam's still image endpoint
        url = f"http://{droidcam_ip}:{droidcam_port}/photo.jpg"
        response = requests.get(url, timeout=2)
        
        if response.status_code == 200:
            return response.content
        
        # If that fails, try the regular shot endpoint
        url = f"http://{droidcam_ip}:{droidcam_port}/shot.jpg"
        response = requests.get(url, timeout=2)
        
        if response.status_code == 200:
            return response.content
    except Exception as e:
        print(f"Error getting still image: {e}")
    
    return None

# Initialize with USB connection
connect_droidcam("127.0.0.1", "4747")

# Test code
if __name__ == "__main__":
    print("DroidCam Simple Connector Test")
    print("=============================")
    
    # Connect to DroidCam
    success, message = connect_droidcam()
    print(f"Connection: {message}")
    
    if success:
        # Test getting frames
        for i in range(5):
            print(f"Getting frame {i+1}...")
            frame = get_frame()
            if frame:
                print(f"Frame {i+1}: {len(frame)} bytes")
            else:
                print(f"Frame {i+1}: No data")
            time.sleep(1)
        
        # Test getting still image
        print("Getting still image...")
        image = get_still_image()
        if image:
            print(f"Still image: {len(image)} bytes")
        else:
            print("Still image: No data")
