
import unittest
from unittest.mock import MagicMock, patch
import numpy as np
import pandas as pd
from app.frame_processor import FrameProcessor
from app.detector import Detector
from app.target_tracker import TargetTracker
from hardware.fake_hardware import FakeHardwareController
from camera.fake_camera import FakeCamera
import cv2
import os
import ipdb
class FrameProcessorTestCase(unittest.TestCase):
    
    def setUp(self):
        # Create the mocks for the dependencies
        self.detector = MagicMock(spec=Detector)
        self.target_tracker = MagicMock(spec=TargetTracker)
        self.hardware_controller = MagicMock(spec=FakeHardwareController)

        # Instantiate FrameProcessor with the mocks
        self.frame_processor = FrameProcessor(
            detector=self.detector, 
            target_tracker=self.target_tracker, 
            hardware_controller=self.hardware_controller
        )

    def test_no_target_detected(self):
        # Mock detect_objects to return no detections
        self.detector.detect_objects.return_value = { 'frame': FakeCamera.fake_frame(), 'items': [] }

        # Call process_frame
        frame = FakeCamera.fake_frame()
        self.frame_processor.process_frame(frame)
        result = self.frame_processor.annotated_frame

        # ensure nothing was targetted
        self.target_tracker.process_detections.assert_not_called()
        self.hardware_controller.process_signals.assert_not_called()
        
        # Ensure the result contains the original frame
        self.assertIsInstance(result, np.ndarray)


    def test_target_detected(self):
        # Mock detect_objects to return a detection
        mock_detection_output = {
            'frame': FakeCamera.fake_frame(),
            'items': [
                {'name': 'bird', 'class': 14, 'confidence': 0.75, 'box': {'x1': 900, 'y1': 900, 'x2': 950, 'y2': 950}, 'box_center': {'x': 925, 'y': 925}, 'angle_x': -10, 'angle_y': -10, 'relay_on': True },  # Center: (925, 925)
                {'name': 'bird', 'class': 14, 'confidence': 0.85, 'box': {'x1': 490, 'y1': 490, 'x2': 510, 'y2': 510}, 'box_center': {'x': 500, 'y': 500}, 'angle_x': 0, 'angle_y': 0, 'relay_on': False  }      
            ]
        }
        self.detector.detect_objects.return_value = mock_detection_output
        t = TargetTracker()
        t.x1 = 450
        t.x2 = 550
        t.y1 = 450
        t.y2 = 550
        t.target_x = 500
        t.target_y = 500
        t.dx = 0
        t.dy = 0
        t.fire = True
        self.frame_processor._target_tracker = t
        
        self.hardware_controller.process_signals.return_value = None
        
        # Call process_frame
        frame = FakeCamera.fake_frame()

        with patch.object(t, 'process_detections') as mock_targeting:
            self.frame_processor.process_frame(frame)
            
            # Assert that signals were sent to the hardware
            self.hardware_controller.process_signals.assert_called_once()

        # Test frame annotations - suggest saving a fixture file and comparing
        self.image_path = os.path.join('tests','annotated.png')
        
        # Uncomment this to update the fixture
        # cv2.imwrite(os.path.join('tests','annotated.png'), self.frame_processor.annotated_frame)
        
        # Load the annotated image
        frame = cv2.imread(self.image_path)

        # Verify that the image matches the fake frame
        self.assertTrue(np.array_equal(frame, self.frame_processor.annotated_frame))
        
if __name__ == '__main__':
    unittest.main()