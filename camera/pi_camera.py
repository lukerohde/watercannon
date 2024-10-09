# camera/pi_camera.py

from picamera2 import Picamera2
from libcamera import Transform
import numpy as np
import cv2
from .base_camera import BaseCamera
import ipdb

class PiCamera(BaseCamera):
    """
    Camera implementation for Raspberry Pi using Picamera2.
    """

    def __init__(self):
        # Initialize Picamera2
        self.picam2 = Picamera2()
        # Configure the camera for a preview stream with the desired resolution
        # "size":(640,480), 
        config = self.picam2.create_video_configuration(main={"format": "RGB888"}, transform=Transform(hflip = False, vflip = True))
        self.picam2.configure(config)
        # Start the camera
        self.picam2.start()

    def frame_generator(self):
        """
        Generator that yields frames from the camera.
        """
        frame_count = 0
        while True:
            # Capture a frame as a NumPy array
            frame = self.picam2.capture_array()

            # Print frame count on the same line
            print(f"Frame count: {frame_count}", end='\r', flush=True)
            frame_count += 1

            yield frame

    def release(self):
        self.picam2.stop()
