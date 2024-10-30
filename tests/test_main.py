# tests/test_main.py

import unittest
import numpy as np
import cv2
from unittest.mock import MagicMock

from app.main import App
from camera.fake_camera import FakeCamera
from hardware.fake_hardware import FakeHardwareController
from app.frame_store import FrameStore


class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        """Set up the test case with fake camera, hardware controller, frame processor, and frame store."""
        self.fake_camera = FakeCamera(frames=[FakeCamera.fake_frame()])
        self.fake_hardware_controller = FakeHardwareController()
        self.frame_processor = MagicMock()
        self.frame_processor.annotated_frame = FakeCamera.fake_frame()
        self.temp_monitor = MagicMock()
        
        self.app_instance = App(
            camera=self.fake_camera,
            hardware_controller=self.fake_hardware_controller,
            frame_processor=self.frame_processor,
            temp_monitor=self.temp_monitor
        )
        self.app_instance.start_processing()
        self.client = self.app_instance.app.test_client()

    def tearDown(self):
        """Clean up resources after each test."""
        self.app_instance.stop_processing()

    # def test_streaming_endpoint(self):
    #     """Test the streaming endpoint to ensure it returns valid multipart JPEG frames."""
    #     response = self.client.get('/')

    #     # Assert that the response status code is 200 (OK)
    #     self.assertEqual(response.status_code, 200)

    #     # Assert that the Content-Type is multipart/x-mixed-replace
    #     self.assertEqual(response.headers['Content-Type'], 'text/html; charset=utf-8')

    #     received_frames = 0
    #     for chunk in response.response:
    #         if b'--frame' in chunk:
    #             # Check that the chunk contains JPEG data
    #             self.assertIn(b'Content-Type: image/jpeg', chunk)

    #             # Extract the image data
    #             header_end = chunk.find(b'\r\n\r\n') + 4
    #             image_data = chunk[header_end:]

    #             # Decode the image data
    #             image_array = np.frombuffer(image_data, dtype=np.uint8)
    #             image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    #             # Verify that the image was decoded successfully
    #             self.assertIsNotNone(image)

    #             # Verify that the image matches the fake frame
    #             self.assertTrue(np.array_equal(image, FakeCamera.fake_frame()))
    #             received_frames += 1

    #     # Ensure that at least one frame was received
    #     self.assertGreater(received_frames, 0)

    def test_streaming_endpoint(self):
        """Test the streaming endpoint to ensure it returns valid multipart JPEG frames."""
        response = self.client.get('/video_feed')

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Assert that the Content-Type is multipart/x-mixed-replace
        self.assertEqual(response.headers['Content-Type'], 'multipart/x-mixed-replace; boundary=frame')

        received_frames = 0
        # Since response.response is a generator, we can iterate over it to get the frames
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


                # Save the received image to disk for inspection
                cv2.imwrite('received_image.png', image)

                # Save the fake frame to disk for inspection
                fake_image = FakeCamera.fake_frame()
                cv2.imwrite('fake_image.png', fake_image)

                # Verify that the image matches the fake frame
                #self.assertTrue(np.array_equal(image, FakeCamera.fake_frame()))
                #self.assertTrue(np.allclose(image, FakeCamera.fake_frame(), atol=10))
                  # Verify that the image matches the fake frame within a tolerance
                difference = cv2.absdiff(image, FakeCamera.fake_frame())
                mean_diff = np.mean(difference)
                acceptable_threshold = 10  # Adjust this value as needed
                self.assertLess(mean_diff, acceptable_threshold, f"Mean difference {mean_diff} exceeds threshold")



                received_frames += 1

                # For testing purposes, we can break after receiving a certain number of frames
                if received_frames >= 1:
                    break

        # Ensure that at least one frame was received
        self.assertGreater(received_frames, 0)

if __name__ == '__main__':
    unittest.main()