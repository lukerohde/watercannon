# app/frame_store.py

import threading
import time
import cv2 
from collections import deque


class FrameStore:
    """Thread-safe store for the latest processed frame."""
    
    def __init__(self, video_snapshot_seconds=10):
        self.lock = threading.Lock()
        self.latest_frame = None
        self.timestamp = 0
        self.condition = threading.Condition(self.lock)
        self.is_running = True

        # Video stuff - TBD, this class is doing two things, consider splitting
        self.video_snapshot_seconds = video_snapshot_seconds
        self.video = deque()
        self.saving = False
        self.saving_stop_event = threading.Event()
        self.save_thread = None
        self.save_lock = threading.Lock()


    def update(self, frame):
        """Update the latest frame and notify waiting threads."""
        with self.condition:
            self.latest_frame = frame
            self.timestamp = time.time()
            
            with self.save_lock:
                self.video.append({
                    'frame': frame, 
                    'ts': self.timestamp
                })
                if not self.saving:
                    # keep video while we're saving, so we always keep the buffer leading up to the save event
                    self._drop_old_video()

            self.condition.notify_all()

    def get_latest(self, last_timestamp):
        """Retrieve the latest frame newer than last_timestamp."""
        with self.condition:
            while self.timestamp <= last_timestamp and self.is_running:
                self.condition.wait()

            return self.latest_frame, self.timestamp
            
    def stop(self):
        """Signal that frame processing has stopped."""
        self._stop_saving()
        self.is_running = False
        self.condition.notify_all()

    def save(self):
        """
        Starts a background thread to periodically clean up old frames.
        """
        save_time = time.time() + (self.video_snapshot_seconds / 2)

        # if we have a thread waiting to save, restart it
        # so we only save one video when several events happen close together
        self._stop_saving()
        
        self.save_thread = threading.Thread(
            target=self._delay_save,
            args=(save_time,),
            daemon=True
        )
        self.save_thread.start()

    def _drop_old_video(self):
        """
        Removes frames older than 'video_snapshot_seconds' from self.video using deque.
        """
        current_time = time.time()
        cutoff = current_time - (self.video_snapshot_seconds / 2)

        while self.video and self.video[0]['ts'] < cutoff:
            self.video.popleft()

    def _delay_save(self, save_time):
        """
        Waits till save_time before saving, so we get a little bit of video before and after the save event
        """
        with self.save_lock:
            self.saving = True
        
        while True:
            if time.time() > save_time:
                with self.save_lock:
                    self._save_video()
                    self.saving = False
                break
            if self.saving_stop_event.is_set():
                break
            else:
                time.sleep(0.5)

    def _save_video(self):
        """Save the collected frames to a video file."""
        if len(self.video) < 2:
            # need at least two frames for a video
            return
        
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"fire_event_{timestamp}.mp4"
        height, width, layers = self.video[0]['frame'].shape
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(filename, fourcc, self._frame_rate(), (width, height))
        
        for frame in self.video:
            out.write(frame['frame'])
        out.release()
        print(f"Saved video: {filename}")

    def _frame_rate(self): 
        duration = self.video[-1]['ts'] - self.video[0]['ts']
        return len(self.video) / duration
    
    def _stop_saving(self):
        if self.save_thread and self.save_thread.is_alive():
            self.saving_stop_event.set()
            self.save_thread.join()
            self.saving_stop_event.clear()