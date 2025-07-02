import cv2
import numpy as np
import sys
import os

class DocumentScanner:
    def __init__(self):
        self.image = None
        self.orig_image = None
        self.corners = None
        self.width = 0
        self.height = 0
    
    def load_image(self, image_path):
        """Load image from file"""
        self.orig_image = cv2.imread(image_path)
        if self.orig_image is None:
            raise ValueError(f"Could not read image at {image_path}")
        self.image = self.orig_image.copy()
        return self
    
    def resize_image(self, height=500):
        """Resize image keeping aspect ratio"""
        if self.image is None:
            return self
        
        h, w = self.image.shape[:2]
        ratio = height / h
        dim = (int(w * ratio), height)
        self.image = cv2.resize(self.image, dim)
        return self
    
    def edge_detection(self):
        """Detect edges in the image"""
        if self.image is None:
            return self
        
        # Convert to grayscale
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Edge detection
        edges = cv2.Canny(blurred, 75, 200)
        
        return edges
    
    def find_contours(self):
        """Find contours in the image"""
        if self.image is None:
            return self
        
        # Get edges
        edges = self.edge_detection()
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        
        # Sort contours by area (largest first)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        
        # Find the document contour (assumed to be the largest with 4 corners)
        document_contour = None
        for contour in contours:
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
            
            # If contour has 4 points, it's likely the document
            if len(approx) == 4:
                document_contour = approx
                break
        
        if document_contour is None:
            print("Could not find document contours. Using full image.")
            h, w = self.image.shape[:2]
            document_contour = np.array([[0, 0], [w-1, 0], [w-1, h-1], [0, h-1]], dtype=np.float32).reshape(-1, 1, 2)
        
        # Draw contours on a copy of the image
        contour_image = self.image.copy()
        cv2.drawContours(contour_image, [document_contour], -1, (0, 255, 0), 2)
        
        # Extract corners
        self.corners = document_contour.reshape(4, 2)
        
        # Draw corners
        for corner in self.corners:
            x, y = corner
            cv2.circle(contour_image, (int(x), int(y)), 5, (0, 0, 255), -1)
        
        return contour_image
    
    def order_points(self, pts):
        """Order points in top-left, top-right, bottom-right, bottom-left order"""
        rect = np.zeros((4, 2), dtype=np.float32)
        
        # Sum of coordinates
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]  # Top-left: smallest sum
        rect[2] = pts[np.argmax(s)]  # Bottom-right: largest sum
        
        # Difference of coordinates
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]  # Top-right: smallest difference
        rect[3] = pts[np.argmax(diff)]  # Bottom-left: largest difference
        
        return rect
    
    def perspective_transform(self):
        """Apply perspective transform to get top-down view"""
        if self.image is None or self.corners is None:
            return self
        
        # Order points
        rect = self.order_points(self.corners)
        
        # Calculate width and height of the new image
        # Width: maximum distance between top-right and top-left or bottom-right and bottom-left
        width_a = np.sqrt(((rect[1][0] - rect[0][0]) ** 2) + ((rect[1][1] - rect[0][1]) ** 2))
        width_b = np.sqrt(((rect[2][0] - rect[3][0]) ** 2) + ((rect[2][1] - rect[3][1]) ** 2))
        self.width = max(int(width_a), int(width_b))
        
        # Height: maximum distance between top-right and bottom-right or top-left and bottom-left
        height_a = np.sqrt(((rect[2][0] - rect[1][0]) ** 2) + ((rect[2][1] - rect[1][1]) ** 2))
        height_b = np.sqrt(((rect[3][0] - rect[0][0]) ** 2) + ((rect[3][1] - rect[0][1]) ** 2))
        self.height = max(int(height_a), int(height_b))
        
        # Destination points
        dst = np.array([
            [0, 0],
            [self.width - 1, 0],
            [self.width - 1, self.height - 1],
            [0, self.height - 1]
        ], dtype=np.float32)
        
        # Calculate perspective transform matrix
        M = cv2.getPerspectiveTransform(rect, dst)
        
        # Apply perspective transform
        warped = cv2.warpPerspective(self.orig_image, M, (self.width, self.height))
        
        return warped
    
    def enhance_scan(self, warped):
        """Enhance the scanned document"""
        if warped is None:
            return None
        
        # Convert to grayscale
        gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        
        return thresh
    
    def scan_document(self, image_path, output_path=None, enhance=True):
        """Scan document and save result"""
        try:
            # Load and resize image
            self.load_image(image_path).resize_image()
            
            # Find document contours
            contour_image = self.find_contours()
            
            # Apply perspective transform
            warped = self.perspective_transform()
            
            # Enhance if requested
            if enhance:
                result = self.enhance_scan(warped)
            else:
                result = warped
            
            # Save result if output path provided
            if output_path:
                directory = os.path.dirname(output_path)
                if directory and not os.path.exists(directory):
                    os.makedirs(directory)
                cv2.imwrite(output_path, result)
                print(f"Scanned document saved to {output_path}")
            
            return result, contour_image
            
        except Exception as e:
            print(f"Error scanning document: {e}")
            return None, None

def main():
    if len(sys.argv) < 2:
        print("Usage: python document_scanner.py <image_path> [output_path]")
        return
    
    image_path = sys.argv[1]
    
    # Default output path if not provided
    output_path = None
    if len(sys.argv) > 2:
        output_path = sys.argv[2]
    else:
        # Generate output path based on input path
        filename, ext = os.path.splitext(image_path)
        output_path = f"{filename}_scanned{ext}"
    
    scanner = DocumentScanner()
    result, contour_image = scanner.scan_document(image_path, output_path)
    
    if result is not None and contour_image is not None:
        # Display results
        cv2.imshow("Original with Contours", contour_image)
        cv2.imshow("Scanned Document", result)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main() 