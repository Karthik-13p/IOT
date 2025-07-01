#!/usr/bin/env python3
import os
import subprocess
import time
import threading
import cv2

# Global variables
frame_lock = threading.Lock()
latest_frame = None
capture_running = False
capture_thread = None

def start_capture():
    """Start capturing from USB-connected phone camera"""
    global capture_running, capture_thread
    
    if capture_running:
        return True
        
    capture_running = True
    capture_thread = threading.Thread(target=_capture_worker)
    capture_thread.daemon = True
    capture_thread.start()
    
    return True

def _capture_worker():
    """Background worker to capture frames from phone"""
    global latest_frame, capture_running
    
    try:
        # Verify ADB connection
        subprocess.run(['adb', 'devices'], check=True)
        
        # Start camera capture
        cap = cv2.VideoCapture(0)  # USB camera
        
        while capture_running:
            ret, frame = cap.read()
            if ret:
                with frame_lock:
                    latest_frame = frame
            time.sleep(0.03)  # ~30fps
            
        cap.release()
        
    except Exception as e:
        print(f"Error in USB camera capture: {e}")
        capture_running = False

def stop_capture():
    """Stop capturing from phone"""
    global capture_running
    capture_running = False
    if capture_thread:
        capture_thread.join(timeout=1.0)
    return True

def get_frame():
    """Get the latest frame as JPEG bytes"""
    with frame_lock:
        if latest_frame is None:
            return None
            
        # Convert to JPEG
        ret, jpeg = cv2.imencode('.jpg', latest_frame)
        if ret:
            return jpeg.tobytes()
    return None

def is_connected():
    """Check if phone is connected via USB"""
    try:
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
        # Look for a device that's not marked as unauthorized
        lines = result.stdout.strip().split('\n')[1:]
        for line in lines:
            if line and 'unauthorized' not in line and 'offline' not in line:
                return True
        return False
    except:
        return False

if __name__ == "__main__":
    # Test code
    print("USB Camera Test")
    print("==============")
    
    if is_connected():
        print("Phone connected via USB")
        start_capture()
        
        # Capture for 10 seconds
        for i in range(10):
            frame = get_frame()
            if frame:
                print(f"Frame captured: {len(frame)} bytes")
            else:
                print("No frame available")
            time.sleep(1)
            
        stop_capture()
    else:
        print("No phone connected via USB")
