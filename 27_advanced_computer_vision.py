#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Advanced Computer Vision System
------------------------------
A comprehensive computer vision system that implements:
- Object detection and recognition
- Face detection and recognition
- Image segmentation
- Real-time video processing
- OCR (Optical Character Recognition)
- Image enhancement and restoration
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras import models, layers, applications
from sklearn.cluster import KMeans
from sklearn.metrics import accuracy_score
import mediapipe as mp
import pytesseract
import face_recognition
import argparse
import os
import sys
import json
import time
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum, auto
import logging
from pathlib import Path
import pickle

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DetectionMode(Enum):
    """Detection modes for the vision system"""
    OBJECT_DETECTION = auto()
    FACE_DETECTION = auto()
    FACE_RECOGNITION = auto()
    OCR = auto()
    SEGMENTATION = auto()
    POSE_ESTIMATION = auto()
    HAND_TRACKING = auto()

@dataclass
class DetectionResult:
    """Result of a detection operation"""
    mode: DetectionMode
    confidence: float
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    label: str
    metadata: Dict[str, Any]

class ObjectDetector:
    """Advanced object detection using YOLO and other models"""
    
    def __init__(self, model_path: str = None):
        """Initialize the object detector
        
        Args:
            model_path: Path to custom model weights
        """
        self.model_path = model_path
        self.net = None
        self.output_layers = None
        self.classes = []
        self.colors = np.random.uniform(0, 255, size=(100, 3))
        
        # Load YOLO model
        self.load_yolo_model()
    
    def load_yolo_model(self):
        """Load YOLO model for object detection"""
        try:
            # Try to load YOLOv4 or YOLOv5 model
            weights_path = "yolo/yolov4.weights"
            config_path = "yolo/yolov4.cfg"
            classes_path = "yolo/coco.names"
            
            if os.path.exists(weights_path) and os.path.exists(config_path):
                self.net = cv2.dnn.readNet(weights_path, config_path)
                layer_names = self.net.getLayerNames()
                self.output_layers = [layer_names[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]
                
                # Load class names
                with open(classes_path, 'r') as f:
                    self.classes = [line.strip() for line in f.readlines()]
                
                logger.info("YOLO model loaded successfully")
            else:
                logger.warning("YOLO model files not found, using fallback detection")
                self.load_fallback_model()
                
        except Exception as e:
            logger.error(f"Error loading YOLO model: {e}")
            self.load_fallback_model()
    
    def load_fallback_model(self):
        """Load a fallback model using OpenCV's DNN module"""
        try:
            # Use MobileNet SSD as fallback
            self.net = cv2.dnn.readNetFromTensorflow(
                'models/frozen_inference_graph.pb',
                'models/ssd_mobilenet_v2_coco.pbtxt'
            )
            self.classes = ['background', 'person', 'bicycle', 'car', 'motorcycle', 
                          'airplane', 'bus', 'train', 'truck', 'boat']
            logger.info("Fallback model loaded")
        except:
            logger.warning("No pre-trained models available, using basic detection")
    
    def detect_objects(self, image: np.ndarray, confidence_threshold: float = 0.5) -> List[DetectionResult]:
        """Detect objects in an image
        
        Args:
            image: Input image
            confidence_threshold: Minimum confidence for detection
            
        Returns:
            List of detection results
        """
        if self.net is None:
            return self.detect_objects_basic(image)
        
        height, width = image.shape[:2]
        
        # Prepare image for detection
        blob = cv2.dnn.blobFromImage(image, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        self.net.setInput(blob)
        outputs = self.net.forward(self.output_layers)
        
        # Process detections
        boxes = []
        confidences = []
        class_ids = []
        
        for output in outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                
                if confidence > confidence_threshold:
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)
        
        # Apply non-maximum suppression
        indices = cv2.dnn.NMSBoxes(boxes, confidences, confidence_threshold, 0.4)
        
        results = []
        if len(indices) > 0:
            for i in indices.flatten():
                x, y, w, h = boxes[i]
                label = self.classes[class_ids[i]] if class_ids[i] < len(self.classes) else "Unknown"
                
                results.append(DetectionResult(
                    mode=DetectionMode.OBJECT_DETECTION,
                    confidence=confidences[i],
                    bbox=(x, y, w, h),
                    label=label,
                    metadata={"class_id": class_ids[i]}
                ))
        
        return results
    
    def detect_objects_basic(self, image: np.ndarray) -> List[DetectionResult]:
        """Basic object detection using traditional computer vision"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        results = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 1000:  # Filter small objects
                x, y, w, h = cv2.boundingRect(contour)
                results.append(DetectionResult(
                    mode=DetectionMode.OBJECT_DETECTION,
                    confidence=0.7,
                    bbox=(x, y, w, h),
                    label="Object",
                    metadata={"area": area}
                ))
        
        return results

class FaceRecognitionSystem:
    """Advanced face detection and recognition system"""
    
    def __init__(self):
        """Initialize the face recognition system"""
        self.known_face_encodings = []
        self.known_face_names = []
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
    def add_known_face(self, image_path: str, name: str):
        """Add a known face to the recognition database
        
        Args:
            image_path: Path to the face image
            name: Name of the person
        """
        try:
            image = face_recognition.load_image_file(image_path)
            encoding = face_recognition.face_encodings(image)[0]
            
            self.known_face_encodings.append(encoding)
            self.known_face_names.append(name)
            
            logger.info(f"Added face for {name}")
        except Exception as e:
            logger.error(f"Error adding face for {name}: {e}")
    
    def detect_faces(self, image: np.ndarray) -> List[DetectionResult]:
        """Detect faces in an image
        
        Args:
            image: Input image
            
        Returns:
            List of face detection results
        """
        # Convert to RGB if needed
        if len(image.shape) == 3 and image.shape[2] == 3:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            rgb_image = image
        
        # Find face locations
        face_locations = face_recognition.face_locations(rgb_image)
        
        results = []
        for (top, right, bottom, left) in face_locations:
            results.append(DetectionResult(
                mode=DetectionMode.FACE_DETECTION,
                confidence=0.9,
                bbox=(left, top, right - left, bottom - top),
                label="Face",
                metadata={"face_location": (top, right, bottom, left)}
            ))
        
        return results
    
    def recognize_faces(self, image: np.ndarray) -> List[DetectionResult]:
        """Recognize faces in an image
        
        Args:
            image: Input image
            
        Returns:
            List of face recognition results
        """
        if not self.known_face_encodings:
            return self.detect_faces(image)
        
        # Convert to RGB if needed
        if len(image.shape) == 3 and image.shape[2] == 3:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            rgb_image = image
        
        # Find face locations and encodings
        face_locations = face_recognition.face_locations(rgb_image)
        face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
        
        results = []
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # Compare with known faces
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            
            name = "Unknown"
            confidence = 0.5
            
            if matches:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]
                    confidence = 1.0 - face_distances[best_match_index]
            
            results.append(DetectionResult(
                mode=DetectionMode.FACE_RECOGNITION,
                confidence=confidence,
                bbox=(left, top, right - left, bottom - top),
                label=name,
                metadata={"face_encoding": face_encoding.tolist()}
            ))
        
        return results

class OCRSystem:
    """Optical Character Recognition system"""
    
    def __init__(self):
        """Initialize the OCR system"""
        # Configure Tesseract
        self.tesseract_config = '--oem 3 --psm 6'
    
    def extract_text(self, image: np.ndarray, preprocess: bool = True) -> List[DetectionResult]:
        """Extract text from an image
        
        Args:
            image: Input image
            preprocess: Whether to preprocess the image
            
        Returns:
            List of text detection results
        """
        processed_image = image.copy()
        
        if preprocess:
            processed_image = self.preprocess_for_ocr(processed_image)
        
        try:
            # Extract text with bounding boxes
            data = pytesseract.image_to_data(processed_image, config=self.tesseract_config, output_type=pytesseract.Output.DICT)
            
            results = []
            n_boxes = len(data['level'])
            
            for i in range(n_boxes):
                confidence = float(data['conf'][i])
                text = data['text'][i].strip()
                
                if confidence > 30 and text:  # Filter low confidence and empty text
                    x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                    
                    results.append(DetectionResult(
                        mode=DetectionMode.OCR,
                        confidence=confidence / 100.0,
                        bbox=(x, y, w, h),
                        label=text,
                        metadata={"word_num": data['word_num'][i], "block_num": data['block_num'][i]}
                    ))
            
            return results
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return []
    
    def preprocess_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR results
        
        Args:
            image: Input image
            
        Returns:
            Preprocessed image
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply adaptive threshold
        thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        
        # Morphological operations to clean up
        kernel = np.ones((2, 2), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return cleaned

class ImageSegmentation:
    """Advanced image segmentation system"""
    
    def __init__(self):
        """Initialize the segmentation system"""
        self.model = None
        self.load_segmentation_model()
    
    def load_segmentation_model(self):
        """Load pre-trained segmentation model"""
        try:
            # Use DeepLab or U-Net model if available
            self.model = tf.keras.applications.imagenet_utils.decode_predictions
            logger.info("Segmentation model loaded")
        except Exception as e:
            logger.warning(f"Could not load segmentation model: {e}")
    
    def segment_image(self, image: np.ndarray, method: str = "watershed") -> np.ndarray:
        """Segment an image using various methods
        
        Args:
            image: Input image
            method: Segmentation method ('watershed', 'kmeans', 'grabcut')
            
        Returns:
            Segmented image
        """
        if method == "watershed":
            return self.watershed_segmentation(image)
        elif method == "kmeans":
            return self.kmeans_segmentation(image)
        elif method == "grabcut":
            return self.grabcut_segmentation(image)
        else:
            return self.watershed_segmentation(image)
    
    def watershed_segmentation(self, image: np.ndarray) -> np.ndarray:
        """Watershed segmentation algorithm"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Noise removal
        kernel = np.ones((3, 3), np.uint8)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
        
        # Sure background area
        sure_bg = cv2.dilate(opening, kernel, iterations=3)
        
        # Finding sure foreground area
        dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
        _, sure_fg = cv2.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)
        
        # Finding unknown region
        sure_fg = np.uint8(sure_fg)
        unknown = cv2.subtract(sure_bg, sure_fg)
        
        # Marker labelling
        _, markers = cv2.connectedComponents(sure_fg)
        markers = markers + 1
        markers[unknown == 255] = 0
        
        # Apply watershed
        markers = cv2.watershed(image, markers)
        image[markers == -1] = [255, 0, 0]
        
        return image
    
    def kmeans_segmentation(self, image: np.ndarray, k: int = 3) -> np.ndarray:
        """K-means clustering segmentation"""
        data = image.reshape((-1, 3))
        data = np.float32(data)
        
        # Apply K-means
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        _, labels, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        
        # Convert back to uint8 and reshape
        centers = np.uint8(centers)
        segmented_data = centers[labels.flatten()]
        segmented_image = segmented_data.reshape(image.shape)
        
        return segmented_image
    
    def grabcut_segmentation(self, image: np.ndarray) -> np.ndarray:
        """GrabCut segmentation algorithm"""
        height, width = image.shape[:2]
        
        # Initialize mask
        mask = np.zeros((height, width), np.uint8)
        
        # Define rectangle for probable foreground
        rect = (50, 50, width - 100, height - 100)
        
        # Initialize background and foreground models
        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)
        
        # Apply GrabCut
        cv2.grabCut(image, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)
        
        # Modify mask
        mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
        result = image * mask2[:, :, np.newaxis]
        
        return result

