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
        self._relay_on = False
        self._pan_angle = 90
        self._tilt_angle = 90
        # No actual hardware initialization

    def _update_servos(self):
        """
        Simulate servo angle updates.
        """
        pass
       
    def _toggle_relay(self):
        """
        Simulate relay toggling.
        """
        self._relay_on = not self._relay_on
        
    def cleanup(self):
        """
        Simulate cleanup of resources.
        """
        pass
       