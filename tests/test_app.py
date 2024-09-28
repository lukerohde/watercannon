# tests/test_app.py

import unittest
import numpy as np
import cv2
from unittest.mock import patch, MagicMock

from app import create_app
from camera.fake_camera import FakeCamera
from hardware.fake_hardware import FakeHardwareController

class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        # Initialize fake camera and hardware controller
        self.fake_camera = FakeCamera(frames=[FakeCamera.fake_frame])
        self.fake_hardware_controller = FakeHardwareController()
        
        # Create the Flask app with injected fakes
        self.frame_processor=MagicMock()
        self.frame_processor.process_frame.return_value = {'annotated_frame': FakeCamera.fake_frame}

        self.app = create_app(
            camera=self.fake_camera, 
            hardware_controller=self.fake_hardware_controller, 
            frame_processor=self.frame_processor
        )
        self.client = self.app.test_client()
    
    def tearDown(self):
        # Clean up fake resources
        self.fake_camera.release()
        self.fake_hardware_controller.cleanup()
    
    def test_streaming_endpoint(self):
        # Make a request to the streaming endpoint
        response = self.client.get('/')
        
        # Assert that the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check that the content type is multipart
        self.assertEqual(response.headers['Content-Type'], 'multipart/x-mixed-replace; boundary=frame')
        
        # Read the response data
        data = b''.join(response.iter_encoded())
        
        # Check that the data contains the frame boundary and content type
        self.assertIn(b'--frame', data)
        self.assertIn(b'Content-Type: image/jpeg', data)
        
        # Extract the JPEG image from the response and verify it's valid
        parts = data.split(b'--frame')
        for part in parts:
            if b'Content-Type: image/jpeg' in part:
                # Extract the image data
                header_end = part.find(b'\r\n\r\n') + 4
                image_data = part[header_end:]
                
                # Decode the image
                image_array = np.frombuffer(image_data, dtype=np.uint8)
                image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
                
                # Verify the image is not None
                self.assertIsNotNone(image)
                
                # Check that the image matches the fake frame
                self.assertTrue(np.array_equal(image, FakeCamera.fake_frame))
                
                break

if __name__ == '__main__':
    unittest.main()
