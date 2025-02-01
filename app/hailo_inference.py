
import numpy as np
import cv2
import queue
from functools import partial

class HailoInference:
    def __init__(self, hef_path, threshold=0.5, **kwargs):
        #self.input_queue = queue.Queue()
        self.output_queue = queue.Queue()
        self._threshold = threshold
        
        try:
            from hailo_platform import HEF, VDevice, FormatType, HailoSchedulingAlgorithm
        except ImportError:
            raise ImportError("hailo_platform package is required for Hailo-based detection. Install with: pip install hailo-platform")
        
        
        params = VDevice.create_params()    
        params.scheduling_algorithm = HailoSchedulingAlgorithm.ROUND_ROBIN
        self.hef = HEF(hef_path)
        self.target = VDevice(params)
        self.infer_model = self.target.create_infer_model(hef_path)
        self.infer_model.set_batch_size(1)      
        self.infer_model.input().set_format_type(FormatType.UINT8)
        self.height, self.width, _ = self.hef.get_input_vstream_infos()[0].shape
    
        with open('coco.txt', 'r') as f:
            self.coco_labels = [line.strip() for line in f.readlines()]

    def callback(
        self, completion_info, bindings_list: list, input_batch: list,
    ) -> None:
        
        if completion_info.exception:
            logger.error(f'Inference error: {completion_info.exception}')
        else:
            for i, bindings in enumerate(bindings_list):
                # If the model has a single output, return the output buffer. 
                # Else, return a dictionary of output buffers, where the keys are the output names.
                if len(bindings._output_names) == 1:
                    result = bindings.output().get_buffer()
                else:
                    result = {
                        name: np.expand_dims(
                            bindings.output(name).get_buffer(), axis=0
                        )
                        for name in bindings._output_names
                    }
                self.output_queue.put(result)

    def _preprocess_frame(self, frame):
        """Preprocess frame for Hailo input"""
        # Resize frame to model input size (640x640)
        frame_resized = cv2.resize(frame, (self.width, self.height))
        # Model expects UINT8 input in NHWC format, which is what we have
        return frame_resized

    def _create_bindings(self, configured_infer_model) -> object:
        output_buffers = {
            output_info.name: np.empty(
                self.infer_model.output(output_info.name).shape,
                dtype=(getattr(np, str(output_info.format.type).split(".")[1].lower()))
            )
        for output_info in self.hef.get_output_vstream_infos()
        }
        return configured_infer_model.create_bindings(
            output_buffers=output_buffers
        )

    def infer(self, raw_frame):
        with self.infer_model.configure() as configured_infer_model:
            batch_data = [] # 
            processed_frame = self._preprocess_frame(raw_frame)
            batch_data.append(processed_frame.flatten())
            
            bindings_list = []
            for frame in batch_data:
                bindings = self._create_bindings(configured_infer_model)
                bindings.input().set_buffer(np.array(frame))
                bindings_list.append(bindings)

            configured_infer_model.wait_for_async_ready(timeout_ms=10000)
            job = configured_infer_model.run_async(
                bindings_list, partial(
                    self.callback,
                    input_batch=batch_data,
                    bindings_list=bindings_list
                )
            )
            job.wait(10000)  # Wait for the last job

            raw_detections = self.output_queue.get() # One frame in, so there should be only one frame out
            detections = self._extract_detections(raw_frame, raw_detections)
            annotated_frame = self._visualise_detections(raw_frame, detections)
            
            return annotated_frame, detections

    def _extract_detections(self, original_frame, input_data):
        
        result = []
        height, width = original_frame.shape[:2]
        
        for i, detection in enumerate(input_data):
            if len(detection) == 0 :
                continue

            for det in detection:
                bbox, score = det[:4], det[4]

                if score < self._threshold:
                    continue

                # append in ultralytics format
                result.append({
                    'name': self.coco_labels[i],
                    'class': i,
                    'box': {
                        'x1': int(bbox[1] * width),
                        'y1': int(bbox[0] * height),
                        'x2': int(bbox[3] * width),
                        'y2': int(bbox[2] * height),
                    },
                    'confidence': score,
                    
                })    
                
        return result
        
    def _visualise_detections(self, frame, detections):
        
        # Draw detections on frame
        frame_with_boxes = frame.copy()
        for det in detections:
            y1, x1, y2, x2 = det['box']['y1'], det['box']['x1'], det['box']['y2'], det['box']['x2']
            cv2.rectangle(frame_with_boxes, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame_with_boxes, f"{det['name']}: {det['confidence']:.2f}", 
                       (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return frame_with_boxes
