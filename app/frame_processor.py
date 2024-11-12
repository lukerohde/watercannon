# frame_processor.py

import cv2
import ipdb
import numpy as np
import time

class FrameProcessor:
    """
    Processes frames to detect targets, calculate angles, and annotate frames.
    """

    def __init__(self, detector, target_tracker, hardware_controller):
        # config
        self._detector = detector
        self._target_tracker = target_tracker
        self._hardware_controller = hardware_controller
        self._brightness_threshold = 12
        self._uniformity_threshold = 25
        self._frame = None

        # public vars
        self.annotated_frame = None
   
    def process_frame(self, frame):
        """
        Process a single frame.  This does all the work.  Spot a chicken and spray it.
        """
        self._frame = frame
        if self.is_interesting():
            height, width = self._frame.shape[:2]
            detections = self._detector.detect_objects(self._frame)
            self.annotated_frame = detections['frame']

            items = detections['items']
            if items != []:
                self._target_tracker.process_detections(items, width, height)
                self._hardware_controller.process_signals(self._target_tracker)
                self.update_frame()
            else:
                self._target_tracker.nothing_detected()
                target_data = None  # No target detected
                self._hardware_controller.patrol()
            
        else:
            print('sleeping...')
            time.sleep(10)
            return frame
            
    def fire(self):
        return self._target_tracker.fire
             
    def is_interesting(self):
        
        gray = cv2.cvtColor(self._frame, cv2.COLOR_BGR2GRAY)
        average_brightness = np.mean(gray)
        std_dev = np.std(gray)
        
        if average_brightness < self._brightness_threshold or std_dev < self._uniformity_threshold:
            return False
        else:
            return True


    def update_frame(self):
        """
        Draw bounding box, center point, and angle offsets on the frame.
        """
        t = self._target_tracker 
        
        # Draw bounding box and center point
        cv2.rectangle(self.annotated_frame, (int(t.x1), int(t.y1)), (int(t.x2), int(t.y2)), (0, 255, 0), 2)
        
        # Set the circle color based on solenoid state
        circle_color = (0, 0, 255) if t.fire else (0, 255, 0)  # Red if active, Green if not
        cv2.circle(self.annotated_frame, (int(t.target_x), int(t.target_y)), 5, circle_color, -1)

        # Display angle offsets on the frame
        cv2.putText(self.annotated_frame, f'DX: {t.dx:.2f} deg, DY: {t.dy:.2f} deg', (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

        # Display angle offsets on the frame
        cv2.putText(self.annotated_frame, f'Target: {t.target_name()}, Distance: {t.approx_distance():.2f}, Attack Angle: {t.attack_angle()}', (10, 90),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)