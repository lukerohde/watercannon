import unittest
import cv2
import os
from app.detector import Detector
import ipdb

class YOLODetectorTestCase(unittest.TestCase):
    def setUp(self):
        # Initialize the YOLO detector, targeting 'bird' class
        self.detector = Detector(model_name='yolov10n.pt', target_class='bird')

        # Path to the chicken image file
        self.image_path = 'tests/chickens.jpg'
    
    def test_detect_chicken(self):
        # Load the chicken image using OpenCV
        frame = cv2.imread(self.image_path)

        # Check that the image is loaded correctly
        self.assertIsNotNone(frame, "Failed to load the image")

        # Run the detector to detect objects in the frame
        results = self.detector.detect_objects(frame)
        detections = results['items']

        # Assert that at least one detection is returned
        self.assertTrue(len(detections)==2, "Two birds should be detected")

        # Check that all detections are of the target class 'bird'
        self.assertTrue(all([item['name'] == 'bird' for item in detections]), "Not all detections are birds")

    def test_no_chicken(self):
        # Load the chicken image using OpenCV
        frame = cv2.imread('tests/chicken_missing.jpg')

        # Check that the image is loaded correctly
        self.assertIsNotNone(frame, "Failed to load the image")

        # Run the detector to detect objects in the frame
        results = self.detector.detect_objects(frame)
        detections = results['items']
        
        # Assert that at least one detection is returned
        self.assertTrue(len(detections)==0, "No birds should be detected")

if __name__ == '__main__':
    unittest.main()