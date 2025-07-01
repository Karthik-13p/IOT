# PowerShell script to transfer the final fix script to the Raspberry Pi
# Set Pi connection details
$PI_IP = "192.168.1.9"
$PI_USER = "pi"
$PI_PATH = "/home/pi/pi-motor-control-project"

Write-Host "Transferring final fix script to Raspberry Pi..." -ForegroundColor Cyan

# Transfer the fix script
$localPath = Join-Path -Path (Get-Location) -ChildPath "final_fix.sh"
scp $localPath "$PI_USER@$PI_IP`:$PI_PATH/final_fix.sh"

if ($LASTEXITCODE -eq 0) {
    Write-Host "Successfully transferred final_fix.sh" -ForegroundColor Green
    
    # Make it executable
    ssh $PI_USER@$PI_IP "chmod +x $PI_PATH/final_fix.sh"
    Write-Host "Made final_fix.sh executable" -ForegroundColor Green
    
    Write-Host "`nTo run the final fix script, connect via SSH and run:" -ForegroundColor Magenta
    Write-Host "cd $PI_PATH && ./final_fix.sh" -ForegroundColor White
} else {
    Write-Host "Failed to transfer final_fix.sh" -ForegroundColor Red
}
