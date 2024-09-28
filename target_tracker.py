# target_tracker.py

import numpy as np

class TargetTracker:
    """
    Processes detections to find the closest target and calculate angles.
    """

    def __init__(self, fov_horizontal=60.0, fov_vertical=40.0):
        self.fov_horizontal = fov_horizontal
        self.fov_vertical = fov_vertical
        self.servo_angle_x = 90.0  # Assuming center is 90 degrees
        self.servo_angle_y = 90.0

    def process_detections(self, detections, frame_width, frame_height):
        """
        Process detections to update angles.

        Args:
            detections: List of detection dicts.
            frame_width: Width of the frame.
            frame_height: Height of the frame.

        Returns:
            dict: Tracking data with angles and bbox info.
        """
        target = self._find_closest_target(detections, frame_width, frame_height)
        if target:
            tracking_data = self._calculate_angles(target, frame_width, frame_height)
            
            return tracking_data
        return None

    def _find_closest_target(self, detections, frame_width, frame_height):
        """
        Find the detection closest to the center of the frame.

        Args:
            detections: List of target detections.
            frame_width: Width of the frame.
            frame_height: Height of the frame.

        Returns:
            dict: The detection closest to the center.
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

        Args:
            detection: Detection dict with 'box'.
            frame_width: Width of the frame.
            frame_height: Height of the frame.

        Returns:
            dict: Dictionary containing angles and bounding box data.
        """
        box = detection['box']
        x1, y1, x2, y2 = box['x1'], box['y1'], box['x2'], box['y2']
        bbox_center_x = (x1 + x2) / 2
        bbox_center_y = (y1 + y2) / 2
        center_x = frame_width / 2
        center_y = frame_height / 2
        offset_x = bbox_center_x - center_x
        offset_y = bbox_center_y - center_y
        angle_x = self._calculate_angle(offset_x, frame_width, self.fov_horizontal)
        angle_y = self._calculate_angle(offset_y, frame_height, self.fov_vertical)
        self._update_servos(angle_x, angle_y)
        
        result = detection.copy()
        result.update({
            'box_center': {'x': bbox_center_x, 'y': bbox_center_y},
            'angle_x': angle_x,
            'angle_y': angle_y,
            'servo_angle_x': self.servo_angle_x,
            'servo_angle_y': self.servo_angle_y
        })

        return result

    def _calculate_angle(self, offset, frame_dimension, fov):
        """
        Calculate the angle offset from the center.

        Args:
            offset (float): The offset from the center in pixels.
            frame_dimension (int): The frame dimension (width or height) in pixels.
            fov (float): The field of view in degrees.

        Returns:
            float: The angle offset in degrees.
        """
        return (offset / frame_dimension) * fov


    def _update_servos(self, angle_x_delta, angle_y_delta):
        """
        Update the current angles based on delta.

        Args:
            angle_x_delta (float): Change in x angle.
            angle_y_delta (float): Change in y angle.
        """
        self.servo_angle_x = np.clip(self.servo_angle_x + angle_x_delta, 0, 180)
        self.servo_angle_y = np.clip(self.servo_angle_y + angle_y_delta, 0, 180)

