# frame_store.py

import threading
import time

class FrameStore:
    """Thread-safe store for the latest processed frame."""
    
    def __init__(self):
        self.lock = threading.Lock()
        self.latest_frame = None
        self.timestamp = 0
        self.condition = threading.Condition(self.lock)
        self.is_running = True

    def update(self, frame):
        """Update the latest frame and notify waiting threads."""
        with self.condition:
            self.latest_frame = frame
            self.timestamp = time.time()
            self.condition.notify_all()

    def get_latest(self, last_timestamp):
        """Retrieve the latest frame newer than last_timestamp."""
        with self.condition:
            while self.timestamp <= last_timestamp and self.is_running:
                self.condition.wait()
            return self.latest_frame, self.timestamp

    def stop(self):
        """Signal that frame processing has stopped."""
        with self.condition:
            self.is_running = False
            self.condition.notify_all()