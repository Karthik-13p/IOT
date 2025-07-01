#!/usr/bin/env python3
"""
DroidCam USB connector - This module handles connecting to DroidCam via USB.
"""
import os
import time
import subprocess
import threading
import cv2
import requests

# Global variables
frame_lock = threading.Lock()
latest_frame = None
capture_running = False
capture_thread = None
droidcam_ip = "127.0.0.1"
droidcam_port = "4747"
droidcam_connected = False

def is_droidcam_available():
    """Check if DroidCam is available."""
    try:
        # Try to access the DroidCam info page
        url = f"http://{droidcam_ip}:{droidcam_port}/favicon.ico"
        response = requests.head(url, timeout=2)
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

def start_capture():
    """Start capturing frames from DroidCam."""
    global capture_running, capture_thread, droidcam_connected
    
    if capture_running:
        return True, "Capture already running"
    
    if not droidcam_connected:
        success, message = connect_droidcam()
        if not success:
            return False, message
    
    # Start the capture thread
    capture_running = True
    capture_thread = threading.Thread(target=_capture_worker)
    capture_thread.daemon = True
    capture_thread.start()
    
    return True, "Capture started successfully"

def _capture_worker():
    """Background worker that captures frames from DroidCam."""
    global latest_frame, capture_running
    
    try:
        # Open video capture from DroidCam
        video_url = f"http://{droidcam_ip}:{droidcam_port}/video"
        cap = cv2.VideoCapture(video_url)
        
        if not cap.isOpened():
            print(f"Failed to open DroidCam video stream: {video_url}")
            capture_running = False
            return
        
        print(f"DroidCam stream opened successfully: {video_url}")
        
        # Capture frames until stopped
        while capture_running:
            ret, frame = cap.read()
            if ret:
                with frame_lock:
                    latest_frame = frame
            else:
                print("Failed to read frame from DroidCam")
                time.sleep(1)  # Wait before retrying
            
            # Small delay to prevent high CPU usage
            time.sleep(0.03)  # ~30 fps
        
        # Release resources
        cap.release()
        
    except Exception as e:
        print(f"Error in DroidCam capture thread: {e}")
    
    capture_running = False

def stop_capture():
    """Stop capturing frames from DroidCam."""
    global capture_running, capture_thread
    
    if not capture_running:
        return True, "Capture not running"
    
    capture_running = False
    if capture_thread:
        capture_thread.join(timeout=1.0)
    
    return True, "Capture stopped successfully"

def get_frame():
    """Get the latest captured frame as JPEG bytes."""
    global latest_frame
    
    with frame_lock:
        if latest_frame is None:
            return None
        
        try:
            # Convert frame to JPEG
            ret, jpeg = cv2.imencode('.jpg', latest_frame)
            if ret:
                return jpeg.tobytes()
        except Exception as e:
            print(f"Error encoding frame: {e}")
    
    return None

def get_still_image():
    """Get a still image from DroidCam."""
    if not droidcam_connected:
        success, message = connect_droidcam()
        if not success:
            return None
    
    try:
        # Try to get image directly from DroidCam's still image endpoint
        url = f"http://{droidcam_ip}:{droidcam_port}/photo.jpg"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            return response.content
        
        # If that fails, try the regular video endpoint
        url = f"http://{droidcam_ip}:{droidcam_port}/shot.jpg"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            return response.content
    except Exception as e:
        print(f"Error getting still image: {e}")
    
    # If direct methods fail, use the captured frame
    return get_frame()

# Initialize with USB connection
connect_droidcam("127.0.0.1", "4747")

# Test code
if __name__ == "__main__":
    print("DroidCam USB Connector Test")
    print("==========================")
    
    # Connect to DroidCam
    success, message = connect_droidcam()
    print(f"Connection: {message}")
    
    if success:
        # Start capture
        success, message = start_capture()
        print(f"Start capture: {message}")
        
        if success:
            # Test for 10 seconds
            for i in range(10):
                time.sleep(1)
                frame = get_frame()
                if frame:
                    print(f"Frame {i+1}: {len(frame)} bytes")
                else:
                    print(f"Frame {i+1}: No data")
            
            # Stop capture
            success, message = stop_capture()
            print(f"Stop capture: {message}")
