# app.py

from flask import Flask, Response
from camera import get_camera
from detector import Detector
from frame_processor import FrameProcessor
from hardware import get_hardware_controller
from target_tracker import TargetTracker
import cv2

def create_app(camera, hardware_controller, frame_processor):
    """
    Factory function to create and configure the Flask app.
    Allows injecting fake components for testing.
    """
    app = Flask(__name__)
    
    def generate_frames():
        """
        Generate frames for streaming, including detection and annotations.
    
        Yields:
            bytes: Encoded frame bytes
        """
        frame_gen = camera.frame_generator()
        try:
            for frame in frame_gen:
                # Process frame and get results
                result = frame_processor.process_frame(frame)
    
                # Get the annotated frame
                annotated_frame = result['annotated_frame']
    
                # Encode the frame in JPEG format
                ret, buffer = cv2.imencode('.jpg', annotated_frame)
                frame_bytes = buffer.tobytes()
    
                # Yield the output frame in byte format
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        finally:
            camera.release()
    
    @app.route('/')
    def index():
        """
        Streaming page route.
        """
        return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
    
    return app

if __name__ == '__main__':
    # Run the Flask app
    camera = get_camera()
    hardware_controller = get_hardware_controller()

    detector = Detector(model_name='yolov10n', target_class='bird')
    target_tracker = TargetTracker(fov_horizontal=60, fov_vertical=40)
    frame_processor = FrameProcessor(detector, target_tracker, hardware_controller)
    
    app = create_app(camera, hardware_controller, frame_processor)
    app.run(host='0.0.0.0', port=3000, debug=True)

