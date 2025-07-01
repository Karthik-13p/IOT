import sys
print("Python path:", sys.path)
print("\nTrying to import modules...")
try:
    import src.motor_control.pi_to_motor
    print("✓ Successfully imported motor_control module")
except ImportError as e:
    print("✗ Error importing motor_control:", e)
