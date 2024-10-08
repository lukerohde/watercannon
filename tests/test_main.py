# tests/test_app.py

import unittest
import numpy as np
import cv2
from unittest.mock import MagicMock

from app.main import create_app
from camera.fake_camera import FakeCamera
from hardware.fake_hardware import FakeHardwareController

class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        """Set up the test case with fake camera and hardware controller."""
        self.fake_camera = FakeCamera(frames=[FakeCamera.fake_frame])
        self.fake_hardware_controller = FakeHardwareController()
        self.frame_processor = MagicMock()
        self.frame_processor.process_frame.return_value = FakeCamera.fake_frame

        self.app = create_app(
            camera=self.fake_camera,
            hardware_controller=self.fake_hardware_controller,
            frame_processor=self.frame_processor
        )
        self.client = self.app.test_client()

    def tearDown(self):
        """Clean up resources after each test."""
        self.fake_camera.release()
        self.fake_hardware_controller.cleanup()

    def test_streaming_endpoint(self):
        """Test the streaming endpoint to ensure it returns valid multipart JPEG frames."""
        response = self.client.get('/')
        
        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)
        
        # Assert that the Content-Type is multipart/x-mixed-replace
        self.assertEqual(response.headers['Content-Type'], 'multipart/x-mixed-replace; boundary=frame')
        
        for chunk in response.response:
            if b'--frame' in chunk:
                # Check that the chunk contains JPEG data
                self.assertIn(b'Content-Type: image/jpeg', chunk)
                
                # Extract the image data
                header_end = chunk.find(b'\r\n\r\n') + 4
                image_data = chunk[header_end:]
                
                # Decode the image data
                image_array = np.frombuffer(image_data, dtype=np.uint8)
                image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
                
                # Verify that the image was decoded successfully
                self.assertIsNotNone(image)
                
                # Verify that the image matches the fake frame
                #import ipdb; ipdb.set_trace()
                self.assertTrue(np.array_equal(image, FakeCamera.fake_frame))
        

if __name__ == '__main__':
    unittest.main()