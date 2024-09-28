# camera/pi_camera.py

from picamera.array import PiRGBArray
from picamera import PiCamera
from .base_camera import BaseCamera

class PiCamera(BaseCamera):
    """
    Camera implementation for Raspberry Pi.
    """

    def __init__(self):
        self.camera = PiCamera()
        self.camera.resolution = (640, 480)
        self.raw_capture = PiRGBArray(self.camera, size=self.camera.resolution)
        self.stream = self.camera.capture_continuous(
            self.raw_capture, format="bgr", use_video_port=True
        )

    def frame_generator(self):
        """
        Generator that yields frames from the camera.
        """
        for f in self.stream:
            frame = f.array
            self.raw_capture.truncate(0)
            yield frame

    def release(self):
        """
        Release the camera resources.
        """
        self.camera.close()