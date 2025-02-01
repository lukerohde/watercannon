#!/usr/bin/env python3

from app.hailo_inference import HailoInference

class BaseDetector:
    """
    Base class for object detection.
    """

    def __init__(self, threshold=0.5, target_classes=['bird'], avoid_classes=['person']):
        self._threshold = threshold
        self._target_classes = target_classes
        self._avoid_classes = avoid_classes
        self.annotated_frame = None
        self.detections = []
        self.targets = []
        self.aversions = []

    def detect_objects(self, frame, classes):
        raise NotImplementedError("This method should be overridden by subclasses.")


class CPUDetector(BaseDetector):
    """
    Handles object detection using a YOLO model on CPU.
    """
    def __init__(self, model_name='yolov10n.pt', **kwargs):
        super().__init__(**kwargs)
        try:
            from ultralytics import YOLO
            self.model = YOLO(model_name)

        except ImportError:
            raise ImportError("ultralytics package is required for CPU-based detection. Install with: pip install ultralytics")

    def detect_objects(self, frame):
        results = self.model(frame, verbose=False)
        detections = json.loads(results[0].to_json())
        self.annotated_frame = results[0].plot()
        self.detections = detections
        self.aversions = [item for item in self.detections if item['name'] in self._avoid_classes]
        self.targets = [item for item in self.detections if item['name'] in self._target_classes]

        return self.annotated_frame


class HailoDetector(BaseDetector):
    """
    Handles object detection using the Hailo AI hat.
    """
    def __init__(self, hef_path, threshold=0.5, **kwargs):
        super().__init__(**kwargs)

        self.hef_path = hef_path
        self.model = HailoInference(hef_path, threshold=threshold)

    def detect_objects(self, frame):
        
        annotated_frame, detections = self.model.infer(frame)

        self.detections = detections
        self.annotated_frame = annotated_frame
        self.aversions = [item for item in self.detections if item['name'] in self._avoid_classes]
        self.targets = [item for item in self.detections if item['name'] in self._target_classes]

        # Process each detection
        return annotated_frame

