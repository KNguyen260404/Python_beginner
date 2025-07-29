# Advanced Computer Vision System

A comprehensive computer vision system that implements multiple detection and recognition capabilities using deep learning and traditional computer vision techniques.

## Features

- **Object Detection**: YOLO-based object detection with 80+ object classes
- **Face Detection & Recognition**: Real-time face detection and person identification
- **Optical Character Recognition (OCR)**: Text extraction from images with preprocessing
- **Image Segmentation**: Watershed, K-means, and GrabCut segmentation algorithms
- **Pose Estimation**: Human pose detection using MediaPipe
- **Real-time Video Processing**: Live video analysis with multiple detection modes
- **Multi-modal Analysis**: Combine different detection methods simultaneously

## Requirements

- Python 3.7+
- OpenCV
- TensorFlow
- MediaPipe
- face_recognition
- pytesseract
- scikit-learn
- NumPy
- Matplotlib

## Installation

1. Install the required packages:

```bash
pip install -r requirements_computer_vision.txt
```

2. Install Tesseract OCR:

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
```

**Windows:**
Download and install from: https://github.com/UB-Mannheim/tesseract/wiki

**macOS:**
```bash
brew install tesseract
```

## Usage

### Command Line Interface

**Process an image with object detection:**
```bash
python 27_advanced_computer_vision.py --input image.jpg --modes objects
```

**Multiple detection modes:**
```bash
python 27_advanced_computer_vision.py --input image.jpg --modes objects faces ocr pose
```

**Process video with real-time detection:**
```bash
python 27_advanced_computer_vision.py --input video.mp4 --video --modes faces pose --output processed_video.avi
```

**Add known face for recognition:**
```bash
python 27_advanced_computer_vision.py --add-face person.jpg "John Doe" --input group_photo.jpg --modes face_recognition
```

### Detection Modes

- `objects`: Detect and classify objects using YOLO
- `faces`: Detect faces in images
- `face_recognition`: Recognize known faces
- `ocr`: Extract text from images
- `pose`: Estimate human pose landmarks
- `segmentation`: Segment images using various algorithms

## Advanced Features

### Object Detection
- Uses YOLOv4/YOLOv5 for high-accuracy detection
- Supports 80+ COCO object classes
- Non-maximum suppression for clean results
- Fallback to traditional CV methods

### Face Recognition
- Face encoding using deep learning
- Support for multiple known faces
- Real-time recognition in video streams
- Confidence scoring for matches

### OCR System
- Automatic image preprocessing for better text extraction
- Supports multiple languages
- Bounding box detection for text regions
- Confidence filtering for accurate results

### Image Segmentation
- **Watershed**: Marker-based segmentation for touching objects
- **K-means**: Color-based clustering segmentation
- **GrabCut**: Interactive foreground/background separation

### Pose Estimation
- 33 body landmarks detection
- Real-time pose tracking
- 3D coordinate estimation
- Visibility confidence for each landmark

## Project Structure

- `ObjectDetector`: YOLO-based object detection
- `FaceRecognitionSystem`: Face detection and recognition
- `OCRSystem`: Text extraction with preprocessing
- `ImageSegmentation`: Multiple segmentation algorithms
- `PoseEstimation`: Human pose detection
- `ComputerVisionSystem`: Main integration class
- `CVApplication`: Command-line interface

## Model Files

For optimal performance, download these model files:

1. **YOLO Models**:
   - `yolov4.weights`
   - `yolov4.cfg`
   - `coco.names`

2. **Place in `yolo/` directory**

## Performance Optimization

- GPU acceleration with CUDA support
- Batch processing for multiple images
- Optimized preprocessing pipelines
- Memory-efficient video processing

## Examples

### Basic Object Detection
```python
from advanced_computer_vision import ComputerVisionSystem, DetectionMode

cv_system = ComputerVisionSystem()
results = cv_system.process_image('image.jpg', [DetectionMode.OBJECT_DETECTION])

for detection in results['objects']:
    print(f"Found {detection.label} with confidence {detection.confidence:.2f}")
```

### Face Recognition Setup
```python
# Add known faces
cv_system.face_recognition.add_known_face('john.jpg', 'John Doe')
cv_system.face_recognition.add_known_face('jane.jpg', 'Jane Smith')

# Recognize faces in new image
results = cv_system.process_image('group.jpg', [DetectionMode.FACE_RECOGNITION])
```

### Video Processing
```python
cv_system.process_video(
    'input_video.mp4',
    [DetectionMode.OBJECT_DETECTION, DetectionMode.POSE_ESTIMATION],
    'output_video.avi'
)
```

## Troubleshooting

- **YOLO model not found**: Download model files or system will use fallback detection
- **Tesseract not found**: Install Tesseract OCR system package
- **Face recognition errors**: Install dlib with proper compilation flags
- **GPU not detected**: Install CUDA-compatible OpenCV build

## License

This project is open source and available under the MIT License. 