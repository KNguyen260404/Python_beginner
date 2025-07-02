# Motion Detection with OpenCV

This project implements a motion detection system using OpenCV. It can detect motion in real-time from a webcam or video file, and optionally record video clips when motion is detected.

## Features
- Real-time motion detection
- Adjustable sensitivity and detection parameters
- Motion area highlighting with bounding boxes
- Optional video recording of motion events
- Date and time overlay on video
- Command-line interface for easy configuration

## Usage
```
python motion_detector.py [options]
```

### Command-line Options
- `-v, --video`: Path to video file (default: use webcam)
- `-s, --sensitivity`: Motion detection sensitivity (lower is more sensitive, default: 20)
- `-b, --blur`: Blur kernel size (default: 21)
- `-a, --min-area`: Minimum contour area to detect motion (default: 500)
- `-r, --record`: Enable recording of detected motion
- `-o, --output`: Output directory for recorded videos (default: "motion_captures")

### Examples
```
# Use webcam with default settings
python motion_detector.py

# Use webcam with higher sensitivity and record motion
python motion_detector.py -s 15 -r

# Use a video file as input
python motion_detector.py -v path/to/video.mp4
```

## How it works
The motion detection algorithm works by:

1. Converting each frame to grayscale and applying Gaussian blur
2. Computing the absolute difference between the current frame and a background model
3. Thresholding the difference to create a binary image
4. Finding contours in the binary image
5. Filtering contours by area to identify significant motion
6. Drawing bounding boxes around areas with detected motion
7. Updating the background model using a weighted average

## Controls
- Press 'q' to quit the application

## Requirements
- OpenCV
- NumPy

## Output
When recording is enabled, video clips are saved to the specified output directory with filenames in the format:
```
motion_YYYYMMDD_HHMMSS_N.mp4
```
Where N is a counter that increments for each new recording session. 