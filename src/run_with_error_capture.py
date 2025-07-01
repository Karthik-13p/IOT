#!/usr/bin/env python3
import os
import sys
import traceback
import datetime

def run_main():
    try:
        # Import and run the main module
        import main
        main.main()
    except Exception as e:
        # Get the full traceback
        error_trace = traceback.format_exc()
        
        # Create timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Display the error prominently
        print("\n" + "="*60)
        print(f"ERROR: Smart Wheelchair system failed to start! ({timestamp})")
        print("="*60)
        print(f"\nException: {e}")
        print("\nDetailed traceback:")
        print(error_trace)
        
        # Log the error to a file
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, "error_log.txt")
        with open(log_file, "a") as f:
            f.write(f"\n\n===== ERROR {timestamp} =====\n")
            f.write(f"Command: {' '.join(sys.argv)}\n")
            f.write(f"Exception: {e}\n")
            f.write(error_trace)
        
        print(f"\nError has been logged to: {log_file}")
        print("\nPlease check permissions and hardware connections.")
        print("Run with sudo to ensure proper hardware access.")
        
        # Exit with error status
        sys.exit(1)

if __name__ == "__main__":
    run_main()
