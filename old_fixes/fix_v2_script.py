#!/usr/bin/env python3
"""
Fix for apply_web_motor_fix_v2.py - Repairs syntax errors
with nested triple-quoted strings in the file
"""

import os
import sys
import re

def main():
    # Find the file path
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'apply_web_motor_fix_v2.py')
    
    if not os.path.exists(script_path):
        print(f"Error: File not found at {script_path}")
        return False
    
    print(f"Fixing file: {script_path}")
    
    try:
        # Read the file
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix all nested docstrings
        # First replacement
        pattern1 = r'def cleanup_app\(\):\n    """Clean up resources when app exits."""'
        replacement1 = r'def cleanup_app():\n    \"\"\"Clean up resources when app exits.\"\"\\"'
        content = re.sub(pattern1, replacement1, content, flags=re.DOTALL)
        
        # Second replacement
        pattern2 = r'def emergency_stop\(\):\n    """API endpoint for emergency stop."""'
        replacement2 = r'def emergency_stop():\n    \"\"\"API endpoint for emergency stop.\"\"\\"'
        content = re.sub(pattern2, replacement2, content, flags=re.DOTALL)
        
        # Third replacement - also handle any other potential docstrings
        content = content.replace('"""\n', '\\"\\"\\"\n')
        content = content.replace('\n    """', '\n    \\"\\"\\"')
        
        # Write the fixed content back to the file
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"File fixed successfully!")
        return True
    
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    main()
