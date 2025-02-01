from typing import List, Generator, Optional, Tuple, Dict
from pathlib import Path
from functools import partial
import queue
from loguru import logger
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from hailo_platform import (HEF, VDevice,
                            FormatType, HailoSchedulingAlgorithm)
                          
IMAGE_EXTENSIONS: Tuple[str, ...] = ('.jpg', '.png', '.bmp', '.jpeg')

class HailoAsyncInference:
    def __init__(
        self, hef_path: str, input_queue: queue.Queue,
        output_queue: queue.Queue, batch_size: int = 1,
        input_type: Optional[str] = None, output_type: Optional[Dict[str, str]] = None,
        send_original_frame: bool = False) -> None:
        """
        Initialize the HailoAsyncInference class with the provided HEF model 
        file path and input/output queues.

        Args:
            hef_path (str): Path to the HEF model file.
            input_queue (queue.Queue): Queue from which to pull input frames 
                                       for inference.
            output_queue (queue.Queue): Queue to hold the inference results.
            batch_size (int): Batch size for inference. Defaults to 1.
            input_type (Optional[str]): Format type of the input stream. 
                                        Possible values: 'UINT8', 'UINT16'.
            output_type Optional[dict[str, str]] : Format type of the output stream. 
                                         Possible values: 'UINT8', 'UINT16', 'FLOAT32'.
        """
        self.input_queue = input_queue
        self.output_queue = output_queue
        params = VDevice.create_params()    
        # Set the scheduling algorithm to round-robin to activate the scheduler
        params.scheduling_algorithm = HailoSchedulingAlgorithm.ROUND_ROBIN

        self.hef = HEF(hef_path)
        self.target = VDevice(params)
        self.infer_model = self.target.create_infer_model(hef_path)
        self.infer_model.set_batch_size(batch_size)      
        if input_type is not None:
            self._set_input_type(input_type)
        if output_type is not None:
            self._set_output_type(output_type)

        self.output_type = output_type
        self.send_original_frame = send_original_frame

    def _set_input_type(self, input_type: Optional[str] = None) -> None:
        """
        Set the input type for the HEF model. If the model has multiple inputs,
        it will set the same type of all of them.

        Args:
            input_type (Optional[str]): Format type of the input stream.
        """
        self.infer_model.input().set_format_type(getattr(FormatType, input_type))
    
    def _set_output_type(self, output_type_dict: Optional[Dict[str, str]] = None) -> None:
        """
        Set the output type for the HEF model. If the model has multiple outputs,
        it will set the same type for all of them.

        Args:
            output_type_dict (Optional[dict[str, str]]): Format type of the output stream.
        """
        for output_name, output_type in output_type_dict.items():
            self.infer_model.output(output_name).set_format_type(
                getattr(FormatType, output_type)
            )

    def callback(
        self, completion_info, bindings_list: list, input_batch: list,
    ) -> None:
        """
        Callback function for handling inference results.

        Args:
            completion_info: Information about the completion of the 
                             inference task.
            bindings_list (list): List of binding objects containing input 
                                  and output buffers.
            processed_batch (list): The processed batch of images.
        """
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
                self.output_queue.put((input_batch[i], result))

    def get_vstream_info(self) -> Tuple[list, list]:

        """
        Get information about input and output stream layers.

        Returns:
            Tuple[list, list]: List of input stream layer information, List of 
                               output stream layer information.
        """
        return (
            self.hef.get_input_vstream_infos(), 
            self.hef.get_output_vstream_infos()
        )

    def get_hef(self) -> HEF:
        """
        Get the object's HEF file
        
        Returns:
            HEF: A HEF (Hailo Executable File) containing the model.
        """
        return self.hef

    def get_input_shape(self) -> Tuple[int, ...]:
        """
        Get the shape of the model's input layer.

        Returns:
            Tuple[int, ...]: Shape of the model's input layer.
        """
        return self.hef.get_input_vstream_infos()[0].shape  # Assumes one input

    def run(self) -> None:
        with self.infer_model.configure() as configured_infer_model:
            #while True:
            batch_data = self.input_queue.get()
            
            if batch_data is None:
                return  # Sentinel value to stop the inference loop

            if self.send_original_frame:
                original_batch, preprocessed_batch = batch_data
            else:
                preprocessed_batch = batch_data

            bindings_list = []
            for frame in preprocessed_batch:
                bindings = self._create_bindings(configured_infer_model)
                bindings.input().set_buffer(np.array(frame))
                bindings_list.append(bindings)

            configured_infer_model.wait_for_async_ready(timeout_ms=10000)
            job = configured_infer_model.run_async(
                bindings_list, partial(
                    self.callback,
                    input_batch=original_batch if self.send_original_frame else preprocessed_batch,
                    bindings_list=bindings_list
                )
            )
            job.wait(10000)  # Wait for the last job

    def _get_output_type_str(self, output_info) -> str:
        if self.output_type is None:
            return str(output_info.format.type).split(".")[1].lower()
        else:
            self.output_type[output_info.name].lower()

    def _create_bindings(self, configured_infer_model) -> object:
        """
        Create bindings for input and output buffers.

        Args:
            configured_infer_model: The configured inference model.

        Returns:
            object: Bindings object with input and output buffers.
        """
        if self.output_type is None:
            output_buffers = {
                output_info.name: np.empty(
                    self.infer_model.output(output_info.name).shape,
                    dtype=(getattr(np, self._get_output_type_str(output_info)))
                )
            for output_info in self.hef.get_output_vstream_infos()
            }
        else:
            output_buffers = {
                name: np.empty(
                    self.infer_model.output(name).shape, 
                    dtype=(getattr(np, self.output_type[name].lower()))
                )
            for name in self.output_type
            }
        return configured_infer_model.create_bindings(
            output_buffers=output_buffers
        )


