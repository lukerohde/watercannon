# camera/mac_camera.py

import cv2
from .base_camera import BaseCamera
import time

class MacCamera(BaseCamera):
    """
    Camera implementation for macOS.
    """

    def __init__(self):
        self.camera = cv2.VideoCapture(0)
        if not self.camera.isOpened():
            raise IOError("Cannot open webcam")

    def frame_generator(self):
        """
        Generator that yields frames from the camera.
        """
        while True:
            ret, frame = self.camera.read()
            if not ret:
                break
            yield frame

    def release(self):
        """
        Release the camera resources.
        """
        self.camera.release()