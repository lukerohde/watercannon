# camera/base_camera.py

class BaseCamera:
    """
    Abstract base class for camera implementations.
    """

    def frame_generator(self):
        raise NotImplementedError("Must be implemented by subclass.")

    def release(self):
        raise NotImplementedError("Must be implemented by subclass.")