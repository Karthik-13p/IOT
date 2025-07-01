# PowerShell script to transfer motor fix files to Raspberry Pi
# Set Pi connection details
$PI_IP = "192.168.1.9"
$PI_USER = "pi"
$PI_PATH = "/home/pi/pi-motor-control-project"  # Updated path to match the actual directory on Pi

# Define files to transfer - only motor fix related files
$FILES_TO_TRANSFER = @(
    # Motor fix files
    "fix_web_motors.py",
    "apply_web_motor_fix.py",
    "diagnose_web_motors.sh",
    "test_motor_fixes.py",
    # Updated motor control implementation
    "src/motor_control/pi_to_motor.py",
    # Updated web app
    "src/web/app.py"
)

Write-Host "Starting motor fix file transfer to Raspberry Pi at $PI_IP..." -ForegroundColor Cyan

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

# Make scripts executable
Write-Host "Making scripts executable..." -ForegroundColor Yellow
ssh $PI_USER@$PI_IP "chmod +x $PI_PATH/diagnose_web_motors.sh $PI_PATH/apply_web_motor_fix.py $PI_PATH/fix_web_motors.py"

Write-Host "Motor fix file transfer completed!" -ForegroundColor Cyan

Write-Host "`nTo fix the web motor interface issues, connect via SSH and run:" -ForegroundColor Magenta
Write-Host "cd $PI_PATH && sudo python3 apply_web_motor_fix.py" -ForegroundColor White

Write-Host "`nTo diagnose web motor issues:" -ForegroundColor Magenta
Write-Host "cd $PI_PATH && sudo ./diagnose_web_motors.sh" -ForegroundColor White

Write-Host "`nTo test the motor fixes:" -ForegroundColor Magenta
Write-Host "cd $PI_PATH && sudo python3 test_motor_fixes.py" -ForegroundColor White

Write-Host "`nTo start the web application after applying fixes:" -ForegroundColor Magenta
Write-Host "cd $PI_PATH && sudo python3 src/main.py" -ForegroundColor White
