# PowerShell script to transfer the final set of files to Raspberry Pi
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
    "apply_web_motor_fix_final.py",
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
