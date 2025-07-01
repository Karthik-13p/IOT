# Hardware Setup for Raspberry Pi Motor Control Project

## Overview
This document outlines the hardware setup required for the Raspberry Pi Motor Control Project. It includes wiring diagrams and specifications for the components used in the project.

## Components Required
- Raspberry Pi (any model with GPIO pins)
- Motor Driver (e.g., L298N)
- DC Motors (2 units)
- Ultrasonic Distance Sensor (e.g., HC-SR04)
- Jumper Wires
- Breadboard (optional)
- Power Supply for Motors

## Wiring Diagram
![Wiring Diagram](path/to/wiring_diagram.png)

## Wiring Instructions

### Motor Connections
1. **Connect the DC Motors to the Motor Driver:**
   - Motor 1:
     - Connect the first motor's terminals to the output pins of the motor driver (e.g., OUT1 and OUT2).
   - Motor 2:
     - Connect the second motor's terminals to the output pins of the motor driver (e.g., OUT3 and OUT4).

2. **Connect the Motor Driver to the Raspberry Pi:**
   - Connect the PWM pin for Motor 1 to GPIO12.
   - Connect IN1 for Motor 1 to GPIO23.
   - Connect IN2 for Motor 1 to GPIO24.
   - Connect the PWM pin for Motor 2 to GPIO13.
   - Connect IN1 for Motor 2 to GPIO27.
   - Connect IN2 for Motor 2 to GPIO22.

### Ultrasonic Sensor Connections
1. **Connect the Ultrasonic Sensor to the Raspberry Pi:**
   - Connect the Trigger pin to a GPIO pin (e.g., GPIO17).
   - Connect the Echo pin to another GPIO pin (e.g., GPIO18).
   - Connect the VCC pin to the 5V pin on the Raspberry Pi.
   - Connect the GND pin to a ground pin on the Raspberry Pi.

## Power Supply
- Ensure that the motor driver is powered with an appropriate power supply that matches the voltage and current requirements of the motors.
- The Raspberry Pi should be powered separately to avoid voltage drops during motor operation.

## Testing the Setup
Once all components are connected, you can run the motor control code to test the functionality of the motors and the ultrasonic sensor. Ensure that the Raspberry Pi is properly configured and that the necessary libraries are installed.

## Conclusion
This hardware setup provides the necessary connections for the Raspberry Pi Motor Control Project. Follow the wiring instructions carefully to ensure proper functionality.