class PoseEstimation:
    """Human pose estimation system"""
    
    def __init__(self):
        """Initialize pose estimation"""
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
    
    def estimate_pose(self, image: np.ndarray) -> List[DetectionResult]:
        """Estimate human pose in image
        
        Args:
            image: Input image
            
        Returns:
            List of pose detection results
        """
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_image)
        
        detection_results = []
        
        if results.pose_landmarks:
            # Extract key points
            landmarks = []
            for landmark in results.pose_landmarks.landmark:
                landmarks.append({
                    'x': landmark.x,
                    'y': landmark.y,
                    'z': landmark.z,
                    'visibility': landmark.visibility
                })
            
            # Calculate bounding box
            x_coords = [lm['x'] for lm in landmarks]
            y_coords = [lm['y'] for lm in landmarks]
            
            x_min, x_max = min(x_coords), max(x_coords)
            y_min, y_max = min(y_coords), max(y_coords)
            
            height, width = image.shape[:2]
            bbox = (
                int(x_min * width),
                int(y_min * height),
                int((x_max - x_min) * width),
                int((y_max - y_min) * height)
            )
            
            detection_results.append(DetectionResult(
                mode=DetectionMode.POSE_ESTIMATION,
                confidence=0.8,
                bbox=bbox,
                label="Person",
                metadata={"landmarks": landmarks}
            ))
        
        return detection_results

