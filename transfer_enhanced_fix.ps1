# PowerShell script to transfer the enhanced fix script to the Raspberry Pi
# Set Pi connection details
$PI_IP = "192.168.1.9"
$PI_USER = "pi"
$PI_PATH = "/home/pi/pi-motor-control-project"

Write-Host "Transferring enhanced fix script to Raspberry Pi..." -ForegroundColor Cyan

# Transfer the fix script
$localPath = Join-Path -Path (Get-Location) -ChildPath "fix_enhanced.sh"
scp $localPath "$PI_USER@$PI_IP`:$PI_PATH/fix_enhanced.sh"

if ($LASTEXITCODE -eq 0) {
    Write-Host "Successfully transferred fix_enhanced.sh" -ForegroundColor Green
    
    # Make it executable
    ssh $PI_USER@$PI_IP "chmod +x $PI_PATH/fix_enhanced.sh"
    Write-Host "Made fix_enhanced.sh executable" -ForegroundColor Green
    
    Write-Host "`nTo run the enhanced setup script, connect via SSH and run:" -ForegroundColor Magenta
    Write-Host "cd $PI_PATH && ./fix_enhanced.sh" -ForegroundColor White
} else {
    Write-Host "Failed to transfer fix_enhanced.sh" -ForegroundColor Red
}
