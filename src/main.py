#!/usr/bin/env python3
import os
import sys
import signal
import threading
import time
import argparse
import json
import subprocess
import platform
import importlib
import logging

# Set up logging
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'wheelchair.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('wheelchair')

# Add the parent directory to the path so we can import project modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Global flag for shutdown
running = True

def signal_handler(sig, frame):
    """Handle Ctrl+C and other signals to shutdown cleanly."""
    global running
    logger.info("Shutting down...")
    running = False
    # Allow time for cleanup
    time.sleep(1)
    sys.exit(0)

def check_system():
    """Check system compatibility and requirements."""
    
    # Get system info
    print(f"System: {platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()}")
    
    # Check for GPIO module
    try:
        import RPi.GPIO as GPIO
        print(f"RPi.GPIO: {GPIO.VERSION}")
    except ImportError:
        print("RPi.GPIO: Not installed")
    
    # Check for key modules
    modules = ["serial", "flask", "pynmea2"]
    for module_name in modules:
        try:
            module = importlib.import_module(module_name)
            version = getattr(module, "__version__", "Unknown")
            print(f"{module_name}: {version}")
        except ImportError:
            print(f"{module_name}: Not installed")
    
    # Check directory structure
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"Base directory: {base_dir}")
    
    for required_dir in ["src", "config", "data"]:
        check_dir = os.path.join(base_dir, required_dir)
        if os.path.isdir(check_dir):
            print(f"✓ {required_dir} directory found")
        else:
            print(f"✗ {required_dir} directory missing")

