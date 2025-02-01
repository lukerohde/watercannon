#!/usr/bin/env python3

import numpy as np
from .base_camera import BaseCamera
import cv2
import os

class FakeCamera(BaseCamera):
    """
    Fake camera implementation for testing purposes.
    """

    def fake_frame():
        """
        Class helper method used for testing
        """
        # Get absolute path to test image
        image_path = os.path.join(os.path.dirname(__file__), '..', 'tests', 'chicken_missing.jpg')
        image_data = cv2.imread(image_path)
        if image_data is None:
            # If image not found, return a test pattern
            height, width = 480, 640
            image_data = np.random.randint(100, 256, (height, width, 3), dtype=np.uint8)
        return image_data

    def __init__(self, frames=None):
        """
        Initialize with a list of frames to yield.
        If no frames are provided, yield a default black frame.
        """
        self.fake_frame = FakeCamera.fake_frame()

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
            self.index += 1  # Increment index to get next frame
        
        # Reset index for next iteration
        self.index = 0

    def release(self):
        """
        Fake release method.
        """
        pass
