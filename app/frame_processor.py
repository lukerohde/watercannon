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
        self.detector = detector
        self.target_tracker = target_tracker
        self.hardware_controller = hardware_controller
        self.brightness_threshold = 12
        self.uniformity_threshold = 25
   
    def process_frame(self, frame):
        """
        Process a single frame.  This does all the work.  Spot a chicken and spray it.
        """
        if self.is_interesting(frame):
            frame_copy = frame.copy() # this doesn't work and deep copy didn't either (fake_frame was being over written)
            height, width = frame_copy.shape[:2]
            detections = self.detector.detect_objects(frame_copy)
            annotated_frame = detections['frame']
            items = detections['items']

            if items != []:
                target_data = self.target_tracker.process_detections(items, width, height)
                self.hardware_controller.process_signals(target_data)
                self.update_frame(annotated_frame, target_data)
            else:
                target_data = None  # No target detected
                self.hardware_controller.patrol()
            
            return annotated_frame
        else:
            print('sleeping...')
            time.sleep(10)
            return frame
            
            

    def is_interesting(self,frame):

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        average_brightness = np.mean(gray)
        std_dev = np.std(gray)
        
        if average_brightness < self.brightness_threshold or std_dev < self.uniformity_threshold:
            return False
        else:
            return True


    def update_frame(self, frame, data):
        """
        Draw bounding box, center point, and angle offsets on the frame.
        """
        x1, y1, x2, y2 = data['box'].values()
        box_center_x, box_center_y = data['box_center'].values()
        angle_x = data['angle_x']
        angle_y = data['angle_y']

        # Draw bounding box and center point
        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        
        # Set the circle color based on solenoid state
        circle_color = (0, 0, 255) if data['relay_on'] else (0, 255, 0)  # Red if active, Green if not
        cv2.circle(frame, (int(box_center_x), int(box_center_y)), 5, circle_color, -1)

        # Display angle offsets on the frame
        cv2.putText(frame, f'Angle X: {angle_x:.2f} deg', (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        cv2.putText(frame, f'Angle Y: {angle_y:.2f} deg', (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)