def main():
    """Main program entry point."""
    global running
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Load settings from config file
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'settings.json')
    try:
        with open(config_path, 'r') as f:
            settings = json.load(f)
        logger.info(f"Loaded settings from {config_path}")
    except Exception as e:
        logger.error(f"Error loading settings: {e}")
        settings = {}
    
    # Get web interface settings
    web_settings = settings.get('web_interface', {})
    web_port = web_settings.get('port', 5001)  # Changed default from 5000 to 5001
    web_debug = web_settings.get('debug', False)
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Wheelchair Control System')
    parser.add_argument('--port', type=int, default=web_port, help='Web server port')
    parser.add_argument('--debug', action='store_true', default=web_debug, help='Enable debug mode')
    parser.add_argument('--no-motor', action='store_true', help='Disable motor control')
    parser.add_argument('--no-sensor', action='store_true', help='Disable sensors')
    parser.add_argument('--no-web', action='store_true', help='Disable web interface')
    parser.add_argument('--no-gps', action='store_true', help='Disable GPS module')

    args = parser.parse_args()
    
    # Initialize global variables
    WEB_INTERFACE_AVAILABLE = not args.no_web
    MOTOR_CONTROL_AVAILABLE = not args.no_motor
    SENSOR_AVAILABLE = not args.no_sensor
    GPS_AVAILABLE = not args.no_gps

    
    # Initialize status flags
    motors_initialized = False
    sensor_initialized = False
    obstacle_detection_initialized = False
    gps_initialized = False

    
    try:
        logger.info("Starting SWheels control system...")
        
        # Import modules here to handle import errors more gracefully
        try:
            if MOTOR_CONTROL_AVAILABLE:
                from motor_control import pi_to_motor as motor
                logger.info("Motor control module loaded")
        except ImportError as e:
            logger.error(f"Error importing motor control module: {e}")
            logger.warning("Running without motor control")
            MOTOR_CONTROL_AVAILABLE = False
            
        try:
            if SENSOR_AVAILABLE:
                from sensors import distance_sensor
                logger.info("Sensor module loaded")
        except ImportError as e:
            logger.error(f"Error importing sensor module: {e}")
            logger.warning("Running without sensor support")
            SENSOR_AVAILABLE = False
            
        # Initialize hardware
        if MOTOR_CONTROL_AVAILABLE:
            logger.info("Initializing motors with 1kHz PWM frequency for optimal performance...")
            try:
                # Attempt initialization with retry logic
                retry_count = 0
                max_retries = 3
                motors_initialized = False
                
                while not motors_initialized and retry_count < max_retries:
                    motors_initialized = motor.initialize_motors(timeout=5.0)
                    if motors_initialized:
                        logger.info(f"Motors initialized successfully on attempt {retry_count + 1}/{max_retries}")
                        # Ensure motors are stopped initially
                        motor.stop()
                        logger.info("Motors set to initial stopped state")
                        break
                    else:
                        retry_count += 1
                        logger.warning(f"Motor initialization failed on attempt {retry_count}/{max_retries}")
                        time.sleep(1)  # Wait before retry
                
                if not motors_initialized:
                    logger.error("Motor initialization failed after all retries")
            except Exception as e:
                logger.error(f"Motor initialization error: {e}")
                MOTOR_CONTROL_AVAILABLE = False
                
        if SENSOR_AVAILABLE:
            logger.info("Initializing distance sensor...")
            try:
                sensor_initialized = distance_sensor.setup_distance_sensor()
                if sensor_initialized:
                    logger.info("Distance sensor initialized successfully")
                else:
                    logger.warning("Distance sensor initialization failed")
            except Exception as e:
                logger.error(f"Sensor initialization error: {e}")
                SENSOR_AVAILABLE = False
        
        # Initialize GPS module
        if GPS_AVAILABLE:
            try:
                logger.info("Initializing GPS module...")
                from sensors import gps_module
                gps_started = gps_module.start_gps_monitoring()
                if gps_started:
                    logger.info("GPS monitoring started")
                    gps_initialized = True
                else:
                    logger.warning("Failed to start GPS monitoring")
            except Exception as e:
                logger.error(f"Error initializing GPS module: {e}")
                GPS_AVAILABLE = False
        

        
        # Initialize obstacle detection
        obstacle_detection_initialized = False
        try:
            from sensors import obstacle_detection
            logger.info("Initializing obstacle detection...")
            if obstacle_detection.start_detection():
                logger.info("Obstacle detection initialized successfully")
                obstacle_detection_initialized = True
            else:
                logger.warning("Failed to initialize obstacle detection")
        except Exception as e:
            logger.error(f"Error initializing obstacle detection: {e}")
            obstacle_detection_initialized = False
        
        if WEB_INTERFACE_AVAILABLE:
            try:
                # Import the web app
                from web.app import app
                
                # Pass the initialized components to the web app
                app.config['MOTOR_CONTROL_AVAILABLE'] = MOTOR_CONTROL_AVAILABLE
                app.config['SENSOR_AVAILABLE'] = SENSOR_AVAILABLE
                app.config['GPS_AVAILABLE'] = GPS_AVAILABLE
                
                logger.info(f"Starting web interface at http://0.0.0.0:{args.port}")
                
                # Start the web server in a thread with error handling
                def start_web_server(app, port, debug):
                    try:
                        # Try to start the server
                        app.run(host='0.0.0.0', port=port, debug=debug, use_reloader=False)
                    except OSError as e:
                        if "Address already in use" in str(e):
                            logger.error(f"Port {port} is already in use. Try a different port.")
                            # Try incrementing the port and retrying once
                            try:
                                new_port = port + 1
                                logger.info(f"Attempting to bind to alternate port {new_port}")
                                app.run(host='0.0.0.0', port=new_port, debug=debug, use_reloader=False)
                            except Exception as retry_e:
                                logger.error(f"Failed to bind to alternate port: {retry_e}")
                        else:
                            logger.error(f"Web server error: {e}")
                    except Exception as e:
                        logger.error(f"Failed to start web interface: {e}")
                
                web_thread = threading.Thread(target=start_web_server, args=(app, args.port, args.debug))
                web_thread.daemon = True
                web_thread.start()
                
                # Keep main program running with the web interface
                logger.info("System is running. Press Ctrl+C to stop.")
                while running:
                    # Main event loop
                    try:
                        if SENSOR_AVAILABLE and sensor_initialized:
                            # Periodically read distance for obstacle detection
                            distance = distance_sensor.read_distance()
                            if distance < 30:  # Less than 30cm
                                logger.warning(f"Obstacle detected {distance:.1f}cm ahead")
                                if MOTOR_CONTROL_AVAILABLE and motors_initialized:
                                    motor.stop()  # Stop motors if obstacle is too close
                        
                        # Heartbeat log every 60 seconds
                        if int(time.time()) % 60 == 0:
                            logger.debug("System heartbeat")
                            
                        time.sleep(0.5)
                    except KeyboardInterrupt:
                        break
                    except Exception as e:
                        logger.error(f"Error in main loop: {e}")
                        time.sleep(1)
                    except Exception as e:
                        print(f"Error in main loop: {e}")
                        time.sleep(1)
                
            except ImportError as e:
                print(f"Error importing web interface: {e}")
                # Fall through to the console mode below
        
        else:
            # Keep the program running even without web interface
            print("System is running. Press Ctrl+C to stop.")
            while running:
                try:
                    if SENSOR_AVAILABLE and sensor_initialized:
                        # Periodically read distance for obstacle detection
                        distance = distance_sensor.read_distance()
                        if distance < 30:  # Less than 30cm
                            print(f"Warning: Obstacle detected {distance:.1f}cm ahead")
                            if MOTOR_CONTROL_AVAILABLE and motors_initialized:
                                motor.stop()  # Stop motors if obstacle is too close
                        time.sleep(0.5)
                    else:
                        # Just sleep if sensors aren't available
                        time.sleep(1)
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"Error in main loop: {e}")
                    time.sleep(1)

    except KeyboardInterrupt:
        print("\nKeyboard interrupt received. Shutting down...")
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        # Clean up resources
        running = False
        print("Cleaning up resources...")
        
        # Only clean up what we initialized
        if 'motor_control.pi_to_motor' in sys.modules or (motors_initialized and MOTOR_CONTROL_AVAILABLE):
            try:
                from motor_control import pi_to_motor as motor
                # First ensure motors are stopped
                try:
                    motor.stop()
                    print("Motors stopped")
                except Exception as e:
                    print(f"Warning: Error stopping motors: {e}")
                    
                # Then clean up GPIO resources
                try:
                    motor.cleanup_motors()  # No reset_gpio parameter
                    print("Motors cleaned up")
                except Exception as e:
                    print(f"Error cleaning up motors: {e}")
            except Exception as e:
                print(f"Error handling motor cleanup: {e}")
            
        if sensor_initialized and SENSOR_AVAILABLE:
            try:
                from sensors import distance_sensor
                distance_sensor.cleanup_distance_sensor()
                print("Sensors cleaned up")
            except Exception as e:
                print(f"Error cleaning up sensors: {e}")
        
        if 'gps_module' in sys.modules:
            try:
                from sensors import gps_module
                gps_module.stop_gps_monitoring()
                print("GPS monitoring stopped")
            except Exception as e:
                print(f"Error stopping GPS module: {e}")
            
        if 'obstacle_detection_initialized' in locals() and obstacle_detection_initialized:
            try:
                from sensors import obstacle_detection
                obstacle_detection.stop_detection()
                print("Obstacle detection stopped")
            except Exception as e:
                print(f"Error stopping obstacle detection: {e}")
            
        print("Cleanup complete. Exiting.")

