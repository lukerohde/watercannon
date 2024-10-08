# camera/fake_camera.py

import numpy as np
from .base_camera import BaseCamera

class FakeCamera(BaseCamera):
    """
    Fake camera implementation for testing purposes.
    """

    def fake_frame():
        """
        Class helper method used for testing
        """
        return np.zeros((480, 640, 3), dtype=np.uint8)

    def __init__(self, frames=None):
        """
        Initialize with a list of frames to yield.
        If no frames are provided, yield a default black frame.
        """
        if frames is None:
            self.frames = [self.fake_frame]
        else:
            self.frames = frames
        self.index = 0

    def frame_generator(self):
        """
        Generator that yields predefined frames.
        """
        while self.index < len(self.frames):
            yield self.frames[self.index]
            self.index += 1

    def release(self):
        """
        Fake release method.
        """
        pass
