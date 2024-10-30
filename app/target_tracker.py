# target_tracker.py

import numpy as np
import time

class TargetTracker:
    """
    Processes detections to find the closest target and calculate angles.
    """

    def __init__(self, fov_horizontal=60.0, fov_vertical=40.0):
        self.fov_horizontal = fov_horizontal
        self.fov_vertical = fov_vertical

        # firing event stuff #TODO move this into target tracker (probably)
        self.activation_threshold_angle = 2
        self.firing_events = []
        self.fire_start_time = None
        self.cool_down_time = 3
        self.max_fire_time = 1
        self.cool_down_till = time.time()
        self.fired = False
        self.target_size_in_range = 0.1
        
    def process_detections(self, detections, frame_width, frame_height):
        """
        Process detections to update angles.
        """
        tracking_data = None
        target = self._find_closest_target(detections, frame_width, frame_height)
        if target:
            tracking_data = self._calculate_angles(target, frame_width, frame_height)
            tracking_data = self._fire(tracking_data, frame_width, frame_height)
        
        return tracking_data

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
            'dx': angle_x,
            'dy': angle_y,
        })

        return result

    def _fire(self, tracking_data, frame_width, frame_height):
        tracking_data['fire'] = 0
        if self._permitted_to_fire() and self._on_target(tracking_data['dx'], tracking_data['dy']) and self._close_enough(tracking_data, frame_width, frame_height): 
            tracking_data['fire'] = 1
            self._start_fire_event()
        else:
            tracking_data['fire'] = 1
            self._end_fire_event()

        return tracking_data

    def _calculate_angle(self, offset, frame_dimension, fov):
        """
        Calculate the angle offset from the center.
        """
        return (offset / frame_dimension) * (fov/2) # divided by 2 stops the hunting and works nice.  Not sure why?

    def _start_fire_event(self):
        self.fired = True
        self.fire_start_time = time.time()
    
    def _end_fire_event(self):
        self.fired = False
        fire_time = self._fire_duration()
        self.firing_events.append({
            'time': self.fire_start_time,
            'duration': fire_time
        })
        self.fire_start_time = None

    def _close_enough(self, tracking_data, frame_width, frame_height):
        target_width = abs(tracking_data['box']['x2'] -  tracking_data['box']['x1'])
        target_height = abs(tracking_data['box']['y2'] -  tracking_data['box']['y1'])
        percent_width = target_width / frame_width 
        percent_height = target_height / frame_height
        if percent_width > self.target_size_in_range or percent_height > self.target_size_in_range:
            return True
        else:
            return False

    def _fire_duration(self):
        return time.time() - self.fire_start_time if self.fire_start_time else 0

    def _on_target(self, dx, dy):
        return abs(dx) < self.activation_threshold_angle and abs(dy) < self.activation_threshold_angle
    
    def _permitted_to_fire(self):
        if self._fire_duration() > self.max_fire_time:
            self.cool_down_till = time.time() + self.cool_down_time
            return False

        if time.time() < self.cool_down_till:
            return False
        
        if self._person_detected():
            return False

        return True

    def _person_detected(self):
        return False
