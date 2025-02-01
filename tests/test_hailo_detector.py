#!/usr/bin/env python3

import os
import sys
import cv2
from pathlib import Path

# Add the app directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.detector import HailoDetector
from camera.fake_camera import FakeCamera

def test_hailo_detector():
    # Use the H8L model
    model_path = os.path.join(os.path.dirname(__file__), "..", "yolov8s_h8l.hef")
    
    image_path = os.path.join(os.path.dirname(__file__), '..', 'tests', 'chickens.jpg')
    image_data = cv2.imread(image_path)
        

    # Initialize detector with bird and person classes
    detector = HailoDetector(
        hef_path=model_path,
        target_classes=['bird'],
        avoid_classes=['person']
    )
    
    # Initialize fake camera
    camera = FakeCamera(frames=[image_data])
    frame_gen = camera.frame_generator()
    
    # Get a frame and detect
    frame = next(frame_gen)
    annotated_frame = detector.detect_objects(frame)
    targets = detector.targets
    print(f"Found {len(targets)} birds in the image")
    assert len(targets) == 2

    # Save annotated image
    output_path = "output_hailo.jpg"
    cv2.imwrite(output_path, annotated_frame)
    print(f"Saved annotated image to {output_path}")

if __name__ == "__main__":
    test_hailo_detector()