def shutdown_gracefully():
    """Clean shutdown function that can be called from anywhere."""
    global running
    running = False
    print("\nInitiating graceful shutdown...")
    
    # Sleep briefly to allow things to complete
    time.sleep(0.5)
    
    # Import motor control module if needed
    try:
        from motor_control import pi_to_motor as motor
        # Check if motors were initialized
        if hasattr(motor, 'motors_initialized') and motor.motors_initialized:
            try:
                motor.stop()
                print("Motors stopped")
                motor.cleanup_motors(reset_gpio=True)
                print("Motors cleaned up")
            except Exception as e:
                print(f"Error stopping motors: {e}")
    except ImportError:
        print("Motor control module not available for shutdown")
    except Exception as e:
        print(f"Error during graceful shutdown: {e}")

def ensure_process_stays_alive():
    """Output a periodic heartbeat to ensure the process keeps running."""
    global running
    next_heartbeat = time.time() + 60  # First heartbeat after 60 seconds
    
    while running:
        try:
            current_time = time.time()
            if current_time >= next_heartbeat:
                print("Wheelchair system running... (heartbeat)")
                next_heartbeat = current_time + 60  # Next heartbeat in 60 seconds
            time.sleep(1)
        except Exception:
            time.sleep(5)  # In case of error, retry after a longer delay


if __name__ == "__main__":
    main()