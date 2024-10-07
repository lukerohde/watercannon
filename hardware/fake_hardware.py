# hardware/fake_hardware.py

from .base_hardware import BaseHardwareController

class FakeHardwareController(BaseHardwareController):
    """
    Fake hardware controller for testing purposes.
    """
    
    def _initialize_hardware(self):
        """
        Initialize fake hardware components.
        """
        self.solenoid_pin = 17
        self.pan_servo_pin = 12
        self.tilt_servo_pin = 13
        self.relay_on = False
        self.pan_angle = 90
        self.tilt_angle = 90
        # No actual hardware initialization

    def _update_servos(self):
        """
        Simulate servo angle updates.
        """
       
    def _toggle_relay(self):
        """
        Simulate relay toggling.
        """
        self.relay_on = not self.relay_on
        
    def cleanup(self):
        """
        Simulate cleanup of resources.
        """
       