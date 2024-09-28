# hardware/base_hardware.py

from abc import ABC, abstractmethod

class BaseHardwareController(ABC):
    """
    Abstract base class for hardware controllers.
    """

    @abstractmethod
    def process_signals(self, signals):
        """Process signals to control hardware components."""
        pass

    @abstractmethod
    def cleanup(self):
        """Clean up hardware resources."""
        pass
