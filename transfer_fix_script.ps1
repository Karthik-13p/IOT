# PowerShell script to transfer just the fix_setup.sh file to the Pi
# Set Pi connection details
$PI_IP = "192.168.1.9"
$PI_USER = "pi"
$PI_PATH = "/home/pi/pi-motor-control-project"

Write-Host "Transferring fix_setup.sh to Raspberry Pi..." -ForegroundColor Cyan

# Transfer the fix script
$localPath = Join-Path -Path (Get-Location) -ChildPath "fix_setup.sh"
scp $localPath "$PI_USER@$PI_IP`:$PI_PATH/fix_setup.sh"

if ($LASTEXITCODE -eq 0) {
    Write-Host "Successfully transferred fix_setup.sh" -ForegroundColor Green
    
    # Make it executable
    ssh $PI_USER@$PI_IP "chmod +x $PI_PATH/fix_setup.sh"
    Write-Host "Made fix_setup.sh executable" -ForegroundColor Green
    
    Write-Host "`nTo run the setup script, connect via SSH and run:" -ForegroundColor Magenta
    Write-Host "cd $PI_PATH && ./fix_setup.sh" -ForegroundColor White
} else {
    Write-Host "Failed to transfer fix_setup.sh" -ForegroundColor Red
}
