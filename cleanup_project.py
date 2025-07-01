#!/usr/bin/env python3
"""
This script cleans up the project by removing unnecessary test scripts
and fixing any remaining errors in the motor control code.
"""
import os
import sys
import shutil
import time
from datetime import datetime

def print_section(title):
    """Print a formatted section title."""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def backup_file(filepath):
    """Create a backup of a file."""
    if os.path.exists(filepath):
        backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backups')
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        filename = os.path.basename(filepath)
        backup_path = os.path.join(backup_dir, f"{filename}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}")
        shutil.copy2(filepath, backup_path)
        print(f"Created backup: {backup_path}")
        return backup_path
    return None

def cleanup_test_scripts():
    """Remove unnecessary test scripts."""
    print_section("Cleaning Up Test Scripts")
    
    # List of essential test scripts to keep
    keep_scripts = [
        'test_motor_fixes.py',
        'test_optimized_motors.py',
    ]
    
    # Get all test scripts
    base_dir = os.path.dirname(os.path.abspath(__file__))
    test_scripts = [f for f in os.listdir(base_dir) if f.startswith('test_') and f.endswith('.py')]
    
    # Create a backup directory for removed scripts
    backup_dir = os.path.join(base_dir, 'old_tests')
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print(f"Created backup directory: {backup_dir}")
    
    # Move unnecessary scripts to backup directory
    moved_count = 0
    for script in test_scripts:
        if script not in keep_scripts:
            src_path = os.path.join(base_dir, script)
            dst_path = os.path.join(backup_dir, script)
            shutil.move(src_path, dst_path)
            moved_count += 1
            print(f"Moved {script} to backup directory")
    
    print(f"Cleanup complete. Moved {moved_count} unnecessary test scripts.")

def cleanup_fix_scripts():
    """Clean up multiple fix script versions."""
    print_section("Cleaning Up Fix Scripts")
    
    # List of essential fix scripts to keep
    keep_scripts = [
        'apply_web_motor_fix_cleaned.py',
        'apply_web_motor_fix.sh',
    ]
    
    # Get all fix scripts
    base_dir = os.path.dirname(os.path.abspath(__file__))
    fix_scripts = [f for f in os.listdir(base_dir) 
                 if (f.startswith('apply_') or f.startswith('fix_')) and f.endswith('.py')]
    
    # Create a backup directory for removed scripts
    backup_dir = os.path.join(base_dir, 'old_fixes')
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print(f"Created backup directory: {backup_dir}")
    
    # Move unnecessary scripts to backup directory
    moved_count = 0
    for script in fix_scripts:
        if script not in keep_scripts:
            src_path = os.path.join(base_dir, script)
            dst_path = os.path.join(backup_dir, script)
            shutil.move(src_path, dst_path)
            moved_count += 1
            print(f"Moved {script} to backup directory")
    
    print(f"Cleanup complete. Moved {moved_count} unnecessary fix scripts.")

def create_final_transfer_script():
    """Create a final transfer script for easy deployment."""
    print_section("Creating Final Transfer Script")
    
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'transfer_final_files.ps1')
    
    try:
        with open(script_path, 'w') as f:
            f.write(r'''# PowerShell script to transfer the final set of files to Raspberry Pi
# Set Pi connection details
$PI_IP = "192.168.1.9"
$PI_USER = "pi"
$PI_PATH = "/home/pi/pi-motor-control-project"

Write-Host "Transferring fixed motor control files to Raspberry Pi..."

# Essential files to transfer
$FILES_TO_TRANSFER = @(
    "src/motor_control/pi_to_motor.py",
    "src/web/app.py",
    "test_motor_fixes.py",
    "apply_web_motor_fix_cleaned.py",
    "apply_web_motor_fix.sh"
)

# Transfer each file
foreach ($file in $FILES_TO_TRANSFER) {
    Write-Host "Transferring $file to Pi..."
    
    # Create the parent directory if needed
    if ($file -match "^(.+)/[^/]+$") {
        $dir = $Matches[1]
        ssh "${PI_USER}@${PI_IP}" "mkdir -p ${PI_PATH}/$dir"
    }
    
    # Copy the file
    scp "$PSScriptRoot/$file" "${PI_USER}@${PI_IP}:${PI_PATH}/$file"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Successfully transferred $file" -ForegroundColor Green
    } else {
        Write-Host "Failed to transfer $file" -ForegroundColor Red
    }
}

# Make scripts executable
Write-Host "Making scripts executable..."
ssh "${PI_USER}@${PI_IP}" "chmod +x ${PI_PATH}/*.py ${PI_PATH}/*.sh"

Write-Host "`nTransfer complete!" -ForegroundColor Green
Write-Host "`nTo apply the fix on the Pi, connect via SSH and run:"
Write-Host "cd ${PI_PATH} && sudo ./apply_web_motor_fix.sh" -ForegroundColor Cyan

Write-Host "`nTo test the motors directly:"
Write-Host "cd ${PI_PATH} && sudo python3 test_motor_fixes.py" -ForegroundColor Cyan
''')
        
        print(f"Created final transfer script: {script_path}")
        return True
        
    except Exception as e:
        print(f"Error creating transfer script: {e}")
        return False

def main():
    """Main function."""
    print("=== Project Cleanup and Final Setup ===")
    
    # Clean up test scripts
    cleanup_test_scripts()
    
    # Clean up fix scripts
    cleanup_fix_scripts()
    
    # Create final transfer script
    create_final_transfer_script()
    
    print("\n=== All Done! ===")
    print("To transfer the fixed files to your Raspberry Pi, run:")
    print("  .\\transfer_final_files.ps1")
    print("\nThen SSH into your Pi and run:")
    print("  cd /home/pi/pi-motor-control-project && sudo ./apply_web_motor_fix.sh")

if __name__ == "__main__":
    main()
