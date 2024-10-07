# hardware/mac_hardware.py

from .fake_hardware import FakeHardwareController

class MacHardwareController(FakeHardwareController):
    """
    Mac hardware controller with simulated hardware interactions and debug prints.
    """

    def _update_servos(self):
        """
        Simulate servo angle updates with debug prints.
        """
        print(f"Simulated servo angles: Pan={self.pan_angle}, Tilt={self.tilt_angle}")
        super()._update_servos()

    def _toggle_relay(self):
        """
        Simulate relay toggling with debug prints.
        """
        super()._toggle_relay()
        state = "Activated" if self.relay_on else "Deactivated"
        print(f"Simulated solenoid relay: {state}")

    def cleanup(self):
        """
        Simulate cleanup of resources with debug prints.
        """
        print("Simulated cleanup of hardware resources.")
        super().cleanup()