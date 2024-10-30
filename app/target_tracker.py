# target_tracker.py

import numpy as np
import time

class TargetTracker:
    """
    Processes detections to find the closest target and calculate angles.
    """

    def __init__(self, fov_horizontal=60.0, fov_vertical=40.0):
        # Tracking configuration
        self._fov_horizontal = fov_horizontal
        self._fov_vertical = fov_vertical
        self._frame_height = None
        self._frame_width = None
        self._detections = None

        # Firing configuration
        self._activation_threshold_angle = 2
        self._firing_events = []
        self._fire_start_time = None
        self._cool_down_time = 3
        self._max_fire_time = 1
        self._cool_down_till = time.time()
        self._target_size_in_range = 0.1

        # Public attributes
        self.target = None
        self.fire = False
        self.dx = 0
        self.dy = 0
        self.target_x = 0
        self.target_y = 0
        self.x1 = None
        self.x2 = None
        self.y1 = None
        self.y2 = None
        self.attack_message = ''

    def process_detections(self, detections, frame_width, frame_height):
        """
        Process detections to update angles.
        """
        self._frame_width = frame_width
        self._frame_height = frame_height
        self._detections = detections

        self.target = self._find_closest_target()
        if self.target:
            self._calculate_angles()
            self._should_i_fire()
            self._log_attack()
        else:
            self._end_fire_event()

    def _find_closest_target(self):
        """
        Find the detection closest to the center of the frame.
        """
        if not self._detections:
            return None

        center_x = self._frame_width / 2
        center_y = self._frame_height / 2

        closest_detection = min(
            self._detections,
            key=lambda det: np.hypot(
                ((det['box']['x1'] + det['box']['x2']) / 2) - center_x,
                ((det['box']['y1'] + det['box']['y2']) / 2) - center_y
            )
        )

        return closest_detection

    def _calculate_angles(self):
        """
        Calculate the angle offsets for the target box.
        """
        box = self.target['box']
        self.x1, self.y1, self.x2, self.y2 = box['x1'], box['y1'], box['x2'], box['y2']

        # Aim directly at the target
        self.target_x = (self.x1 + self.x2) / 2
        self.target_y = (self.y1 + self.y2) / 2

        current_x = self._frame_width / 2
        current_y = self._frame_height / 2
        offset_x = current_x - self.target_x
        offset_y = current_y - self.target_y

        self.dx = self._calculate_angle(offset_x, self._frame_width, self._fov_horizontal)
        self.dy = self._calculate_angle(offset_y, self._frame_height, self._fov_vertical)

    def _should_i_fire(self):
        if self._permitted_to_fire() and self._on_target() and self._close_enough():
            self._start_fire_event()
        else:
            self._end_fire_event()

    def _calculate_angle(self, offset, frame_dimension, fov):
        """
        Calculate the angle offset from the center.
        """
        return (offset / frame_dimension) * (fov / 2)

    def _start_fire_event(self):
        if not self.fire:
            self.fire = True
            self._fire_start_time = time.time()

    def _end_fire_event(self):
        self.attack_message = ''
        if self.fire:
            self.fire = False
            fire_time = self._fire_duration()
            self._firing_events.append({
                'time': self._fire_start_time,
                'duration': fire_time
            })
            self._fire_start_time = None

    def _close_enough(self):
        target_width = abs(self.x2 - self.x1)
        target_height = abs(self.y2 - self.y1)
        percent_width = target_width / self._frame_width
        percent_height = target_height / self._frame_height
        if percent_width >= self._target_size_in_range or percent_height >= self._target_size_in_range:
            return True
        else:
            return False

    def _fire_duration(self):
        return time.time() - self._fire_start_time if self._fire_start_time else 0

    def _on_target(self):
        return abs(self.dx) < self._activation_threshold_angle and abs(self.dy) < self._activation_threshold_angle

    def _permitted_to_fire(self):
        if self._fire_duration() > self._max_fire_time:
            self._cool_down_till = time.time() + self._cool_down_time
            return False

        if time.time() < self._cool_down_till:
            return False

        if self._person_detected():
            return False
        
        return True

    def _person_detected(self):
        return False

    def _log_attack(self):
        target_name = self.target['name']
        if self.fire:
            self.attack_message = f'Firing on {target_name} at dx: {self.dx}, dy: {self.dy}'
        elif not self._close_enough():
            self.attack_message = f'{target_name} out of range at dx: {self.dx}, dy: {self.dy}'
        else:
            self.attack_message = f'Targeting {target_name} at dx: {self.dx}, dy: {self.dy}'

        self._log(self.attack_message)

    def _log(self, message):
        print(message)