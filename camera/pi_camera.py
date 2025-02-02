# camera/pi_camera.py

from picamera2 import Picamera2
from libcamera import Transform
import numpy as np
import cv2
from .base_camera import BaseCamera
import time

class PiCamera(BaseCamera):
    """
    Camera implementation for Raspberry Pi using Picamera2.
    """

    def __init__(self):
        # Initialize Picamera2
        self.picam2 = Picamera2()
        
        # Retrieve full sensor resolution and bit depth
        # Typically, Raspberry Pi Camera Module v2 has 4056x3040 resolution and 12-bit depth
        full_sensor_size = (4056, 3040)
        bit_depth = 12

        # Create video configuration with scaling
        config = self.picam2.create_video_configuration(
            sensor={
                'output_size': full_sensor_size,
                'bit_depth': bit_depth
            },
            main={
                'format': 'RGB888',
                'size': (640, 480)
            },
            transform=Transform(hflip=True, vflip=True)
        )

        self.picam2.configure(config)

        # # Set exposure mode to 'night' or 'backlight' to improve dark areas
        # self.picam2.set_controls({"ExposureTime": 10000,  # Example: 10ms exposure
        #                           "AnalogueGain": 2.0,  # Adjust ISO equivalent gain
        #                           "AeEnable": True,     # Enable automatic exposure
        #                           "ExposureValue": 1.0})  # Bias to make image brighter

        # # prioritize the deck (lower half) using ROI
        # self.picam2.set_controls({
        #     "ScalerCrop": (0, full_sensor_size[1] // 2, full_sensor_size[0], full_sensor_size[1] // 2)
        # })
        
        # Start the camera
        self.picam2.start()

    def frame_generator(self):
        """
        Generator that yields frames from the camera.
        """
        frame_count = 0
        t = time.time()
        while True:
            # Capture a frame as a NumPy array
            frame = self.picam2.capture_array()

            # Print frame rate on the same line
            if time.time() - t >= 5:
                print(f"FPS: {frame_count/5}", end='\r', flush=True)
                t = time.time()
                frame_count = 0
            
            frame_count += 1

            yield frame

    def release(self):
        self.picam2.stop()
