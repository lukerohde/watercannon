# app.py

from flask import Flask, Response
from app.frame_store import FrameStore
import cv2
import time
import threading 

from camera.fake_camera import FakeCamera
from camera import get_camera
from hardware import get_hardware_controller
from app.detector import Detector
from app.frame_processor import FrameProcessor
from app.target_tracker import TargetTracker


def create_app(camera, hardware_controller, frame_processor):
    """Create and configure the Flask app with injected dependencies."""
    app = Flask(__name__)
    frame_store = FrameStore()

    def frame_processing():
        """Continuously process frames and update the FrameStore."""
        try:
            for frame in camera.frame_generator():
                #frame_store.update(frame)
                annotated_frame = frame_processor.process_frame(frame)
                frame_store.update(annotated_frame)

        finally:
            """If the camera runs out of frames or dies let the 
            FrameStore know the stream has stopped"""
            camera.release()
            frame_store.stop()
            hardware_controller.cleanup()

    threading.Thread(target=frame_processing, daemon=True).start()

    def generate_frames():
        """Generator that yields the latest frame from the FrameStore to clients."""
        last_timestamp = 0
        while True:
            frame, ts = frame_store.get_latest(last_timestamp)
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
            if not frame_store.is_running:
                break

    @app.route('/')
    def index():
        """Streaming route that serves the video feed."""
        return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

    return app

def main():
    # Initialize dependencies
    # camera = get_camera(fake=True, frames=[FakeCamera.fake_frame])
    camera = get_camera()
    hardware_controller = get_hardware_controller()
    detector = Detector(model_name='yolov10n', target_class='person')
    target_tracker = TargetTracker(fov_horizontal=60, fov_vertical=40)
    frame_processor = FrameProcessor(detector, target_tracker, hardware_controller)

    # Create and run the Flask app
    app = create_app(camera, hardware_controller, frame_processor)
    app.run(host='0.0.0.0', port=3000, debug=True, threaded=True, use_reloader=False)

if __name__ == '__main__':
    main()