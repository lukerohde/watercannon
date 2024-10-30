# test_target_tracker.py

import unittest
from app.target_tracker import TargetTracker

class TargetTrackerTestCase(unittest.TestCase):

    def setUp(self):
        # Mock a sample frame width and height
        self.frame_width = 1000
        self.frame_height = 1000

        # Mock a list of human-readable detections with bounding boxes and confidence scores
        self.detections = [
            {'name': 'bird', 'class': 14, 'confidence': 0.95, 'box': {'x1': 100, 'y1': 100, 'x2': 200, 'y2': 200}},  # Center: (150, 150)
            {'name': 'bird', 'class': 14, 'confidence': 0.80, 'box': {'x1': 400, 'y1': 400, 'x2': 500, 'y2': 500}},  # Center: (450, 450)
            {'name': 'bird', 'class': 14, 'confidence': 0.75, 'box': {'x1': 900, 'y1': 900, 'x2': 950, 'y2': 950}},  # Center: (925, 925)
            {'name': 'bird', 'class': 14, 'confidence': 0.85, 'box': {'x1': 490, 'y1': 490, 'x2': 510, 'y2': 510}},   # Center: (500, 500) - Closest
        ]
        

    def test_find_closest_target(self):
        tracker = TargetTracker()
        closest_detection = tracker._find_closest_target(self.detections, self.frame_width, self.frame_height)
        
        # Assert that the detection with center (500, 500) is the closest to the frame center (500, 500)
        expected_closest = self.detections[-1]
        self.assertEqual(closest_detection, expected_closest)

    def test_calculate_angles(self):
        tracker = TargetTracker(fov_horizontal=60, fov_vertical=40)
        detection = self.detections[-1]  # Center at (500, 500)
        tracking_data = tracker._calculate_angles(detection, self.frame_width, self.frame_height)
        # Adjusted expected angles since the center is (500, 500)
        self.assertAlmostEqual(tracking_data['dx'], 0.0)
        self.assertAlmostEqual(tracking_data['dy'], 0.0)

        # Test a detection to the right and above
        detection_right = {'name': 'bird', 'class': 14, 'confidence': 0.90, 'box': {'x1': 600, 'y1': 400, 'x2': 700, 'y2': 500}}  # Center: (650, 450)
        tracking_data = tracker._calculate_angles(detection_right, self.frame_width, self.frame_height)
        expected_angle_x = -((650 - (self.frame_width / 2)) / self.frame_width) * tracker.fov_horizontal / 2  # 150 / 1000 * 60 = 9.0 / 2
        expected_angle_y = -((450 - (self.frame_height / 2)) / self.frame_height) * tracker.fov_vertical / 2  # -50 / 1000 * 40 = -2.0 / 2
        self.assertAlmostEqual(tracking_data['dx'], expected_angle_x)
        self.assertAlmostEqual(tracking_data['dy'], expected_angle_y)

    def test_process_detections(self):
        tracker = TargetTracker()
        tracking_data = tracker.process_detections(self.detections, self.frame_width, self.frame_height)
        self.assertIsNotNone(tracking_data)
        # The closest detection is at center, so angles should be 0
        self.assertEqual(tracking_data['dx'], 0.0)
        self.assertEqual(tracking_data['dy'], 0.0)
        
    def test_process_detections_with_offset(self):
        tracker = TargetTracker()
        # Add a detection offset from the center
        offset_detection = {'name': 'bird', 'class': 14, 'confidence': 0.90, 'box': {'x1': 600, 'y1': 400, 'x2': 700, 'y2': 500}}  # Center: (650, 450)
        detections = [offset_detection]
        tracking_data = tracker.process_detections(detections, self.frame_width, self.frame_height)
        self.assertIsNotNone(tracking_data)
        expected_angle_x = -((650 - (self.frame_width / 2)) / self.frame_width) * tracker.fov_horizontal / 2  # 150 / 1000 * 60 = 9.0
        expected_angle_y = -((450 - (self.frame_height / 2)) / self.frame_height) * tracker.fov_vertical / 2 # -50 / 1000 * 40 = -2.0
        self.assertAlmostEqual(tracking_data['dx'], expected_angle_x)
        self.assertAlmostEqual(tracking_data['dy'], expected_angle_y)
        
    def test_no_detections(self):
        tracker = TargetTracker()
        tracking_data = tracker.process_detections([], self.frame_width, self.frame_height)
        self.assertIsNone(tracking_data)

if __name__ == '__main__':
    unittest.main()
