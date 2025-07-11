# pi-motor-control-project

This project is designed to control motors using a Raspberry Pi. It includes functionalities for motor control, distance sensing, and obstacle avoidance, making it suitable for robotics applications.

## Project Structure

- `src/`: Contains the source code for the project.
  - `motor_control/`: Contains motor control logic.
    - `pi_to_motor.py`: Implements motor control functions.
    - `ultrasonic.py`: Handles ultrasonic sensor functionalities.
  - `sensors/`: Contains sensor-related code.
    - `distance_sensor.py`: Implements distance measurement functions.
  - `navigation/`: Contains navigation logic.
    - `obstacle_avoidance.py`: Implements obstacle avoidance strategies.
  - `main.py`: Entry point for the application.
  
- `config/`: Contains configuration settings for the project.
  - `settings.json`: Configuration file for GPIO pin assignments and parameters.

- `tests/`: Contains unit tests for the project.
  - `test_motors.py`: Tests for motor control functionalities.
  - `test_sensors.py`: Tests for distance sensor functionalities.

- `docs/`: Contains documentation for the project.
  - `hardware_setup.md`: Documentation on hardware setup and wiring.
  - `api_reference.md`: API reference for the project's modules and functions.

- `requirements.txt`: Lists the Python dependencies required for the project.

- `setup.py`: Used for packaging the project with metadata and dependencies.

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd pi-motor-control-project
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure the GPIO settings in `config/settings.json` as needed.

## Usage

To run the project, execute the main script:
```
python src/main.py
```

Ensure that the Raspberry Pi is properly set up with the necessary hardware connections as described in the `docs/hardware_setup.md`.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.#   I O T  
 