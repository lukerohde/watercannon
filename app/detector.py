# detector.py
from ultralytics import YOLO
import ipdb
import numpy as np
import json

class Detector:
    """
    Handles object detection using a YOLO model.
    """

    def __init__(self, model_name='yolov10n.pt', target_class='bird'):
        self.model = YOLO(model_name)
        self.target_class = target_class


    def detect_objects(self, frame):
        """
        Perform object detection and filter for the target class.

        Args:
            frame: Input frame.

        Returns:
            DataFrame: Detections of the target class.
        """
        results = self.model(frame, verbose=False)
        target_class_ids = [key for key, value in results[0].names.items() if value == self.target_class]

        detections = json.loads(results[0].to_json()) 
        target_detections = [item for item in detections if item['name'] == self.target_class]
        return {
            'frame': results[0].plot(), 
            'items': target_detections
        }