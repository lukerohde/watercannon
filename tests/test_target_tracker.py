# test_target_tracker.py

import unittest
from unittest.mock import patch
from app.target_tracker import TargetTracker
import time

class TargetTrackerTestCase(unittest.TestCase):

    def setUp(self):
        # Sample frame dimensions
        self.frame_width = 1000
        self.frame_height = 1000

        # Sample detections
        self.detections = [
            {'name': 'bird', 'class': 14, 'confidence': 0.95, 'box': {'x1': 100, 'y1': 100, 'x2': 200, 'y2': 200}},  # Center: (150, 150)
            {'name': 'bird', 'class': 14, 'confidence': 0.80, 'box': {'x1': 400, 'y1': 400, 'x2': 500, 'y2': 500}},  # Center: (450, 450)
            {'name': 'bird', 'class': 14, 'confidence': 0.75, 'box': {'x1': 850, 'y1': 850, 'x2': 950, 'y2': 950}},  # Center: (925, 925)
            {'name': 'bird', 'class': 14, 'confidence': 0.85, 'box': {'x1': 450, 'y1': 450, 'x2': 550, 'y2': 550}},   # Center: (500, 500)
        ]

    def test_process_detections_no_detections(self):
        tracker = TargetTracker()
        tracker.process_detections([], self.frame_width, self.frame_height)
        self.assertIsNone(tracker.target)
        self.assertFalse(tracker.fire)
        self.assertEqual(tracker.attack_message, '')

    def test_process_detections_with_detections(self):
        tracker = TargetTracker()
        with patch.object(tracker, '_log'):        
            tracker.process_detections(self.detections[2:3], self.frame_width, self.frame_height)
            self.assertIsNotNone(tracker.target)
            self.assertEqual(tracker.target['box']['x1'], 850)
            self.assertTrue(tracker.attack_message.startswith('Targeting'))

    def test_process_detections_not_close_enough(self):
        tracker = TargetTracker()
        detections = [{'name': 'bird', 'class': 14, 'confidence': 0.95, 'box': {'x1': 490, 'y1': 490, 'x2': 500, 'y2': 500}}]
        with patch.object(tracker, '_log'):    
            tracker.process_detections(detections, self.frame_width, self.frame_height)
            self.assertFalse(tracker.fire)
            self.assertTrue(tracker.attack_message.startswith('bird out of range'))
            self.assertIsNone(tracker._fire_start_time)
    
    def test_find_closest_target(self):
        tracker = TargetTracker()
        tracker._frame_width = self.frame_width
        tracker._frame_height = self.frame_height
        tracker._detections = self.detections
        closest = tracker._find_closest_target()
        self.assertEqual(closest['box']['x1'], 450)
        self.assertEqual(closest['box']['y1'], 450)

    def test_calculate_angles(self):
        tracker = TargetTracker()
        tracker._frame_width = self.frame_width
        tracker._frame_height = self.frame_height
        tracker.target = self.detections[-1]
        tracker._calculate_angles()
        self.assertAlmostEqual(tracker.dx, 0.0)
        self.assertAlmostEqual(tracker.dy, 0.0)

    def test_calculate_angles_offset(self):
        tracker = TargetTracker()
        tracker._frame_width = self.frame_width
        tracker._frame_height = self.frame_height
        tracker.target = self.detections[0]  # Center at (150, 150)
        tracker._calculate_angles()
        expected_dx = ((500 - 150) / 1000) * (tracker._fov_horizontal / 2)
        expected_dy = ((500 - 150) / 1000) * (tracker._fov_vertical / 2)
        self.assertAlmostEqual(tracker.dx, expected_dx)
        self.assertAlmostEqual(tracker.dy, expected_dy)

    def test_should_i_fire(self):
        tracker = TargetTracker()
        tracker._frame_width = self.frame_width
        tracker._frame_height = self.frame_height
        tracker.target = self.detections[-1]  # Center at (500, 500)
        tracker._calculate_angles()
        # Ensure target is close enough and on target
        tracker.x1, tracker.y1, tracker.x2, tracker.y2 = 450, 450, 550, 550  # Target size 100x100 pixels
        tracker._should_i_fire()
        self.assertTrue(tracker.fire)

    def test_permitted_to_fire(self):
        tracker = TargetTracker()
        tracker._fire_start_time = time.time() - 2  # Fire duration exceeds max_fire_time
        self.assertFalse(tracker._permitted_to_fire())

        # cool down time should be set
        tracker._fire_start_time = None  # Fire duration exceeds max_fire_time
        self.assertFalse(tracker._permitted_to_fire())
        
        tracker._cool_down_till = time.time() - 1
        r = tracker._permitted_to_fire()
        
        self.assertTrue(r)

    def test_fire_duration(self):
        tracker = TargetTracker()
        self.assertEqual(tracker._fire_duration(), 0)
        tracker._fire_start_time = time.time() - 1
        self.assertAlmostEqual(tracker._fire_duration(), 1, delta=0.1)

    def test_on_target(self):
        tracker = TargetTracker()
        tracker.dx = 1
        tracker.dy = 1
        self.assertTrue(tracker._on_target())
        tracker.dx = 3
        tracker.dy = 1
        self.assertFalse(tracker._on_target())

    def test_close_enough(self):
        tracker = TargetTracker()
        tracker._frame_width = self.frame_width
        tracker._frame_height = self.frame_height
        tracker.x1, tracker.y1, tracker.x2, tracker.y2, tracker.width, tracker.height = 0, 0, 99, 99, 99, 99
        self.assertFalse(tracker._close_enough())
        tracker.x1, tracker.y1, tracker.x2, tracker.y2, tracker.width, tracker.height = 0, 0, 200, 200, 200, 200
        self.assertTrue(tracker._close_enough())

    def test_end_fire_event(self):
        tracker = TargetTracker()
        tracker.fire = True
        tracker._fire_start_time = time.time()
        tracker._end_fire_event()
        self.assertFalse(tracker.fire)
        self.assertEqual(tracker.attack_message, '')
        self.assertIsNone(tracker._fire_start_time)
        self.assertEqual(len(tracker._firing_events), 1)

    def test_person_detected(self):
        tracker = TargetTracker()
        with patch.object(tracker, '_person_detected', return_value=True):
            self.assertFalse(tracker._permitted_to_fire())

    def test_cooldown_period(self):
        tracker = TargetTracker()
        tracker._cool_down_till = time.time() + 1
        self.assertFalse(tracker._permitted_to_fire())

    def test_start_fire_event(self):
        tracker = TargetTracker()
        tracker.fire = False
        tracker._start_fire_event()
        self.assertTrue(tracker.fire)
        self.assertIsNotNone(tracker._fire_start_time)

if __name__ == '__main__':
    unittest.main()