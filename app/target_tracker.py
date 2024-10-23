# target_tracker.py

import numpy as np

class TargetTracker:
    """
    Processes detections to find the closest target and calculate angles.
    """

    def __init__(self, fov_horizontal=60.0, fov_vertical=40.0):
        self.fov_horizontal = fov_horizontal
        self.fov_vertical = fov_vertical
        
    def process_detections(self, detections, frame_width, frame_height):
        """
        Process detections to update angles.
        """
        target = self._find_closest_target(detections, frame_width, frame_height)
        if target:
            tracking_data = self._calculate_angles(target, frame_width, frame_height)
            
            return tracking_data
        return None

    def _find_closest_target(self, detections, frame_width, frame_height):
        """
        Find the detection closest to the center of the frame.
        """
        center_x = frame_width / 2
        center_y = frame_height / 2

        if not detections:
            return None

        closest_detection = min(
            detections,
            key=lambda det: np.hypot(
                ((det['box']['x1'] + det['box']['x2']) / 2) - center_x,
                ((det['box']['y1'] + det['box']['y2']) / 2) - center_y
            )
        )

        return closest_detection

    def _calculate_angles(self, detection, frame_width, frame_height):
        """
        Calculate the angle offsets for the target box.
        """
        box = detection['box']
        x1, y1, x2, y2 = box['x1'], box['y1'], box['x2'], box['y2']
        bbox_center_x = (x1 + x2) / 2
        bbox_center_y = (y1 + y2) / 2
        center_x = frame_width / 2
        center_y = frame_height / 2
        offset_x = center_x - bbox_center_x 
        offset_y = center_y - bbox_center_y
        angle_x = self._calculate_angle(offset_x, frame_width, self.fov_horizontal)
        angle_y = self._calculate_angle(offset_y, frame_height, self.fov_vertical)
        
        result = detection.copy()
        result.update({
            'box_center': {'x': bbox_center_x, 'y': bbox_center_y},
            'angle_x': angle_x,
            'angle_y': angle_y,
        })

        return result

    def _calculate_angle(self, offset, frame_dimension, fov):
        """
        Calculate the angle offset from the center.
        """
        return (offset / frame_dimension) * (fov/2) # divided by 2 stops the hunting and works nice.  Not sure why?
