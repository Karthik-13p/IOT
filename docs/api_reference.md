# API Reference for Pi Motor Control Project

## Overview

This document provides an API reference for the Pi Motor Control Project, detailing the available modules and their functionalities.

## Modules

### motor_control

The `motor_control` module contains functions for controlling the motors of the robot.

#### Functions

- **initialize_motors()**
  - Initializes the motors and sets up the GPIO pins.
  - Returns `True` if successful, `False` otherwise.

- **cleanup_motors()**
  - Cleans up GPIO and PWM resources.
  - Returns `True` if successful, `False` otherwise.

- **set_motor_speed(motor_num, speed)**
  - Sets the speed of the specified motor.
  - Parameters:
    - `motor_num`: The motor number (1 or 2).
    - `speed`: The speed value (-100 to 100).
  - Returns `True` if successful, `False` otherwise.

- **move_forward(speed=50)**
  - Moves both motors forward at the specified speed.
  - Returns `True` if successful, `False` otherwise.

- **move_backward(speed=50)**
  - Moves both motors backward at the specified speed.
  - Returns `True` if successful, `False` otherwise.

- **turn_left(speed=50)**
  - Turns the robot left by moving the right motor forward and the left motor backward.
  - Returns `True` if successful, `False` otherwise.

- **turn_right(speed=50)**
  - Turns the robot right by moving the left motor forward and the right motor backward.
  - Returns `True` if successful, `False` otherwise.

- **stop()**
  - Stops both motors.
  - Returns `True` if successful, `False` otherwise.

### sensors

The `sensors` module contains functions for measuring distance using a distance sensor.

#### Functions

- **setup_distance_sensor()**
  - Initializes the distance sensor.
  - Returns `True` if successful, `False` otherwise.

- **read_distance()**
  - Reads the distance value from the sensor.
  - Returns the distance in centimeters.

### navigation

The `navigation` module contains logic for obstacle avoidance.

#### Functions

- **avoid_obstacles()**
  - Implements obstacle avoidance logic using motor control and distance sensor functionalities.
  - Returns `True` if an obstacle is detected and avoided, `False` otherwise.

## Usage

To use the functionalities provided by this project, import the necessary modules in your main application file and call the desired functions as needed. Ensure that the motors and sensors are properly initialized before attempting to control them.