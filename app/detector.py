# detector.py
from ultralytics import YOLO
import ipdb
import numpy as np
import json

class Detector:
    """
    Handles object detection using a YOLO model.
    """

    def __init__(self, model_name='yolov10n.pt', target_classes=['bird'], avoid_classes=['person']):
        self.model = YOLO(model_name)
        self._target_classes = target_classes
        self._avoid_classes = avoid_classes


    def detect_objects(self, frame, classes):
        """
        Perform object detection and filter for the target class.
        """
        results = self.model(frame, verbose=False)
        #target_class_ids = [key for key, value in results[0].names.items() if value in self.target_classes]

        detections = json.loads(results[0].to_json()) 
        target_detections = [item for item in detections if item['name'] in classes]
        return {
            'frame': results[0].plot(), 
            'items': target_detections
        }

    def detect_targets(self, frame):
        return self.detect_objects(frame, self._target_classes)

    def detect_aversions(self, frame):
        return self.detect_objects(frame, self._avoid_classes)