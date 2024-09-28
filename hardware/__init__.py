# hardware/__init__.py

import sys
import os
from .base_hardware import BaseHardwareController

def get_hardware_controller(fake=False):
    """
    Factory function to get the appropriate hardware controller based on the platform.
    If fake=True, returns a FakeHardwareController for testing.
    """
    if fake:
        from .fake_hardware import FakeHardwareController
        return FakeHardwareController()
    
    if sys.platform.startswith('linux') and os.uname().machine.startswith('arm'):
        from .pi_hardware import PiHardwareController
        return PiHardwareController()
    else:
        from .mac_hardware import MacHardwareController
        return MacHardwareController()

__all__ = ['BaseHardwareController', 'get_hardware_controller']