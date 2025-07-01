#!/bin/bash
# Shell script to transfer updated motor control files to Raspberry Pi

# Set Pi connection details
PI_IP="192.168.1.9"
PI_USER="pi"
PI_PATH="/home/pi/pi-motor-control-project"  # Updated path to match the actual directory on Pi

# Define files to transfer
FILES_TO_TRANSFER=(
    "src/motor_control/pi_to_motor.py"
    "src/main.py"
    "src/web/app.py"
    "test_optimized_motors.py"
    "fix_setup.sh"
    "MOTOR_OPTIMIZATIONS.md"
)

echo -e "\033[1;36mStarting file transfer to Raspberry Pi at $PI_IP...\033[0m"

for file in "${FILES_TO_TRANSFER[@]}"; do
    # Create target directory if needed
    remote_dir=$(dirname "$PI_PATH/$file")
    ssh $PI_USER@$PI_IP "mkdir -p $remote_dir"
    
    # Transfer file
    echo -e "\033[1;33mTransferring $file to Pi...\033[0m"
    scp "$(pwd)/$file" "$PI_USER@$PI_IP:$PI_PATH/$file"
    
    if [ $? -eq 0 ]; then
        echo -e "\033[1;32mSuccessfully transferred $file\033[0m"
    else
        echo -e "\033[1;31mFailed to transfer $file\033[0m"
    fi
done

# Make scripts executable
echo -e "\033[1;33mMaking scripts executable...\033[0m"
ssh $PI_USER@$PI_IP "chmod +x $PI_PATH/test_optimized_motors.py $PI_PATH/fix_setup.sh"

echo -e "\033[1;36mFile transfer completed!\033[0m"
echo -e "\n\033[1;35mTo fix setup and install dependencies on the Pi, connect via SSH and run:\033[0m"
echo -e "\033[1;37mcd $PI_PATH && ./fix_setup.sh\033[0m"

echo -e "\n\033[1;35mTo run the optimized motor test on the Pi:\033[0m"
echo -e "\033[1;37msudo python3 $PI_PATH/test_optimized_motors.py\033[0m"

echo -e "\n\033[1;35mTo start the web application:\033[0m"
echo -e "\033[1;37msudo python3 $PI_PATH/src/main.py\033[0m"
