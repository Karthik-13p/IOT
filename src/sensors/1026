#!/usr/bin/env python3
"""GPS module for Smart Wheelchair system"""
import os
import time
import threading
import json
import glob
from datetime import datetime

# Thread control variables
gps_thread = None
is_running = False
gps_lock = threading.Lock()

# Global state
gps_data = {
    'latitude': None,
    'longitude': None,
    'altitude': None,
    'speed': None,
    'course': None,
    'satellites': None,
    'timestamp': None,
    'fix_quality': None,
    'last_update': None,
    'status': 'disconnected'
}

# GPS Configuration class to avoid global variable issues
class GPSConfig:
    """GPS configuration container"""
    def __init__(self):
        # Default settings
        self.port = '/dev/ttyS0'
        self.baud_rate = 9600
        self.timeout = 1
        self.update_interval = 5
        
        # Try to load settings from config
        self.load_from_config()
    
    def load_from_config(self):
        """Load settings from config file"""
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                     'config', 'settings.json')
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    settings = json.load(f)
                
                # Get GPS settings
                gps_settings = settings.get('gps', {})
                self.port = gps_settings.get('port', self.port)
                self.baud_rate = gps_settings.get('baud_rate', self.baud_rate)
                self.timeout = gps_settings.get('timeout', self.timeout)
                self.update_interval = gps_settings.get('update_interval', self.update_interval)
            else:
                print(f"Config file not found at {config_path}, using default settings")
        except Exception as e:
            print(f"Error loading GPS settings: {e}")
            # Continue with defaults

# Create global config object
config = GPSConfig()

def find_gps_port():
    """Find available GPS port"""
    # Common GPS ports to check
    potential_ports = [
        '/dev/ttyS0',     # Common for Raspberry Pi 3 and 4
        '/dev/ttyAMA0',   # Common for older Pis
        '/dev/ttyUSB0',   # Common for USB GPS modules
        '/dev/ttyACM0'    # Some USB GPS modules use this
    ]
    
    # Add any additional ttyUSB devices
    usb_ports = glob.glob('/dev/ttyUSB*')
    for port in usb_ports:
        if port not in potential_ports:
            potential_ports.append(port)
    
    # Check which ports exist
    for port in potential_ports:
        if os.path.exists(port):
            print(f"Found port: {port}")
            return port
    
    return None

def start_gps_monitoring():
    """Start GPS monitoring in a separate thread."""
    global gps_thread, is_running
    
    if is_running:
        return True
    
    # Check if required modules are available
    try:
        import serial
        import pynmea2
    except ImportError as e:
        print(f"Required module missing: {e}")
        print("Please install missing modules with: sudo pip3 install pyserial pynmea2")
        return False
    
    # Check if port exists, try autodetection if not
    if not os.path.exists(config.port):
        print(f"GPS port {config.port} not found")
        detected_port = find_gps_port()
        if detected_port:
            print(f"Using auto-detected port: {detected_port}")
            config.port = detected_port
        else:
            print("No GPS ports found")
            return False
    
    # Start monitoring thread
    try:
        print(f"Starting GPS monitoring on {config.port}")
        is_running = True
        gps_thread = threading.Thread(target=_gps_monitoring_thread)
        gps_thread.daemon = True
        gps_thread.start()
        return True
    except Exception as e:
        print(f"Error starting GPS monitoring: {e}")
        is_running = False
        return False

