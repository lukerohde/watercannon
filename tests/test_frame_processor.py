# # tests/test_app.py

# import unittest
# from unittest.mock import MagicMock
# #import numpy as np
# import pandas as pd
# from camera.fake_camera import FakeCamera
# from hardware.fake_hardware import FakeHardwareController

# # import cv2
# # from io import BytesIO

# import ipdb

# # Import your Flask app
# from hardware.fake_hardware import FakeHardwareController
# from frame_processor import FrameProcessor
# from target_tracker import TargetTracker

# class FlaskAppTestCase(unittest.TestCase):
#     def setUp(self):
        
#         # Replace real camera and hardware controller with fakes
#         self.fake_hardware_controller = FakeHardwareController()

#         # Inject fakes into the frame_processor
#         self.frame_processor = FrameProcessor(
#             detector=MagicMock(), 
#             target_tracker=TargetTracker(), 
#             hardware_controller=self.fake_hardware_controller
#         )

#     def tearDown(self):
#         # Reset any state if necessary
#         self.fake_hardware_controller.cleanup()

#     def test_process_frame(self):

#         # Mock frame_processor to return the fake frame as annotated

#         mock_detection_output = pd.DataFrame({
#             'xmin': [100],
#             'ymin': [150],
#             'xmax': [200],
#             'ymax': [250],
#             'confidence': [0.9],
#             'name': ['bird']
#         })
#         self.frame_processor.detector.detect_objects.return_value = mock_detection_output
        
#         result = self.frame_processor.process_frame(FakeCamera.fake_frame)
#         ipdb.set_trace()

# if __name__ == '__main__':
#     unittest.main()


import unittest
from unittest.mock import MagicMock, patch
import numpy as np
import pandas as pd
from frame_processor import FrameProcessor
from detector import Detector
from target_tracker import TargetTracker
from hardware.fake_hardware import FakeHardwareController
from camera.fake_camera import FakeCamera
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
        self.detector.detect_objects.return_value = { 'frame': FakeCamera.fake_frame, 'items': [] }

        # Call process_frame
        frame = FakeCamera.fake_frame 
        result = self.frame_processor.process_frame(frame)

        # ensure nothing was targetted
        self.target_tracker.process_detections.assert_not_called()
        self.hardware_controller.process_signals.assert_not_called()
        #self.frame_processor.update_frame.assert_not_called()
        
        # Ensure the result contains the original frame
        self.assertIn('annotated_frame', result)
        self.assertIsInstance(result['annotated_frame'], np.ndarray)


    def test_target_detected(self):
        # Mock detect_objects to return a detection
        mock_detection_output = {
            'frame': FakeCamera.fake_frame,
            'items': [
                {'name': 'bird', 'class': 14, 'confidence': 0.75, 'box': {'x1': 900, 'y1': 900, 'x2': 950, 'y2': 950}, 'box_center': {'x': 925, 'y': 925}, 'angle_x': -10, 'angle_y': -10 },  # Center: (925, 925)
                {'name': 'bird', 'class': 14, 'confidence': 0.85, 'box': {'x1': 490, 'y1': 490, 'x2': 510, 'y2': 510}, 'box_center': {'x': 500, 'y': 500}, 'angle_x': 0, 'angle_y': 0 }      
            ]
        }
        self.detector.detect_objects.return_value = mock_detection_output
        self.target_tracker.process_detections.return_value = mock_detection_output['items'][1]
        self.hardware_controller.process_signals.return_value = None
        
        # Call process_frame
        frame = FakeCamera.fake_frame
        result = self.frame_processor.process_frame(frame)

        # Assert that signals were sent to the hardware
        self.hardware_controller.process_signals.assert_called_once()

if __name__ == '__main__':
    unittest.main()