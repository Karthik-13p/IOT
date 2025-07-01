import unittest
from src.sensors.distance_sensor import setup_distance_sensor, read_distance, cleanup_distance_sensor

class TestDistanceSensor(unittest.TestCase):

    def setUp(self):
        setup_distance_sensor()

    def tearDown(self):
        cleanup_distance_sensor()

    def test_read_distance(self):
        distance = read_distance()
        self.assertIsInstance(distance, (int, float), "Distance should be a number")
        self.assertGreaterEqual(distance, 0, "Distance should be non-negative")

if __name__ == '__main__':
    unittest.main()