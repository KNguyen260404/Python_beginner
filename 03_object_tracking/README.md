# Object Tracking with OpenCV

This project demonstrates real-time object tracking using various OpenCV tracking algorithms.

## Features
- Multiple tracking algorithms:
  - CSRT (default): More accurate but slower
  - KCF: Good balance between accuracy and speed
  - BOOSTING: Older algorithm, less accurate
  - MIL: Better accuracy than BOOSTING
  - TLD: Good for tracking objects that change appearance
  - MEDIANFLOW: Good for predictable motion
  - MOSSE: Very fast but less accurate
  - GOTURN: Deep learning based tracker (requires additional model files)
- Real-time tracking with webcam or video file
- Interactive region of interest (ROI) selection
- Ability to switch between trackers during execution

## Usage
```
python object_tracking.py [video_file]
```

If no video file is provided, the program will use the default webcam.

### Controls:
- Press 's' to select an object to track (drag to create a bounding box)
- Press 'c' to cycle through different tracking algorithms
- Press 'q' to quit

## How it works
1. The program captures video frames from a webcam or video file
2. User selects a region of interest (ROI) to track
3. The selected tracking algorithm initializes with the ROI
4. For each subsequent frame, the tracker updates the object position
5. The program displays the tracking results in real-time

## Requirements
- OpenCV with contrib modules (for tracking algorithms)
- NumPy 