def load_input_images(images_path: str) -> List[Image.Image]:
    """
    Load images from the specified path.

    Args:
        images_path (str): Path to the input image or directory of images.

    Returns:
        List[Image.Image]: List of PIL.Image.Image objects.
    """
    path = Path(images_path)
    if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
        return [Image.open(path)]
    elif path.is_dir():
        return [
            Image.open(img) for img in path.glob("*") 
            if img.suffix.lower() in IMAGE_EXTENSIONS
        ]
    return []


def validate_images(images: List[Image.Image], batch_size: int) -> None:
    """
    Validate that images exist and are properly divisible by the batch size.

    Args:
        images (List[Image.Image]): List of images.
        batch_size (int): Number of images per batch.

    Raises:
        ValueError: If images list is empty or not divisible by batch size.
    """
    if not images:
        raise ValueError(
            'No valid images found in the specified path.'
        )
    
    if len(images) % batch_size != 0:
        raise ValueError(
            'The number of input images should be divisible by the batch size '
            'without any remainder.'
        )


def divide_list_to_batches(
    images_list: List[Image.Image], batch_size: int
) -> Generator[List[Image.Image], None, None]:
    """
    Divide the list of images into batches.

    Args:
        images_list (List[Image.Image]): List of images.
        batch_size (int): Number of images in each batch.

    Returns:
        Generator[List[Image.Image], None, None]: Generator yielding batches 
                                                  of images.
    """
    for i in range(0, len(images_list), batch_size):
        yield images_list[i: i + batch_size]

def generate_color(class_id: int) -> tuple:
    """
    Generate a unique color for a given class ID.

    Args:
        class_id (int): The class ID to generate a color for.

    Returns:
        tuple: A tuple representing an RGB color.
    """
    np.random.seed(class_id)
    return tuple(np.random.randint(0, 255, size=3).tolist())


