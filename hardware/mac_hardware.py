# hardware/mac_hardware.py

from .base_hardware import BaseHardwareController

class MacHardwareController(BaseHardwareController):
    """
    Mock hardware controller for macOS.
    """

    def process_signals(self, signals):
        """
        Simulate hardware activation.
        """
        print("Hardware activation simulated with signals:", signals)

    def cleanup(self):
        """
        No cleanup needed for mock controller.
        """
        pass
