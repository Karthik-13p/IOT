#!/usr/bin/env python3
import os
import sys
import time

# Add the project directory to the path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

print("GPS Module Test Script")
print("=====================")

# Try to import the GPS module
try:
    from sensors import gps_module
    print("GPS module imported successfully")
    
    # Print GPS configuration
    print(f"GPS Port: {gps_module.gps_config.port}")
    print(f"Port exists: {'Yes' if os.path.exists(gps_module.gps_config.port) else 'No'}")
    
    # Start GPS monitoring
    print("Starting GPS monitoring...")
    if gps_module.start_gps_monitoring():
        print("GPS monitoring started successfully")
        
        # Display GPS data for 30 seconds
        for i in range(6):
            print("\nGPS data:")
            info = gps_module.format_gps_for_display()
            for key, value in info.items():
                print(f"{key}: {value}")
            time.sleep(5)
            
        # Stop GPS monitoring
        gps_module.stop_gps_monitoring()
        print("GPS monitoring stopped")
    else:
        print("Failed to start GPS monitoring")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
