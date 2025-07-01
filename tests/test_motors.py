import unittest
from src.motor_control.pi_to_motor import initialize_motors, set_motor_speed, move_forward, move_backward, turn_left, turn_right, stop, cleanup_motors

class TestMotorControl(unittest.TestCase):

    def setUp(self):
        """Set up the motors before each test."""
        self.initialized = initialize_motors()
    
    def tearDown(self):
        """Clean up the motors after each test."""
        cleanup_motors()

    def test_initialize_motors(self):
        """Test if motors are initialized successfully."""
        self.assertTrue(self.initialized)

    def test_set_motor_speed(self):
        """Test setting motor speed."""
        self.assertTrue(set_motor_speed(1, 50))
        self.assertTrue(set_motor_speed(2, -50))
        self.assertTrue(set_motor_speed(1, 0))
        self.assertTrue(set_motor_speed(2, 0))

    def test_move_forward(self):
        """Test moving forward."""
        self.assertTrue(move_forward(50))

    def test_move_backward(self):
        """Test moving backward."""
        self.assertTrue(move_backward(50))

    def test_turn_left(self):
        """Test turning left."""
        self.assertTrue(turn_left(50))

    def test_turn_right(self):
        """Test turning right."""
        self.assertTrue(turn_right(50))

    def test_stop(self):
        """Test stopping the motors."""
        self.assertTrue(stop())

if __name__ == '__main__':
    unittest.main()