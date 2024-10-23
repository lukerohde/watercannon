# app/main.py

from flask import Flask, Response
import cv2
import threading
import time

from camera.fake_camera import FakeCamera
from camera import get_camera
from hardware import get_hardware_controller
from app.detector import Detector
from app.frame_processor import FrameProcessor
from app.target_tracker import TargetTracker
from app.frame_store import FrameStore
from app.temperature_monitor import TemperatureMonitor

class App:
    def __init__(self, camera, hardware_controller, frame_processor, temp_monitor):
        """Initialize the App with injected dependencies."""
        self.camera = camera
        self.hardware_controller = hardware_controller
        self.frame_processor = frame_processor
        self.frame_store = FrameStore() # I'm deliberately not injecting this, because I have no test isolation yet, and am using my test_main as a mini integration test
        self.app = Flask(__name__)
        self.thread = None
        self.is_running = False
        self.temp_monitor = temp_monitor  


        self._setup_routes()

    def run(self, host='0.0.0.0', port=3000, debug=True):
        """Run the Flask app."""
        self.start_processing()
        self.app.run(host=host, port=port, debug=debug, threaded=True, use_reloader=False)
    
    def start_processing(self):
        """Start the frame processing thread."""
        if not self.is_running:
            self.temp_monitor.start()
            self.thread = threading.Thread(target=self._frame_processing, daemon=True)
            self.thread.start()
            

    def stop_processing(self):
        """Stop the frame processing thread."""
        if self.is_running:
            self.is_running = False
            self.temp_monitor.stop()
            self.thread.join() # Wait for frame processing thread to finish
            self._clean_up()
    
    def _setup_routes(self):
        """Set up Flask routes."""
        @self.app.route('/')
        def index():
            """Streaming route that serves the video feed."""
            return Response(self._generate_streaming_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
    
    def _generate_streaming_frames(self):
        """Generator that yields the latest frame from the FrameStore to clients."""
        last_timestamp = 0
        while True:
            self.temp_monitor.throttle()

            frame, ts = self.frame_store.get_latest(last_timestamp)
            if frame is not None:
                ret, buffer = cv2.imencode('.jpg', frame)
                if ret:
                    frame_bytes = buffer.tobytes()
                    yield (
                        b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' +
                        frame_bytes + b'\r\n'
                    )
                    last_timestamp = ts
                
            if not self.frame_store.is_running:
                break

    def _frame_processing(self):
        """Continuously process frames and update the FrameStore."""
        try:
            self.is_running = True
            for frame in self.camera.frame_generator():
                self.temp_monitor.throttle()

                annotated_frame = self.frame_processor.process_frame(frame)
                self.frame_store.update(annotated_frame)
                
                if not self.is_running:
                    break
                
            
        finally:
            """If the camera runs out of frames or dies, let the FrameStore know the stream has stopped."""
            self.is_running = False
            self._clean_up() 
    
    def _clean_up(self):
        self.camera.release()
        self.frame_store.stop()
        self.hardware_controller.cleanup()


def main():
    # Initialize dependencies
    camera = get_camera()
    hardware_controller = get_hardware_controller()
    detector = Detector(model_name='yolov10n', target_classes=['cow', 'bird', 'cat', 'dog'])
    target_tracker = TargetTracker(fov_horizontal=130, fov_vertical=102)
    frame_processor = FrameProcessor(detector, target_tracker, hardware_controller)
    temp_monitor = TemperatureMonitor(stable_threshold=78, max_threshold=82)

    # Instantiate the App
    app_instance = App(camera, hardware_controller, frame_processor, temp_monitor)

    # Run the app
    try:
        app_instance.run()
    except KeyboardInterrupt:
        app_instance.stop_processing()


if __name__ == '__main__':
    main()