def _gps_monitoring_thread():
    """Thread function for GPS monitoring."""
    global is_running, gps_data
    
    # Import required modules
    try:
        import serial
        import pynmea2
    except ImportError as e:
        print(f"Required module missing in monitoring thread: {e}")
        is_running = False
        return
    
    print(f"Starting GPS monitoring on {config.port} at {config.baud_rate} baud")
    
    while is_running:
        try:
            # Try to open serial port
            with serial.Serial(config.port, baudrate=config.baud_rate, 
                              timeout=config.timeout) as ser:
                print(f"Connected to GPS module at {config.port}")
                
                with gps_lock:
                    gps_data['status'] = 'connected'
                
                # Read data continuously
                while is_running:
                    try:
                        # Read a line from the GPS module
                        line = ser.readline().decode('ascii', errors='replace').strip()
                        
                        # Skip empty lines
                        if not line:
                            continue
                            
                        # Parse NMEA sentences
                        if line.startswith('$'):
                            try:
                                msg = pynmea2.parse(line)
                                
                                # Extract GPS data from different message types
                                if isinstance(msg, pynmea2.GGA):  # Global Positioning System Fix Data
                                    with gps_lock:
                                        gps_data['latitude'] = msg.latitude
                                        gps_data['longitude'] = msg.longitude
                                        gps_data['altitude'] = msg.altitude
                                        gps_data['fix_quality'] = msg.gps_qual
                                        gps_data['satellites'] = msg.num_sats
                                        gps_data['timestamp'] = str(msg.timestamp)
                                        gps_data['last_update'] = datetime.now().isoformat()
                                        gps_data['status'] = 'active' if msg.gps_qual > 0 else 'no_fix'
                                        
                                elif isinstance(msg, pynmea2.RMC):  # Recommended Minimum Data
                                    with gps_lock:
                                        if hasattr(msg, 'spd_over_grnd') and msg.spd_over_grnd is not None:
                                            gps_data['speed'] = msg.spd_over_grnd * 1.852  # knots to km/h
                                        if hasattr(msg, 'true_course') and msg.true_course is not None:
                                            gps_data['course'] = msg.true_course
                                
                            except pynmea2.ParseError:
                                # Skip parse errors
                                continue
                    
                    except serial.SerialException as e:
                        print(f"Serial error: {e}")
                        with gps_lock:
                            gps_data['status'] = 'error'
                        break
                        
                    except Exception as e:
                        print(f"Error reading GPS data: {e}")
                        # Continue trying to read
                        continue
        
        except serial.SerialException as e:
            print(f"Failed to connect to GPS: {e}")
            with gps_lock:
                gps_data['status'] = 'disconnected'
            
            # Wait before retry
            time.sleep(5)
            
        except Exception as e:
            print(f"Unexpected GPS error: {e}")
            with gps_lock:
                gps_data['status'] = 'error'
            
            # Wait before retry
            time.sleep(5)

def get_gps_data():
    """Get the current GPS data."""
    with gps_lock:
        return gps_data.copy()

def stop_gps_monitoring():
    """Stop GPS monitoring."""
    global is_running
    
    is_running = False
    
    if gps_thread is not None:
        try:
            gps_thread.join(timeout=2.0)
        except:
            pass
    
    print("GPS monitoring stopped")
    return True

def format_gps_for_display():
    """Format GPS data for human-readable display."""
    with gps_lock:
        data = gps_data.copy()
    
    formatted = {
        'status': data['status'],
        'coordinates': 'Unknown'
    }
    
    # Format coordinates if available
    if data['latitude'] is not None and data['longitude'] is not None:
        lat_dir = 'N' if data['latitude'] >= 0 else 'S'
        lon_dir = 'E' if data['longitude'] >= 0 else 'W'
        formatted['coordinates'] = f"{abs(data['latitude']):.6f}° {lat_dir}, {abs(data['longitude']):.6f}° {lon_dir}"
    
    # Add other data
    if data['speed'] is not None:
        formatted['speed'] = f"{data['speed']:.1f} km/h"
    else:
        formatted['speed'] = 'Unknown'
        
    if data['altitude'] is not None:
        formatted['altitude'] = f"{data['altitude']:.1f} m"
    else:
        formatted['altitude'] = 'Unknown'
    
    if data['satellites'] is not None:
        formatted['satellites'] = str(data['satellites'])
    else:
        formatted['satellites'] = 'Unknown'
    
    # Add status description
    status_descriptions = {
        'disconnected': 'GPS module not connected',
        'connected': 'Connected, waiting for fix',
        'no_fix': 'No GPS fix yet',
        'active': 'GPS fix active',
        'error': 'GPS error'
    }
    
    formatted['status_description'] = status_descriptions.get(data['status'], 'Unknown status')
    
    return formatted

# Test function when run directly
if __name__ == "__main__":
    print("GPS Module Test")
    print(f"GPS port: {config.port}")
    print(f"Port exists: {'Yes' if os.path.exists(config.port) else 'No'}")
    
    if start_gps_monitoring():
        print("GPS monitoring started successfully")
        
        try:
            for i in range(6):
                print("\nGPS data:")
                info = format_gps_for_display()
                for key, value in info.items():
                    print(f"{key}: {value}")
                time.sleep(5)
        except KeyboardInterrupt:
            print("\nTest interrupted")
        finally:
            stop_gps_monitoring()
    else:
        print("Failed to start GPS monitoring")