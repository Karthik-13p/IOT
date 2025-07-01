#!/usr/bin/env python3
"""
Obstacle detection module for Smart Wheelchair system.
Monitors distance sensor and triggers actions when obstacles are detected.
"""
import os
import sys
import time
import threading
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Thread control
detection_thread = None
is_running = False
obstacle_lock = threading.Lock()

# Obstacle data
obstacle_data = {
    'detected': False,
    'distance': None,
    'last_detection_time': None,
    'warning_level': 'none',  # none, caution, warning, danger
    'auto_stop_triggered': False
}

# Default settings
OBSTACLE_THRESHOLD_DANGER = 10    # cm - immediate stop
OBSTACLE_THRESHOLD_WARNING = 25   # cm - slow down
OBSTACLE_THRESHOLD_CAUTION = 50   # cm - alert only
CHECK_INTERVAL = 0.1  # seconds between distance checks - increased frequency for better responsiveness

# Status flags
is_emergency_stop = False

# Try to load settings
try:
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                              'config', 'settings.json')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            settings = json.load(f)
            
        # Get obstacle detection settings if available
        obstacle_settings = settings.get('obstacle_detection', {})
        OBSTACLE_THRESHOLD_DANGER = obstacle_settings.get('danger_threshold', OBSTACLE_THRESHOLD_DANGER)
        OBSTACLE_THRESHOLD_WARNING = obstacle_settings.get('warning_threshold', OBSTACLE_THRESHOLD_WARNING)
        OBSTACLE_THRESHOLD_CAUTION = obstacle_settings.get('caution_threshold', OBSTACLE_THRESHOLD_CAUTION)
        CHECK_INTERVAL = obstacle_settings.get('check_interval', CHECK_INTERVAL)
except Exception as e:
    print(f"Error loading obstacle detection settings: {e}")

def start_detection():
    """Start obstacle detection in a separate thread."""
    global detection_thread, is_running
    
    if is_running:
        return True
    
    try:
        from sensors import distance_sensor
        
        # Make sure distance sensor is initialized
        if not hasattr(distance_sensor, 'sensor_initialized') or not distance_sensor.sensor_initialized:
            print("Initializing distance sensor for obstacle detection...")
            distance_sensor.setup_distance_sensor()
        
        # Start monitoring thread
        is_running = True
        detection_thread = threading.Thread(target=_detection_thread)
        detection_thread.daemon = True
        detection_thread.start()
        print("Obstacle detection started")
        return True
    except Exception as e:
        print(f"Error starting obstacle detection: {e}")
        is_running = False
        return False

def _detection_thread():
    """Thread function for obstacle detection."""
    global is_running, obstacle_data
    
    print(f"Starting obstacle detection thread")
    print(f"  Danger threshold: {OBSTACLE_THRESHOLD_DANGER}cm")
    print(f"  Warning threshold: {OBSTACLE_THRESHOLD_WARNING}cm")
    print(f"  Caution threshold: {OBSTACLE_THRESHOLD_CAUTION}cm")
    
    try:
        from sensors import distance_sensor
        from motor_control import pi_to_motor as motor
        
        while is_running:
            try:
                # Get distance reading
                distance = distance_sensor.read_distance()
                
                # Determine warning level
                warning_level = 'none'
                auto_stop = False
                
                if distance <= OBSTACLE_THRESHOLD_DANGER:
                    warning_level = 'danger'
                    auto_stop = True
                elif distance <= OBSTACLE_THRESHOLD_WARNING:
                    warning_level = 'warning'
                elif distance <= OBSTACLE_THRESHOLD_CAUTION:
                    warning_level = 'caution'
                
                # Update obstacle data
                with obstacle_lock:
                    obstacle_data['distance'] = distance
                    obstacle_data['warning_level'] = warning_level
                    
                    # Only trigger detection events when state changes
                    if warning_level != 'none' and not obstacle_data['detected']:
                        obstacle_data['detected'] = True
                        obstacle_data['last_detection_time'] = time.time()
                        print(f"Obstacle detected at {distance:.1f}cm - {warning_level}")
                    elif warning_level == 'none' and obstacle_data['detected']:
                        obstacle_data['detected'] = False
                        print(f"Path clear: {distance:.1f}cm")
                        
                    # Handle auto-stop
                    if auto_stop and not obstacle_data['auto_stop_triggered']:
                        obstacle_data['auto_stop_triggered'] = True
                        print(f"DANGER: Obstacle at {distance:.1f}cm - Auto-stop triggered")
                        motor.stop()
                    elif not auto_stop and obstacle_data['auto_stop_triggered']:
                        obstacle_data['auto_stop_triggered'] = False
                        
                # Sleep between checks
                time.sleep(CHECK_INTERVAL)
                
            except Exception as e:
                print(f"Error in obstacle detection: {e}")
                time.sleep(1)
                
    except Exception as e:
        print(f"Obstacle detection thread error: {e}")
        is_running = False

def stop_detection():
    """Stop obstacle detection."""
    global is_running
    
    is_running = False
    
    if detection_thread is not None:
        detection_thread.join(timeout=2.0)
    
    print("Obstacle detection stopped")
    return True

def get_obstacle_data():
    """Get the current obstacle data."""
    with obstacle_lock:
        return obstacle_data.copy()

def is_path_clear():
    """Check if the path is clear (no obstacles detected)."""
    with obstacle_lock:
        return not obstacle_data['detected']

def handle_obstacle(distance):
    global is_emergency_stop
    from motor_control.pi_to_motor import stop, set_motor_speed
    
    with obstacle_lock:
        obstacle_data['distance'] = distance
        obstacle_data['last_detection_time'] = time.time()
        
        # Emergency stop at 10cm
        if distance <= OBSTACLE_THRESHOLD_DANGER:
            obstacle_data['warning_level'] = 'danger'
            obstacle_data['detected'] = True
            obstacle_data['auto_stop_triggered'] = True
            is_emergency_stop = True
            stop()  # Emergency stop all motors
            
        # Warning zone - slow down
        elif distance <= OBSTACLE_THRESHOLD_WARNING:
            obstacle_data['warning_level'] = 'warning'
            obstacle_data['detected'] = True
            if not is_emergency_stop:
                set_motor_speed(30)  # Reduce speed to 30%
                
        # Caution zone - alert only
        elif distance <= OBSTACLE_THRESHOLD_CAUTION:
            obstacle_data['warning_level'] = 'caution'
            obstacle_data['detected'] = True
            if not is_emergency_stop:
                set_motor_speed(50)  # Reduce speed to 50%
                
        else:
            obstacle_data['warning_level'] = 'none'
            obstacle_data['detected'] = False
            obstacle_data['auto_stop_triggered'] = False
            is_emergency_stop = False

def test_obstacle_detection():
    """Run a test of the obstacle detection system."""
    print("Obstacle Detection Test")
    print("======================")
    
    # Start detection
    print("Starting obstacle detection...")
    if not start_detection():
        print("Failed to start obstacle detection!")
        return
    
    try:
        for i in range(20):  # Test for 10 seconds
            data = get_obstacle_data()
            distance = data['distance']
            warning = data['warning_level']
            
            print(f"Distance: {distance:.1f}cm  Status: {warning}")
            
            if data['auto_stop_triggered']:
                print("AUTO-STOP ACTIVE! - Motors would be stopped")
                
            time.sleep(0.5)
    
    except KeyboardInterrupt:
        print("Test interrupted")
    
    finally:
        stop_detection()
        print("Test complete")

if __name__ == "__main__":
    test_obstacle_detection()