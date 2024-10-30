# tests/test_base_hardware.py

import unittest
from hardware.fake_hardware import FakeHardwareController
from unittest.mock import patch
from app.target_tracker import TargetTracker
    
class TestBaseHardwareController(unittest.TestCase):

    def setUp(self):
        self.controller = FakeHardwareController()
        self.tracker = TargetTracker()

    def tearDown(self):
        self.controller.cleanup()

    def test_initial_state(self):
        self.assertEqual(self.controller._pan_angle, 90)
        self.assertEqual(self.controller._tilt_angle, 90)
        self.assertFalse(self.controller._relay_on)

    # def test_process_signals_activate_solenoid(self):
    #     with patch.object(self.controller, '_log', return_value=None) as mock_log:
    #         self.tracker.fire = True
    #         self.tracker.target = {'name': 'bird'}
    #         self.controller.process_signals(self.tracker)
    #         self.assertTrue(self.controller.relay_on)

    def test_process_signals_deactivate_solenoid(self):
        with patch.object(self.controller, '_log', return_value=None) as mock_log:        
            # First activate
            self.tracker.fire = True
            self.tracker.target = {'name': 'bird'}
            self.controller.process_signals(self.tracker)
            self.assertTrue(self.controller._relay_on)

            # Then deactivate
            self.tracker.fire = False
            self.tracker.target = {'name': 'bird'}
            self.controller.process_signals(self.tracker)
            self.assertFalse(self.controller._relay_on)

    def test_update_servos_within_limits(self):
        with patch.object(self.controller, '_log', return_value=None) as mock_log:
            
            self.tracker.dx = 10
            self.tracker.dy = -10
            self.tracker.target = {'name': 'bird'}
            
            self.controller.process_signals(self.tracker)
            self.assertEqual(self.controller._pan_angle, 100)
            self.assertEqual(self.controller._tilt_angle, 80)

    def test_update_servos_exceeding_limits(self):
        with patch.object(self.controller, '_log', return_value=None) as mock_log:
            
            self.tracker.dx = 100
            self.tracker.dy = -100
            self.tracker.target = {'name': 'bird'}
            
            self.controller.process_signals(self.tracker)
            self.assertEqual(self.controller._pan_angle, self.controller._pan_angle_high_limit)  # Clipped to max
            self.assertEqual(self.controller._tilt_angle, self.controller._tilt_angle_low_limit)   # Clipped to min

    # def test_patrol(self):
    #     with patch.object(self.controller, '_smooth_pan') as mock_smooth_pan:
    #         with patch.object(self.controller, 'deactivate_solenoid') as mock_deactivate_solenoid:
    #             self.controller._last_tracking = time.time() - self.controller._tracking_pause - 1
    #             self.controller._last_scan = time.time() - self.controller._scan_interval - 1
    #             self.controller.patrol()
    #             mock_deactivate_solenoid.assert_called_once()
    #             mock_smooth_pan.assert_called_once()
    
    # def test_smooth_pan(self):
    #     with patch.object(self.controller, '_smooth_pan_handler') as mock_handler:
    #         self.controller._smooth_pan(90, 90, 1)
    #         self.assertTrue(self.controller._smooth_thread.is_alive())
    #         self.controller._smooth_stop_event.set()  # Stop the thread for testing

    # def test_smooth_pan_handler(self):
    #     with patch.object(self.controller, '_update_servos') as mock_update_servos:
    #         self.controller._pan_angle = 0
    #         self.controller._tilt_angle = 0
    #         self.controller._smooth_pan_handler(30, 30, 0.1)
    #         self.assertEqual(self.controller._pan_angle, 30)
    #         self.assertEqual(self.controller._tilt_angle, 30)
    #         self.assertTrue(mock_update_servos.called)
    
    def test_cleanup(self):
        # This test ensures that cleanup doesn't raise errors
        try:
            self.controller.cleanup()
        except Exception as e:
            self.fail(f"Cleanup raised an exception: {e}")

if __name__ == '__main__':
    unittest.main()