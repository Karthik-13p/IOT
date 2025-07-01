#!/usr/bin/env python3
"""
Fix for apply_web_motor_fix.py - Repairs syntax errors
with triple-quoted strings in the file
"""

import os
import sys
import re

def main():
    # Find the file path
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'apply_web_motor_fix.py')
    
    if not os.path.exists(script_path):
        print(f"Error: File not found at {script_path}")
        return False
    
    print(f"Fixing file: {script_path}")
    
    try:
        # Read the file
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix nested triple-quoted strings
        # Replace the problematic patterns
        
        # Pattern 1: Make control_motors_original safe
        pattern1 = r'control_motors_original = """@app\.route\(.*?API endpoint to control motors\."""'
        replacement1 = r'control_motors_original = """@app.route(\'/api/motors/control\', methods=[\'POST\'])\ndef control_motors():\n    \"\"\"API endpoint to control motors.\"\"\""'
        
        content = re.sub(pattern1, replacement1, content, flags=re.DOTALL)
        
        # Pattern 2: Make control_motors_fixed safe
        pattern2 = r'control_motors_fixed = """@app\.route\(.*?API endpoint to control motors\."""'
        replacement2 = r'control_motors_fixed = """@app.route(\'/api/motors/control\', methods=[\'POST\'])\ndef control_motors():\n    \"\"\"API endpoint to control motors.\"\"\""'
        
        content = re.sub(pattern2, replacement2, content, flags=re.DOTALL)
        
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
