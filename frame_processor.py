# frame_processor.py

import cv2
import ipdb

class FrameProcessor:
    """
    Processes frames to detect targets, calculate angles, and annotate frames.
    """

    def __init__(self, detector, target_tracker, hardware_controller):
        self.detector = detector
        self.target_tracker = target_tracker
        self.hardware_controller = hardware_controller
   
    def process_frame(self, frame):
        """
        Process a single frame.

        Args:
            frame: Input frame.

        Returns:
            dict: Contains annotated frame.
        """
        height, width = frame.shape[:2]
        detections = self.detector.detect_objects(frame)
        annotated_frame = detections['frame']
        items = detections['items']

        if items != []:
            target = self.target_tracker.process_detections(items, width, height)
            self.update_frame(annotated_frame, target)
            self.hardware_controller.process_signals(target)
        else:
            target = None  # No target detected

        return {
            'annotated_frame': annotated_frame
        }

    def update_frame(self, frame, data):
        """
        Draw bounding box, center point, and angle offsets on the frame.

        Args:
            frame: Frame to draw on.
            data: Dictionary containing angle and bounding box data.
        """
        x1, y1, x2, y2 = data['box'].values()
        box_center_x, box_center_y = data['box_center'].values()
        angle_x = data['angle_x']
        angle_y = data['angle_y']

        # Draw bounding box and center point
        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        cv2.circle(frame, (int(box_center_x), int(box_center_y)), 5, (0, 255, 0), -1)

        # Display angle offsets on the frame
        cv2.putText(frame, f'Angle X: {angle_x:.2f} deg', (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        cv2.putText(frame, f'Angle Y: {angle_y:.2f} deg', (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)