"""
This module provides a wrapper to the main distance_sensor module, 
to maintain backward compatibility with existing code.
"""

import sys
import os

# Add parent directory to path to import from sibling packages
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from the actual sensor module
from sensors.distance_sensor import setup_distance_sensor, read_distance, cleanup_distance_sensor

def setup_ultrasonic():
    """Set up the ultrasonic sensor."""
    return setup_distance_sensor()

def is_obstacle_detected(threshold=20):
    """Check if an obstacle is detected.
    
    Args:
        threshold: Distance in cm below which an obstacle is detected
    
    Returns:
        bool: True if an obstacle is detected, False otherwise
    """
    distance = read_distance()
    if distance < 0:  # Error reading distance
        return False
    return distance < threshold

def cleanup_ultrasonic():
    """Clean up resources used by the ultrasonic sensor."""
    return cleanup_distance_sensor()