import cv2
import sys
import numpy as np

class ObjectTracker:
    def __init__(self, video_source=0):
        """
        Initialize the object tracker
        
        Args:
            video_source: Camera index or video file path
        """
        self.cap = cv2.VideoCapture(video_source)
        if not self.cap.isOpened():
            raise ValueError(f"Could not open video source {video_source}")
        
        # Default tracking parameters
        self.tracker_types = ['BOOSTING', 'MIL', 'KCF', 'TLD', 'MEDIANFLOW', 'GOTURN', 'MOSSE', 'CSRT']
        self.tracker_type = 'CSRT'  # Default tracker
        self.tracker = None
        self.bbox = None
        self.tracking = False
        
    def __del__(self):
        """Release resources when object is deleted"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
    
    def create_tracker(self):
        """Create a tracker based on tracker_type"""
        if self.tracker_type == 'BOOSTING':
            return cv2.legacy.TrackerBoosting_create()
        elif self.tracker_type == 'MIL':
            return cv2.legacy.TrackerMIL_create()
        elif self.tracker_type == 'KCF':
            return cv2.legacy.TrackerKCF_create()
        elif self.tracker_type == 'TLD':
            return cv2.legacy.TrackerTLD_create()
        elif self.tracker_type == 'MEDIANFLOW':
            return cv2.legacy.TrackerMedianFlow_create()
        elif self.tracker_type == 'GOTURN':
            return cv2.TrackerGOTURN_create()
        elif self.tracker_type == 'MOSSE':
            return cv2.legacy.TrackerMOSSE_create()
        elif self.tracker_type == 'CSRT':
            return cv2.legacy.TrackerCSRT_create()
        else:
            raise ValueError(f"Unsupported tracker type: {self.tracker_type}")
    
    def select_roi(self, frame):
        """Let user select region of interest (ROI)"""
        bbox = cv2.selectROI("Tracking", frame, False)
        return bbox
    
    def run(self):
        """Main tracking loop"""
        print(f"Using {self.tracker_type} tracker")
        print("Press 's' to select ROI")
        print("Press 'c' to change tracker")
        print("Press 'q' to quit")
        
        while True:
            # Read a new frame
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to read frame")
                break
            
            # Display FPS and tracker info
            frame_info = f"Tracker: {self.tracker_type}"
            cv2.putText(frame, frame_info, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # If tracking is active
            if self.tracking:
                # Update tracker
                success, bbox = self.tracker.update(frame)
                
                # Draw bounding box if tracking successful
                if success:
                    # Tracking success
                    p1 = (int(bbox[0]), int(bbox[1]))
                    p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
                    cv2.rectangle(frame, p1, p2, (255, 0, 0), 2, 1)
                    cv2.putText(frame, "Tracking", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                else:
                    # Tracking failure
                    cv2.putText(frame, "Tracking failure", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            
            # Display result
            cv2.imshow("Tracking", frame)
            
            # Process key events
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                # Quit
                break
            elif key == ord('s'):
                # Select ROI
                self.bbox = self.select_roi(frame)
                self.tracker = self.create_tracker()
                self.tracker.init(frame, self.bbox)
                self.tracking = True
            elif key == ord('c'):
                # Change tracker
                current_idx = self.tracker_types.index(self.tracker_type)
                next_idx = (current_idx + 1) % len(self.tracker_types)
                self.tracker_type = self.tracker_types[next_idx]
                print(f"Changed to {self.tracker_type} tracker")
                
                # If already tracking, reinitialize with new tracker
                if self.tracking and self.bbox is not None:
                    self.tracker = self.create_tracker()
                    self.tracker.init(frame, self.bbox)

def main():
    # Use camera or video file
    video_source = 0  # Default: webcam
    if len(sys.argv) > 1:
        video_source = sys.argv[1]
    
    try:
        tracker = ObjectTracker(video_source)
        tracker.run()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 