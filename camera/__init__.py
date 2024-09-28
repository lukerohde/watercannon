# camera/__init__.py

import sys
import os
from .base_camera import BaseCamera

def get_camera(fake=False, frames=None):
    """
    Factory function to get the appropriate camera implementation based on the platform.
    If fake=True, returns a FakeCamera for testing.
    """
    if fake:
        from .fake_camera import FakeCamera
        return FakeCamera(frames=frames)
    
    if sys.platform.startswith('linux') and os.uname().machine.startswith('arm'):
        from .pi_camera import PiCameraImpl
        return PiCameraImpl()
    else:
        from .mac_camera import MacCamera
        return MacCamera()

__all__ = ['BaseCamera', 'get_camera']