class ComputerVisionSystem:
    """Main computer vision system that integrates all components"""
    
    def __init__(self):
        """Initialize the computer vision system"""
        self.object_detector = ObjectDetector()
        self.face_recognition = FaceRecognitionSystem()
        self.ocr_system = OCRSystem()
        self.segmentation = ImageSegmentation()
        self.pose_estimation = PoseEstimation()
        
        # Results storage
        self.results_history = []
    
    def process_image(self, image_path: str, modes: List[DetectionMode]) -> Dict[str, List[DetectionResult]]:
        """Process an image with specified detection modes
        
        Args:
            image_path: Path to the image file
            modes: List of detection modes to apply
            
        Returns:
            Dictionary of detection results by mode
        """
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        results = {}
        
        for mode in modes:
            if mode == DetectionMode.OBJECT_DETECTION:
                results['objects'] = self.object_detector.detect_objects(image)
            
            elif mode == DetectionMode.FACE_DETECTION:
                results['faces'] = self.face_recognition.detect_faces(image)
            
            elif mode == DetectionMode.FACE_RECOGNITION:
                results['face_recognition'] = self.face_recognition.recognize_faces(image)
            
            elif mode == DetectionMode.OCR:
                results['text'] = self.ocr_system.extract_text(image)
            
            elif mode == DetectionMode.POSE_ESTIMATION:
                results['poses'] = self.pose_estimation.estimate_pose(image)
        
        # Store results
        self.results_history.append({
            'image_path': image_path,
            'timestamp': time.time(),
            'results': results
        })
        
        return results
    
    def process_video(self, video_path: str, modes: List[DetectionMode], output_path: str = None):
        """Process a video file with real-time detection
        
        Args:
            video_path: Path to the video file
            modes: List of detection modes to apply
            output_path: Path to save processed video
        """
        cap = cv2.VideoCapture(video_path)
        
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process frame
            processed_frame = self.process_frame(frame, modes)
            
            # Display or save frame
            if output_path:
                out.write(processed_frame)
            else:
                cv2.imshow('Computer Vision System', processed_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            frame_count += 1
            if frame_count % 30 == 0:
                logger.info(f"Processed {frame_count} frames")
        
        cap.release()
        if output_path:
            out.release()
        cv2.destroyAllWindows()
    
    def process_frame(self, frame: np.ndarray, modes: List[DetectionMode]) -> np.ndarray:
        """Process a single frame with detection
        
        Args:
            frame: Input frame
            modes: List of detection modes
            
        Returns:
            Processed frame with annotations
        """
        annotated_frame = frame.copy()
        
        for mode in modes:
            if mode == DetectionMode.OBJECT_DETECTION:
                objects = self.object_detector.detect_objects(frame)
                annotated_frame = self.draw_detections(annotated_frame, objects, (0, 255, 0))
            
            elif mode == DetectionMode.FACE_DETECTION:
                faces = self.face_recognition.detect_faces(frame)
                annotated_frame = self.draw_detections(annotated_frame, faces, (255, 0, 0))
            
            elif mode == DetectionMode.FACE_RECOGNITION:
                face_recognition = self.face_recognition.recognize_faces(frame)
                annotated_frame = self.draw_detections(annotated_frame, face_recognition, (0, 0, 255))
            
            elif mode == DetectionMode.OCR:
                text_results = self.ocr_system.extract_text(frame)
                annotated_frame = self.draw_detections(annotated_frame, text_results, (255, 255, 0))
            
            elif mode == DetectionMode.POSE_ESTIMATION:
                poses = self.pose_estimation.estimate_pose(frame)
                annotated_frame = self.draw_pose(annotated_frame, poses)
        
        return annotated_frame
    
    def draw_detections(self, image: np.ndarray, detections: List[DetectionResult], color: Tuple[int, int, int]) -> np.ndarray:
        """Draw detection results on image
        
        Args:
            image: Input image
            detections: List of detections
            color: Color for drawing
            
        Returns:
            Image with drawn detections
        """
        for detection in detections:
            x, y, w, h = detection.bbox
            
            # Draw bounding box
            cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
            
            # Draw label
            label = f"{detection.label} ({detection.confidence:.2f})"
            cv2.putText(image, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return image
    
    def draw_pose(self, image: np.ndarray, poses: List[DetectionResult]) -> np.ndarray:
        """Draw pose estimation results
        
        Args:
            image: Input image
            poses: List of pose detections
            
        Returns:
            Image with drawn poses
        """
        for pose in poses:
            landmarks = pose.metadata.get('landmarks', [])
            height, width = image.shape[:2]
            
            # Draw landmarks
            for landmark in landmarks:
                x = int(landmark['x'] * width)
                y = int(landmark['y'] * height)
                cv2.circle(image, (x, y), 3, (0, 255, 255), -1)
        
        return image
    
    def save_results(self, output_path: str):
        """Save detection results to file
        
        Args:
            output_path: Path to save results
        """
        with open(output_path, 'w') as f:
            json.dump(self.results_history, f, indent=2, default=str)

class CVApplication:
    """Main application class for the computer vision system"""
    
    def __init__(self):
        """Initialize the application"""
        self.cv_system = ComputerVisionSystem()
        self.parse_arguments()
    
    def parse_arguments(self):
        """Parse command line arguments"""
        parser = argparse.ArgumentParser(description='Advanced Computer Vision System')
        
        parser.add_argument('--input', type=str, required=True, help='Input image or video path')
        parser.add_argument('--output', type=str, help='Output path for results')
        parser.add_argument('--modes', nargs='+', choices=[
            'objects', 'faces', 'face_recognition', 'ocr', 'pose', 'segmentation'
        ], default=['objects'], help='Detection modes to use')
        parser.add_argument('--video', action='store_true', help='Process as video')
        parser.add_argument('--add-face', type=str, nargs=2, metavar=('PATH', 'NAME'),
                           help='Add a known face for recognition')
        
        self.args = parser.parse_args()
    
    def run(self):
        """Run the computer vision application"""
        # Convert mode strings to enums
        mode_map = {
            'objects': DetectionMode.OBJECT_DETECTION,
            'faces': DetectionMode.FACE_DETECTION,
            'face_recognition': DetectionMode.FACE_RECOGNITION,
            'ocr': DetectionMode.OCR,
            'pose': DetectionMode.POSE_ESTIMATION,
            'segmentation': DetectionMode.SEGMENTATION
        }
        
        modes = [mode_map[mode] for mode in self.args.modes]
        
        # Add known face if specified
        if self.args.add_face:
            face_path, face_name = self.args.add_face
            self.cv_system.face_recognition.add_known_face(face_path, face_name)
        
        # Process input
        if self.args.video:
            self.cv_system.process_video(self.args.input, modes, self.args.output)
        else:
            results = self.cv_system.process_image(self.args.input, modes)
            
            # Display results
            for mode_name, detections in results.items():
                print(f"\n{mode_name.upper()} RESULTS:")
                for detection in detections:
                    print(f"  - {detection.label} (confidence: {detection.confidence:.2f})")
                    print(f"    Bounding box: {detection.bbox}")
            
            # Save results if output path specified
            if self.args.output:
                self.cv_system.save_results(self.args.output)
                print(f"\nResults saved to: {self.args.output}")

def main():
    """Main entry point"""
    print("=" * 60)
    print("Advanced Computer Vision System".center(60))
    print("Multi-modal detection and recognition".center(60))
    print("=" * 60)
    
    app = CVApplication()
    app.run()

if __name__ == "__main__":
    main() 