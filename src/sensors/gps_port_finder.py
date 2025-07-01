#!/usr/bin/env python3
import os
import json
import glob

def find_available_gps_port():
    """Find available serial ports for GPS connection."""
    # Common GPS ports to check
    potential_ports = [
        '/dev/ttyAMA0',  # Common for older Pis
        '/dev/ttyS0',    # Common for newer Pis
        '/dev/ttyUSB0'   # Common for USB GPS modules
    ]
    
    # Add any additional ttyUSB devices
    usb_ports = glob.glob('/dev/ttyUSB*')
    for port in usb_ports:
        if port not in potential_ports:
            potential_ports.append(port)
    
    # Check which ports actually exist
    available_ports = [port for port in potential_ports if os.path.exists(port)]
    
    if not available_ports:
        print("No potential GPS ports found")
        return None
    
    print(f"Found potential GPS ports: {', '.join(available_ports)}")
    
    # Default to the first available port
    return available_ports[0]

def update_gps_port_in_settings():
    """Update the GPS port in settings.json based on available ports."""
    # Find the settings.json file
    config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config')
    settings_file = os.path.join(config_dir, 'settings.json')
    
    if not os.path.exists(settings_file):
        print(f"Settings file not found at {settings_file}")
        return False
    
    # Find available GPS port
    port = find_available_gps_port()
    if not port:
        print("No GPS ports available, settings not updated")
        return False
    
    try:
        # Load current settings
        with open(settings_file, 'r') as f:
            settings = json.load(f)
        
        # Update GPS port
        if 'gps' not in settings:
            settings['gps'] = {}
        
        current_port = settings.get('gps', {}).get('port')
        
        if current_port != port:
            settings['gps']['port'] = port
            
            # Save updated settings
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            
            print(f"GPS port updated from {current_port} to {port}")
            return True
        else:
            print(f"GPS port already set to {port}, no update needed")
            return True
            
    except Exception as e:
        print(f"Error updating GPS port: {e}")
        return False

if __name__ == "__main__":
    update_gps_port_in_settings()
