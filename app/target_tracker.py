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
        self._frame_width = 640  # Default
        self._frame_height = 480  # Default
        self._detections = None
        self._aversions = []
        self._aversion_detected_timeout = 5 # seconds
        self._aversion_detected_time = time.time() - self._aversion_detected_timeout # set elapsed

        # Firing configuration
        self._dead_zone_angle = 3
        self._dampen_factor = 0.5 
        self._firing_events = []
        self._fire_start_time = None
        self._cool_down_time = 3
        self._max_fire_time = 1
        self._cool_down_till = time.time()
        self._target_width = 350 #mm used to estimate distance
        self._target_height = 450 #mm
        # distances and angles
        self._attack_angles = { 
            2000: 100,
            2600: 110,
            3100: 120,
            3500: 130,
            3600: 140
        }

        # Public attributes
        self.target = None
        self.fire = False
        self.dx = 0
        self.dy = 0
        self.target_x = 0
        self.target_y = 0
        self.width = None # px 
        self.height = None # px
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

        self.target = self._find_closest_target() # perhaps this should be in self._find_closest_target
        if self.target:
            self._set_dimensions() # perhaps this should be in self._find_closest_target (make testing easier)
            self._calculate_angles()
            self._should_i_fire()
            self._log_attack()
        else:
            self._end_fire_event()

    def process_aversions(self, aversions):
        aversions_names = [ item['name'] for item in aversions ]

        if aversions_names:
            self._aversions = aversions_names
            self._aversion_detected_time = time.time()
            


    def nothing_detected(self):
        self._end_fire_event()

    def _set_dimensions(self):
        box = self.target['box']
        self.x1, self.y1, self.x2, self.y2 = box['x1'], box['y1'], box['x2'], box['y2']
        self.width = abs(self.x2 - self.x1)
        self.height = abs(self.y2 - self.y1)
        self.target_x = (self.x1 + self.x2) / 2
        self.target_y = (self.y1 + self.y2) / 2
            

    def _find_closest_target(self):
        """
        Find the detection closest to the center of the frame.
        """
        if not self._detections:
            return None

        center_x = self._frame_width / 2
        center_y = self._frame_height / 2

        # closest_detection = min(
        #     self._detections,
        #     key=lambda det: np.hypot(
        #         ((det['box']['x1'] + det['box']['x2']) / 2) - center_x,
        #         ((det['box']['y1'] + det['box']['y2']) / 2) - center_y
        #     )
        # )

        closest_detection = max(
            self._detections,
            key=lambda det: (det['box']['x2'] - det['box']['x1']) * (det['box']['y2'] - det['box']['y1'])
        )

        return closest_detection

    def _calculate_angles(self):
        """
        Calculate the angle offsets for the target box.
        """
        # Aim directly at the target
        current_x = self._frame_width / 2
        current_y = self._frame_height / 2
        offset_x = current_x - self.target_x
        offset_y = current_y - self.target_y
        self.dx = self._dampen_factor * self._calculate_angle(offset_x, self._frame_width, self._fov_horizontal)
        self.dy = self._dampen_factor * self._calculate_angle(offset_y, self._frame_height, self._fov_vertical)

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

    def approx_distance(self):
        """
        Approximate distance based upon expected size

        distance = real_world_size * frame_dimension / (size_in_frame * 2 * tan(FOV * 2))
        However, I found the values .94 and 430 empirically - this worked better
        """
        x_dist = (.94 * self._target_width) / (self.width / self._frame_width) - 430
        y_dist = (.94 * self._target_height) / (self.height / self._frame_height) - 430
        return (x_dist + y_dist) / 2
 
    def attack_angle(self):
        """
        Returns the tilt angle for a calculated distance using the lookup table.
        Returns None if the distance exceeds the maximum range.
        """
        distance = self.approx_distance()
        distances = np.array(sorted(self._attack_angles.keys()))
        tilt_angles = np.array([self._attack_angles[d] for d in distances])

        if distance < distances[0]:
            return 0
        elif distance > distances[-1]:
            return None

        return np.interp(distance, distances, tilt_angles)

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
        if self.attack_angle() is None: 
            return False
        else:
            return True

    def _fire_duration(self):
        return time.time() - self._fire_start_time if self._fire_start_time else 0

    def _on_target(self):
        current_x = self._frame_width / 2
        current_y = self._frame_height / 2
        
        return abs(self.dx) < self._dead_zone_angle and current_y < self.y2 # on target horizontally, and above the base of the target - it was too twitch before
        #return self.x1 < current_x and self.x2 > current_x and current_y < self.y2 # in the horizontal bounding box, and above the base of the target
        #return abs(self.dx) < self._dead_zone_angle and abs(self.dy) < self._dead_zone_angle

    def _permitted_to_fire(self):
        if self._fire_duration() > self._max_fire_time:
            self._cool_down_till = time.time() + self._cool_down_time
            return False

        if time.time() < self._cool_down_till:
            return False

        if self._aversion_detected():
            return False
        
        return True

    def _aversion_detected(self):
        if time.time() < self._aversion_detected_time + self._aversion_detected_timeout:
            return True

        return False
        

    def target_name(self):
        return self.target.get('name', 'Unknown Target')

    def _log_attack(self):
        target_name = self.target_name()
        if self.fire:
            self.attack_message = f'Firing on {target_name} at dx: {self.dx}, dy: {self.dy}, distance: {self.approx_distance()}, angle: {self.attack_angle()}, width: {self.width}, height: {self.height}'
        elif self._aversions:
            self.attack_message = f'{self._aversions} detected.  Avoiding firing on {target_name} at dx: {self.dx}, dy: {self.dy}, distance: {self.approx_distance()}, angle: {self.attack_angle()}, width: {self.width}, height: {self.height}'
        elif not self._close_enough():
            self.attack_message = f'{target_name} out of range at dx: {self.dx}, dy: {self.dy}, distance: {self.approx_distance()}, angle: {self.attack_angle()}, width: {self.width}, height: {self.height}'
        else:
            self.attack_message = f'Targeting {target_name} at dx: {self.dx}, dy: {self.dy}, distance: {self.approx_distance()}, angle: {self.attack_angle()}, width: {self.width}, height: {self.height}'

        self._log(self.attack_message)

    def _log(self, message):
        print(message)