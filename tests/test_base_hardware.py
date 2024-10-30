# tests/test_base_hardware.py

import unittest
from hardware.fake_hardware import FakeHardwareController
from unittest.mock import patch
    
class TestBaseHardwareController(unittest.TestCase):

    def setUp(self):
        self.controller = FakeHardwareController()

    def tearDown(self):
        self.controller.cleanup()

    def test_initial_state(self):
        self.assertEqual(self.controller.pan_angle, 90)
        self.assertEqual(self.controller.tilt_angle, 90)
        self.assertFalse(self.controller.relay_on)

    def test_process_signals_activate_solenoid(self):
        with patch.object(self.controller, '_log', return_value=None) as mock_log:
            signals = {'dx': 1, 'dy': 1, 'fire': 1}  # Below threshold
            self.controller.process_signals(signals)
            self.assertTrue(self.controller.relay_on)

    def test_process_signals_deactivate_solenoid(self):
        with patch.object(self.controller, '_log', return_value=None) as mock_log:        
            # First activate
            signals = {'dx': 1, 'dy': 1, 'fire': 1}
            self.controller.process_signals(signals)
            self.assertTrue(self.controller.relay_on)

            # Then deactivate
            signals = {'dx': 3, 'dy': 3, 'fire': 0}  # Above threshold
            self.controller.process_signals(signals)
            self.assertFalse(self.controller.relay_on)

    def test_update_servos_within_limits(self):
        with patch.object(self.controller, '_log', return_value=None) as mock_log:
            
            signals = {'dx': 10, 'dy': -10}
            self.controller.process_signals(signals)
            self.assertEqual(self.controller.pan_angle, 100)
            self.assertEqual(self.controller.tilt_angle, 80)

    def test_update_servos_exceeding_limits(self):
        with patch.object(self.controller, '_log', return_value=None) as mock_log:
            
            signals = {'dx': 100, 'dy': -100}
            self.controller.process_signals(signals)
            self.assertEqual(self.controller.pan_angle, self.controller.pan_angle_high_limit)  # Clipped to max
            self.assertEqual(self.controller.tilt_angle, self.controller.tilt_angle_low_limit)   # Clipped to min

    def test_cleanup(self):
        # This test ensures that cleanup doesn't raise errors
        try:
            self.controller.cleanup()
        except Exception as e:
            self.fail(f"Cleanup raised an exception: {e}")

if __name__ == '__main__':
    unittest.main()