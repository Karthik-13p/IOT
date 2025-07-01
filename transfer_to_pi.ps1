# PowerShell script to transfer updated motor control files to Raspberry Pi
# Set Pi connection details
$PI_IP = "192.168.1.9"
$PI_USER = "pi"
$PI_PATH = "/home/pi/pi-motor-control-project"  # Updated path to match the actual directory on Pi

# Define files to transfer
$FILES_TO_TRANSFER = @(
    "src/motor_control/pi_to_motor.py",
    "src/main.py",
    "src/web/app.py",
    "test_optimized_motors.py",
    "fix_setup.sh",
    "MOTOR_OPTIMIZATIONS.md",
    # New motor web interface fix files
    "fix_web_motors.py",
    "apply_web_motor_fix.py",
    "apply_web_motor_fix_corrected.py",
    "diagnose_web_motors.sh",
    "test_motor_fixes.py"
)

Write-Host "Starting file transfer to Raspberry Pi at $PI_IP..." -ForegroundColor Cyan

foreach ($file in $FILES_TO_TRANSFER) {
    $localPath = Join-Path -Path (Get-Location) -ChildPath $file
    $remotePath = "$PI_PATH/$file"
    
    # Create target directory if needed
    $remoteDir = Split-Path -Parent $remotePath
    ssh $PI_USER@$PI_IP "mkdir -p $remoteDir"
    
    # Transfer file
    Write-Host "Transferring $file to Pi..." -ForegroundColor Yellow
    scp $localPath "$PI_USER@$PI_IP`:$remotePath"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Successfully transferred $file" -ForegroundColor Green
    } else {
        Write-Host "Failed to transfer $file" -ForegroundColor Red
    }
}

# Make test script executable
Write-Host "Making scripts executable..." -ForegroundColor Yellow
ssh $PI_USER@$PI_IP "chmod +x $PI_PATH/test_optimized_motors.py $PI_PATH/fix_setup.sh $PI_PATH/diagnose_web_motors.sh $PI_PATH/apply_web_motor_fix.py $PI_PATH/fix_web_motors.py"

Write-Host "File transfer completed!" -ForegroundColor Cyan
Write-Host "`nTo fix setup and install dependencies on the Pi, connect via SSH and run:" -ForegroundColor Magenta
Write-Host "cd $PI_PATH && ./fix_setup.sh" -ForegroundColor White

Write-Host "`nTo run the optimized motor test on the Pi:" -ForegroundColor Magenta
Write-Host "sudo python3 $PI_PATH/test_optimized_motors.py" -ForegroundColor White

Write-Host "`nTo fix the web motor interface issues:" -ForegroundColor Magenta
Write-Host "cd $PI_PATH && sudo python3 apply_web_motor_fix.py" -ForegroundColor White

Write-Host "`nTo diagnose web motor issues:" -ForegroundColor Magenta
Write-Host "cd $PI_PATH && sudo ./diagnose_web_motors.sh" -ForegroundColor White

Write-Host "`nTo start the web application:" -ForegroundColor Magenta
Write-Host "sudo python3 $PI_PATH/src/main.py" -ForegroundColor White
