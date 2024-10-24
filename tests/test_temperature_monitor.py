# test_temperature_monitor.py

import unittest
from unittest.mock import patch
    
from app.temperature_monitor import TemperatureMonitor
import threading
import time

class TestTemperatureMonitor(unittest.TestCase):
    def setUp(self):
        # Initialize the TemperatureMonitor with specific parameters if needed
        self.temp_monitor = TemperatureMonitor(
            max_temp=80,
            stable_temp=70.0,
            stable_temp_window=3.0,
            check_interval=0.01,  # Reduced for faster testing
            moving_avg_readings=3,
            starting_throttle_time=0.1,
            throttle_up_multiplier=1.3,
            throttle_down_divisor=1.1
        )

    def tearDown(self):
        # Ensure that the monitor is stopped after each test
        # Check if the thread was started before attempting to stop
        if self.temp_monitor.thread.is_alive():
            self.temp_monitor.stop()

    @patch('app.temperature_monitor.os.popen')
    def test_throttle_time_increases_and_overheat_event_set(self, mock_popen):
        """
        Test that throttle_time increases correctly and overheat_event is set when avg_temp >= max_temp.
        """
        # Define a sequence of temperatures to trigger throttle_time increases and overheat
        temperature_sequence = [78, 82, 85]  # Ensures avg_temp >= 80°C

        # Mock the get_cpu_temp method to return temperatures from the sequence
        def mock_measure_temp():
            if temperature_sequence:
                return f"temp={temperature_sequence.pop(0)}'C\n"
            return "temp=80'C\n"  # Default value after sequence is exhausted

        mock_popen.return_value.readline.side_effect = mock_measure_temp

        # Start the TemperatureMonitor
        with patch.object(self.temp_monitor, '_log', return_value=None) as mock_log:
            self.temp_monitor.start()

            # Allow some time for the monitor to process all temperatures
            # Number of temperatures * check_interval + buffer
            time.sleep(0.04)  # 3 temps *0.01 + buffer

            with self.temp_monitor.throttle_lock:
                current_throttle = self.temp_monitor.throttle_time

            self.assertAlmostEqual(current_throttle, 0.169, places=5)

            # Assertions for overheat_event being set
            self.assertTrue(self.temp_monitor.overheat_event.is_set())

    @patch('app.temperature_monitor.os.popen')
    @patch('app.temperature_monitor.TemperatureMonitor._log')  # Suppress print statements
    def test_throttle_time_reset_to_none(self, mock_popen, mock_log):
        """
        Test throttling clears on cool down.
        """
        # Define a sequence where temperatures rise and then fall back to stable_temp
        temperature_sequence = [81, 82, 83, 76, 70, 65]  # Added multiple 65°C

        def mock_measure_temp():
            if temperature_sequence:
                return f"temp={temperature_sequence.pop(0)}'C\n"
            return "temp=65'C\n"

        mock_popen.return_value.readline.side_effect = mock_measure_temp

        # Start the TemperatureMonitor
        self.temp_monitor.start()

        # Allow some time for the monitor to process temperatures
        time.sleep(0.2)  # Enough time to process all temps

        # Assertions for throttle_time increases and decreases
        # Final throttle_time should have been set to None after sufficient decreases

        with self.temp_monitor.throttle_lock:
            throttle_after_reset = self.temp_monitor.throttle_time

        # Now, throttle_time should have been reset to None
        self.assertIsNone(throttle_after_reset)

        # Overheat event should be cleared
        self.assertFalse(self.temp_monitor.overheat_event.is_set())

    @patch('app.temperature_monitor.os.popen')
    def test_throttle_method_halt_behavior(self, mock_popen):
        """
        Test total halt on overheat.
        """
        # Define temperatures to set throttle_time
        temperature_sequence = [78, 80, 82, 76, 65]  # Extended to reset throttle_time

        def mock_measure_temp():
            if temperature_sequence:
                return f"temp={temperature_sequence.pop(0)}'C\n"
            return "temp=65'C\n"

        mock_popen.return_value.readline.side_effect = mock_measure_temp

        # Start the TemperatureMonitor
        with patch.object(self.temp_monitor, '_log', return_value=None) as mock_log:
            with patch.object(self.temp_monitor, '_halt', return_value=None) as mock_halt:
            
                self.temp_monitor.start()

                # Allow some time for the monitor to process temperatures and set throttle_time
                time.sleep(0.03)
                self.assertTrue(self.temp_monitor.overheat_event.is_set())

                self.temp_monitor.throttle()
                
                # TODO make sure self.temp_monitor.halt() was called
                mock_halt.assert_called()

                # Ensure overheat_event is set
                self.assertFalse(self.temp_monitor.overheat_event.is_set())


    @patch('app.temperature_monitor.os.popen')
    def test_throttle_method_slowdown_behavior(self, mock_popen):
        """
        Test it throttles down.
        """
        # Define temperatures to set throttle_time
        temperature_sequence = [77, 78, 79, 76, 65]  # Extended to reset throttle_time

        def mock_measure_temp():
            if temperature_sequence:
                return f"temp={temperature_sequence.pop(0)}'C\n"
            return "temp=65'C\n"

        mock_popen.return_value.readline.side_effect = mock_measure_temp

        # Start the TemperatureMonitor
        with patch.object(self.temp_monitor, '_log', return_value=None) as mock_log:
            with patch.object(self.temp_monitor, '_slowdown', return_value=None) as mock_slow:
            
                self.temp_monitor.start()

                time.sleep(0.015)
                self.temp_monitor.throttle()
                time.sleep(0.015)
                self.temp_monitor.throttle()

                # TODO make sure self.temp_monitor.halt() was called
                mock_slow.assert_any_call(0.10)
                mock_slow.assert_any_call(0.13)

    @patch('app.temperature_monitor.os.popen')
    def test_it_doesnt_throttle_when_cool(self, mock_popen):
        """
        Test it doesn't throttle when cool.
        """
        # Define temperatures to set throttle_time
        temperature_sequence = [50, 51, 52]  # Extended to reset throttle_time

        def mock_measure_temp():
            if temperature_sequence:
                return f"temp={temperature_sequence.pop(0)}'C\n"
            return "temp=65'C\n"

        mock_popen.return_value.readline.side_effect = mock_measure_temp

        # Start the TemperatureMonitor
        with patch.object(self.temp_monitor, '_log', return_value=None) as mock_log:
            with patch.object(self.temp_monitor, '_slowdown', return_value=None) as mock_slow:
            
                self.temp_monitor.start()

                time.sleep(0.015)
                self.temp_monitor.throttle()
                time.sleep(0.015)
                self.temp_monitor.throttle()

                # TODO make sure self.temp_monitor.halt() was called
                mock_slow.assert_not_called()

    @patch('app.temperature_monitor.os.popen')
    def test_stable_in_window(self, mock_popen):
        """
        Test its stable in the stable window.
        """
        # Define temperatures to set throttle_time
        temperature_sequence = [72, 72.5, 70, 69.5, 70.5]  # Extended to reset throttle_time

        def mock_measure_temp():
            if temperature_sequence:
                return f"temp={temperature_sequence.pop(0)}'C\n"
            return "temp=65'C\n"

        mock_popen.return_value.readline.side_effect = mock_measure_temp

        # Start the TemperatureMonitor
        with patch.object(self.temp_monitor, '_log', return_value=None) as mock_log:
            with patch.object(self.temp_monitor, '_slowdown', return_value=None) as mock_slow:
            
                self.temp_monitor.start()

                time.sleep(0.015)
                with self.temp_monitor.throttle_lock:
                    self.assertAlmostEqual(self.temp_monitor.throttle_time, 0.1)
                
                time.sleep(0.01)
                with self.temp_monitor.throttle_lock:
                    self.assertAlmostEqual(self.temp_monitor.throttle_time, 0.1)

                time.sleep(0.01)
                with self.temp_monitor.throttle_lock:
                    self.assertAlmostEqual(self.temp_monitor.throttle_time, 0.1)

                time.sleep(0.01)
                with self.temp_monitor.throttle_lock:
                    self.assertAlmostEqual(self.temp_monitor.throttle_time, 0.1)

                time.sleep(0.01)
                with self.temp_monitor.throttle_lock:
                    self.assertAlmostEqual(self.temp_monitor.throttle_time, None)

if __name__ == '__main__':
    unittest.main()