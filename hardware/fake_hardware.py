# hardware/fake_hardware.py

from .base_hardware import BaseHardwareController

class FakeHardwareController(BaseHardwareController):
    """
    Fake hardware controller for testing purposes.
    """
    def __init__(self):
        self.activated = False
        self.signals = None

    def process_signals(self, signals):
        """
        Simulate hardware activation by storing the signals.
        """
        self.signals = signals
        self.activated = True

    def cleanup(self):
        """
        Fake cleanup method.
        """
        self.activated = False