# Face Detection Project

This project demonstrates face detection using OpenCV's Haar Cascade classifier.

## Features
- Face detection in images
- Real-time face detection using webcam

## Usage
1. To detect faces in an image:
```
python face_detection.py path/to/image.jpg
```

2. To detect faces using webcam (default if no image is provided):
```
python face_detection.py
```

3. Press 'q' to exit the webcam mode.

## Requirements
- OpenCV
- NumPy

## How it works
The program uses the Haar Cascade classifier, which is a machine learning based approach where a cascade function is trained from a lot of positive and negative images. It is then used to detect objects in other images.

For face detection, we use the pre-trained classifier that comes with OpenCV (`haarcascade_frontalface_default.xml`). 