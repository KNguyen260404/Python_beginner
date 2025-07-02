import cv2
import numpy as np
import datetime
import time
import argparse
import os

class MotionDetector:
    def __init__(self, video_source=0, sensitivity=20, blur_size=21, 
                 min_area=500, show_datetime=True, record=False, output_dir="motion_captures"):
        """
        Initialize the motion detector
        
        Args:
            video_source: Camera index or video file path
            sensitivity: Lower values are more sensitive to motion (default: 20)
            blur_size: Size of Gaussian blur kernel (default: 21)
            min_area: Minimum contour area to be considered motion (default: 500)
            show_datetime: Whether to show date and time on frame (default: True)
            record: Whether to record detected motion (default: False)
            output_dir: Directory to save recorded motion (default: "motion_captures")
        """
        self.cap = cv2.VideoCapture(video_source)
        if not self.cap.isOpened():
            raise ValueError(f"Could not open video source {video_source}")
        
        self.sensitivity = sensitivity
        self.blur_size = blur_size
        self.min_area = min_area
        self.show_datetime = show_datetime
        self.record = record
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        if self.record and not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # Initialize variables
        self.background = None
        self.video_writer = None
        self.recording = False
        self.motion_detected = False
        self.motion_start_time = None
        self.record_counter = 0
        
        # Get video properties
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        if self.fps <= 0:  # If FPS detection fails, use default
            self.fps = 30
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
    def __del__(self):
        """Release resources when object is deleted"""
        if self.cap:
            self.cap.release()
        if self.video_writer:
            self.video_writer.release()
        cv2.destroyAllWindows()
    
    def start_recording(self, frame):
        """Start recording video when motion is detected"""
        if not self.record:
            return
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(self.output_dir, f"motion_{timestamp}_{self.record_counter}.mp4")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.video_writer = cv2.VideoWriter(output_path, fourcc, self.fps, (self.width, self.height))
        self.recording = True
        self.record_counter += 1
        print(f"Motion detected! Recording to {output_path}")
    
    def stop_recording(self):
        """Stop recording video"""
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None
        self.recording = False
        print("Recording stopped")
    
    def detect_motion(self, frame):
        """Detect motion in frame"""
        # Convert frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur
        gray = cv2.GaussianBlur(gray, (self.blur_size, self.blur_size), 0)
        
        # If background is None, initialize it
        if self.background is None:
            self.background = gray
            return frame, False
        
        # Calculate absolute difference between current frame and background
        frame_delta = cv2.absdiff(self.background, gray)
        
        # Apply threshold to highlight differences
        thresh = cv2.threshold(frame_delta, self.sensitivity, 255, cv2.THRESH_BINARY)[1]
        
        # Dilate the thresholded image to fill in holes
        thresh = cv2.dilate(thresh, None, iterations=2)
        
        # Find contours in thresholded image
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Initialize motion flag
        motion = False
        
        # Process each contour
        for contour in contours:
            # If contour is too small, ignore it
            if cv2.contourArea(contour) < self.min_area:
                continue
            
            # Draw rectangle around contour
            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            motion = True
        
        # Show motion status
        status = "Motion Detected" if motion else "No Motion"
        cv2.putText(frame, f"Status: {status}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        # Show datetime if enabled
        if self.show_datetime:
            datetime_text = datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p")
            cv2.putText(frame, datetime_text, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        
        # Update background (running average)
        cv2.accumulateWeighted(gray, self.background, 0.5)
        
        return frame, motion
    
    def run(self):
        """Main motion detection loop"""
        print("Motion detection started. Press 'q' to quit.")
        
        while True:
            # Read a new frame
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to read frame")
                break
            
            # Detect motion
            frame, motion = self.detect_motion(frame)
            
            # Handle motion state changes
            if motion and not self.motion_detected:
                # Motion just started
                self.motion_detected = True
                self.motion_start_time = time.time()
                self.start_recording(frame)
            elif not motion and self.motion_detected:
                # No motion for a while, stop recording
                elapsed = time.time() - self.motion_start_time
                if elapsed > 3:  # Wait 3 seconds after motion stops
                    self.motion_detected = False
                    if self.recording:
                        self.stop_recording()
            
            # Record frame if recording is active
            if self.recording and self.video_writer:
                self.video_writer.write(frame)
            
            # Display result
            cv2.imshow("Motion Detection", frame)
            
            # Check for key press
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
        
        # Clean up
        if self.recording:
            self.stop_recording()

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Motion Detection with OpenCV")
    parser.add_argument("-v", "--video", help="Path to video file (default: use webcam)", default=0)
    parser.add_argument("-s", "--sensitivity", help="Motion detection sensitivity (lower is more sensitive)", type=int, default=20)
    parser.add_argument("-b", "--blur", help="Blur kernel size", type=int, default=21)
    parser.add_argument("-a", "--min-area", help="Minimum contour area to detect motion", type=int, default=500)
    parser.add_argument("-r", "--record", help="Record detected motion", action="store_true")
    parser.add_argument("-o", "--output", help="Output directory for recorded videos", default="motion_captures")
    args = parser.parse_args()
    
    # Convert string video source to int if it's a digit
    video_source = args.video
    if video_source.isdigit():
        video_source = int(video_source)
    
    try:
        detector = MotionDetector(
            video_source=video_source,
            sensitivity=args.sensitivity,
            blur_size=args.blur,
            min_area=args.min_area,
            record=args.record,
            output_dir=args.output
        )
        detector.run()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 