class ObjectDetectionUtils:
    def __init__(self, labels_path: str, padding_color: tuple = (114, 114, 114), label_font: str = "LiberationSans-Regular.ttf"):
        """
        Initialize the ObjectDetectionUtils class.

        Args:
            labels_path (str): Path to the labels file.
            padding_color (tuple): RGB color for padding. Defaults to (114, 114, 114).
            label_font (str): Path to the font used for labeling. Defaults to "LiberationSans-Regular.ttf".
        """
        self.labels = self.get_labels(labels_path)
        self.padding_color = padding_color
        self.label_font = label_font
    
    def get_labels(self, labels_path: str) -> list:
        """
        Load labels from a file.

        Args:
            labels_path (str): Path to the labels file.

        Returns:
            list: List of class names.
        """
        with open(labels_path, 'r', encoding="utf-8") as f:
            class_names = f.read().splitlines()
        return class_names

    def preprocess(self, image: Image.Image, model_w: int, model_h: int) -> Image.Image:
        """
        Resize image with unchanged aspect ratio using padding.

        Args:
            image (PIL.Image.Image): Input image.
            model_w (int): Model input width.
            model_h (int): Model input height.

        Returns:
            PIL.Image.Image: Preprocessed and padded image.
        """
        img_w, img_h = image.size
        scale = min(model_w / img_w, model_h / img_h)
        new_img_w, new_img_h = int(img_w * scale), int(img_h * scale)
        image = image.resize((new_img_w, new_img_h), Image.Resampling.BICUBIC)

        padded_image = Image.new('RGB', (model_w, model_h), self.padding_color)
        padded_image.paste(image, ((model_w - new_img_w) // 2, (model_h - new_img_h) // 2))
        return padded_image

    def draw_detection(self, draw: ImageDraw.Draw, box: list, cls: int, score: float, color: tuple, scale_factor: float):
        """
        Draw box and label for one detection.

        Args:
            draw (ImageDraw.Draw): Draw object to draw on the image.
            box (list): Bounding box coordinates.
            cls (int): Class index.
            score (float): Detection score.
            color (tuple): Color for the bounding box.
            scale_factor (float): Scale factor for coordinates.
        """
        label = f"{self.labels[cls]}: {score:.2f}%"
        ymin, xmin, ymax, xmax = box
        font = ImageFont.truetype(self.label_font, size=15)
        draw.rectangle([(xmin * scale_factor, ymin * scale_factor), (xmax * scale_factor, ymax * scale_factor)], outline=color, width=2)
        draw.text((xmin * scale_factor + 4, ymin * scale_factor + 4), label, fill=color, font=font)

    def visualize(self, detections: dict, image: Image.Image, image_id: int, output_path: str, width: int, height: int, min_score: float = 0.45, scale_factor: float = 1):
        """
        Visualize detections on the image.

        Args:
            detections (dict): Detection results.
            image (PIL.Image.Image): Image to draw on.
            image_id (int): Image identifier.
            output_path (str): Path to save the output image.
            width (int): Image width.
            height (int): Image height.
            min_score (float): Minimum score threshold. Defaults to 0.45.
            scale_factor (float): Scale factor for coordinates. Defaults to 1.
        """
        boxes = detections['detection_boxes']
        classes = detections['detection_classes']
        scores = detections['detection_scores']
        draw = ImageDraw.Draw(image)

        for idx in range(detections['num_detections']):
            if scores[idx] >= min_score:
                color = generate_color(classes[idx])
                scaled_box = [x * width if i % 2 == 0 else x * height for i, x in enumerate(boxes[idx])]
                self.draw_detection(draw, scaled_box, classes[idx], scores[idx] * 100.0, color, scale_factor)
                
        image.save(f'{output_path}/output_image{image_id}.jpg', 'JPEG')

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
                    classes.append(i)
                    num_detections += 1
                    
        return {
            'detection_boxes': boxes, 
            'detection_classes': classes, 
            'detection_scores': scores,
            'num_detections': num_detections
        }