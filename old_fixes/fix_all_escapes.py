#!/usr/bin/env python3
"""
This script fixes the syntax errors in apply_web_motor_fix_v2.py
by correctly handling the triple-quoted string escaping issues.
"""
import re

def fix_file(filepath):
    print(f"Fixing all triple-quoted strings in: {filepath}")
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Fix the initial triple-quoted docstring
    content = content.replace('\\\"\\\"\\\"', '"""', 2)
    
    # Fix the function docstrings with two replacements
    pattern = r'\"\"\"([^\"]*?)\"\"\"'
    content = re.sub(pattern, r'"""\\1"""', content)
    
    # Fix the problematic docstrings in replacement strings
    pattern = r'def cleanup_app\(\):.*?\"\"\"Clean up resources when app exits\.\"\"\"'
    replacement = r'def cleanup_app():\n    """Clean up resources when app exits."""'
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    pattern = r'def emergency_stop\(\):.*?\"\"\"API endpoint for emergency stop\.\"\"\"'
    replacement = r'def emergency_stop():\n    """API endpoint for emergency stop."""'
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Fix the triple-quoted strings for file contents in f.write sections
    content = content.replace("f.write('''", "f.write(r'''")
    
    # Write the fixed content back to a new file
    fixed_filepath = filepath.replace(".py", "_fixed.py")
    with open(fixed_filepath, 'w') as f:
        f.write(content)
    
    print(f"Fixed file saved as: {fixed_filepath}")
    return fixed_filepath

if __name__ == "__main__":
    fix_file("c:/Users/srini/src/pi_project/pi-motor-control-project/apply_web_motor_fix_v2.py")
