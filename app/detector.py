#!/usr/bin/env python3

import numpy as np
import json
import cv2
import queue
from hailo_platform import HEF, VDevice, FormatType, HailoSchedulingAlgorithm
from .halio_utils import HailoAsyncInference

# COCO class indices for our target classes
COCO_BIRD_INDEX = 14  # 'bird' in COCO dataset
COCO_PERSON_INDEX = 0  # 'person' in COCO dataset

class BaseDetector:
    """
    Base class for object detection.
    """

    def __init__(self, target_classes=['bird'], avoid_classes=['person']):
        self._target_classes = target_classes
        self._avoid_classes = avoid_classes

    def detect_objects(self, frame, classes):
        raise NotImplementedError("This method should be overridden by subclasses.")

    def detect_targets(self, frame):
        return self.detect_objects(frame, self._target_classes)

    def detect_aversions(self, frame):
        return self.detect_objects(frame, self._avoid_classes)


class Detector(BaseDetector):
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

    def detect_objects(self, frame, classes):
        results = self.model(frame, verbose=False)
        detections = json.loads(results[0].to_json())
        target_detections = [item for item in detections if item['name'] in classes]
        return {
            'frame': results[0].plot(),
            'items': target_detections
        }


class HailoBasedDetector(BaseDetector):
    """
    Handles object detection using the Hailo AI hat.
    """

    def __init__(self, hef_path, **kwargs):
        super().__init__(**kwargs)
        try:
            # Create input/output queues
            self.input_queue = queue.Queue()
            self.output_queue = queue.Queue()
            
            # Initialize async inference
            self.hailo_inference = HailoAsyncInference(
                hef_path=hef_path,
                input_queue=self.input_queue,
                output_queue=self.output_queue,
                batch_size=1,
                input_type='UINT8'  # Model expects UINT8 input
            )
            
            # Get input shape for preprocessing
            self.height, self.width, _ = self.hailo_inference.get_input_shape()
            
            # Read COCO class labels
            with open('coco.txt', 'r') as f:
                self.coco_labels = [line.strip() for line in f.readlines()]
        


        except ImportError:
            raise ImportError("hailo_platform package is required for Hailo-based detection.")

    def preprocess_frame(self, frame):
        """Preprocess frame for Hailo input"""
        # Resize frame to model input size (640x640)
        frame_resized = cv2.resize(frame, (self.width, self.height))
        # Model expects UINT8 input in NHWC format, which is what we have
        return frame_resized


    def extract_detections(self, input_data: list, threshold: float = 0.5) -> dict:
        """
        Extract detections from the input data.

        Args:
            input_data (list): Raw detections from the model.
            threshold (float): Score threshold for filtering detections. Defaults to 0.5.

        Returns:
            dict: Filtered detection results.
        """
        boxes, scores, classes = [], [], []
        num_detections = 0
        
        for i, detection in enumerate(input_data):
            if len(detection) == 0:
                continue

            for det in detection:
                bbox, score = det[:4], det[4]

                if score >= threshold:
                    boxes.append(bbox)
                    scores.append(score)
                    classes.append(self.coco_labels[i])
                    num_detections += 1
                    
        return {
            'boxes': boxes, 
            'classes': classes, 
            'scores': scores,
            'num_detections': num_detections
        }


    def detect_objects(self, frame, classes):
        
        # Preprocess frame
        frame_preprocessed = self.preprocess_frame(frame)
        # Add frame to input queue and start inference
        self.input_queue.put([frame_preprocessed.flatten()])
        self.hailo_inference.run()
        
        # Get results from output queue
        _, results = self.output_queue.get()
        detections = self.extract_detections(results)
        # Results are in HAILO NMS format with 100 boxes per class
        # Each detection is [x1, y1, x2, y2, score, class_id]
        target_detections = []
        
        # Process each detection
        for i in range(detections['num_detections']):
            name = detections['classes'][i]
            score = detections['scores'][i]
            box = detections['boxes'][i]
            
            if score > 0.5:  # Confidence threshold
                # Bounding box is already in pixel coordinates
                x1, y1, x2, y2 = map(int, box * [self.width, self.height, self.width, self.height])
                y1, x1, y2, x2 = map(int, box * [self.width, self.height, self.width, self.height])
                
                # Add detection
                target_detections.append({
                    'name': name,
                    'confidence': score,
                    'bbox': [x1, y1, x2, y2]
                })
        
        # Draw detections on frame
        frame_with_boxes = frame_preprocessed.copy()
        for det in target_detections:
            x1, y1, x2, y2 = det['bbox']
            cv2.rectangle(frame_with_boxes, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame_with_boxes, f"{det['name']}: {det['confidence']:.2f}", 
                       (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return {
            'frame': frame_with_boxes,
            'items': target_detections
        }