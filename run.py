#!/usr/bin/env python3
import os
import sys

# Add the src directory to Python's module search path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

# Now import from your src directory
try:
    from main import main
    main()
except ImportError as e:
    print(f"Error importing main module: {e}")
    print("\nChecking available modules:")
    import os
    src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
    print(f"Contents of {src_dir}:")
    for item in os.listdir(src_dir):
        print(f"  - {item}")
    sys.exit(1)
