#!/usr/bin/env python3
import sys
import os
import time

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import the camera control module
try:
    from camera import camera_control
except ImportError as e:
    print(f"Error importing camera_control module: {e}")
    print("Make sure the module exists at src/camera/camera_control.py")
    sys.exit(1)

def test_ip_camera():
    print("=====================================")
    print("IP CAMERA TEST")
    print("Make sure your phone's IP Webcam app is running")
    print("=====================================")
    
    # Initialize camera
    if not camera_control.initialize_camera():
        print("Failed to connect to IP camera. Check your settings.json file.")
        print(f"IP Camera URL: {camera_control.IP_CAMERA_URL}")
        print(f"Snapshot Path: {camera_control.IP_CAMERA_SNAPSHOT_PATH}")
        return
    
    # Take a test picture
    print("\nTaking a test picture...")
    image_path = camera_control.take_picture()
    
    if image_path:
        print(f"Success! Image saved to: {image_path}")
        print(f"File size: {os.path.getsize(image_path) / 1024:.2f} KB")
    else:
        print("Failed to capture image from IP camera")
    
    # Test continuous capture
    print("\nTesting continuous capture (3 images, 2 second interval)...")
    camera_control.start_continuous_capture(interval=2)
    
    # Wait for 3 pictures to be taken
    for i in range(3):
        print(f"Waiting for picture {i+1}/3...")
        time.sleep(2)
        
    # Stop continuous capture
    camera_control.stop_continuous_capture()
    
    # Get latest image
    print("\nGetting latest image...")
    latest_image = camera_control.get_latest_image()
    if latest_image:
        print(f"Latest image: {latest_image}")
        print(f"File size: {os.path.getsize(latest_image) / 1024:.2f} KB")
    else:
        print("No images found")
    
    # Clean up
    camera_control.cleanup_camera()
    
    print("\nIP camera test complete")

if __name__ == "__main__":
    test_ip_camera()
