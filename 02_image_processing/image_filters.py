import cv2
import numpy as np
import sys
import os

class ImageProcessor:
    def __init__(self, image_path=None):
        if image_path:
            self.original = cv2.imread(image_path)
            if self.original is None:
                raise ValueError(f"Could not read image at {image_path}")
            self.image = self.original.copy()
        else:
            self.original = None
            self.image = None
    
    def load_image(self, image_path):
        """Load an image from file"""
        self.original = cv2.imread(image_path)
        if self.original is None:
            raise ValueError(f"Could not read image at {image_path}")
        self.image = self.original.copy()
        return self
    
    def reset(self):
        """Reset to original image"""
        if self.original is not None:
            self.image = self.original.copy()
        return self
    
    def grayscale(self):
        """Convert image to grayscale"""
        if self.image is not None:
            self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
            # Convert back to 3 channels for consistency with other filters
            self.image = cv2.cvtColor(self.image, cv2.COLOR_GRAY2BGR)
        return self
    
    def blur(self, kernel_size=5):
        """Apply Gaussian blur"""
        if self.image is not None:
            self.image = cv2.GaussianBlur(self.image, (kernel_size, kernel_size), 0)
        return self
    
    def canny_edge(self, threshold1=100, threshold2=200):
        """Apply Canny edge detection"""
        if self.image is not None:
            gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, threshold1, threshold2)
            # Convert back to 3 channels
            self.image = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        return self
    
    def sharpen(self):
        """Sharpen the image"""
        if self.image is not None:
            kernel = np.array([[-1, -1, -1], 
                               [-1,  9, -1], 
                               [-1, -1, -1]])
            self.image = cv2.filter2D(self.image, -1, kernel)
        return self
    
    def sepia(self):
        """Apply sepia filter"""
        if self.image is not None:
            kernel = np.array([[0.272, 0.534, 0.131],
                               [0.349, 0.686, 0.168],
                               [0.393, 0.769, 0.189]])
            self.image = cv2.transform(self.image, kernel)
        return self
    
    def invert(self):
        """Invert the image colors"""
        if self.image is not None:
            self.image = cv2.bitwise_not(self.image)
        return self
    
    def adjust_brightness(self, value=30):
        """Adjust brightness of the image"""
        if self.image is not None:
            hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
            h, s, v = cv2.split(hsv)
            
            # Adjust brightness (Value in HSV)
            v = cv2.add(v, value)
            v[v > 255] = 255
            v[v < 0] = 0
            
            hsv = cv2.merge((h, s, v))
            self.image = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        return self
    
    def rotate(self, angle=90):
        """Rotate the image"""
        if self.image is not None:
            height, width = self.image.shape[:2]
            center = (width // 2, height // 2)
            rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            self.image = cv2.warpAffine(self.image, rotation_matrix, (width, height))
        return self
    
    def display(self, window_name="Image"):
        """Display the current image"""
        if self.image is not None:
            cv2.imshow(window_name, self.image)
            cv2.waitKey(0)
            cv2.destroyWindow(window_name)
        return self
    
    def save(self, output_path):
        """Save the current image to file"""
        if self.image is not None:
            directory = os.path.dirname(output_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            cv2.imwrite(output_path, self.image)
            print(f"Image saved to {output_path}")
        return self

def main():
    if len(sys.argv) < 2:
        print("Usage: python image_filters.py <image_path> [filter_name]")
        print("Available filters: grayscale, blur, edge, sharpen, sepia, invert, brighten, rotate")
        return
    
    image_path = sys.argv[1]
    
    try:
        processor = ImageProcessor(image_path)
        
        if len(sys.argv) > 2:
            filter_name = sys.argv[2].lower()
            
            if filter_name == "grayscale":
                processor.grayscale()
            elif filter_name == "blur":
                processor.blur()
            elif filter_name == "edge":
                processor.canny_edge()
            elif filter_name == "sharpen":
                processor.sharpen()
            elif filter_name == "sepia":
                processor.sepia()
            elif filter_name == "invert":
                processor.invert()
            elif filter_name == "brighten":
                processor.adjust_brightness(30)
            elif filter_name == "rotate":
                processor.rotate()
            else:
                print(f"Unknown filter: {filter_name}")
                return
                
            output_path = f"output_{filter_name}_{os.path.basename(image_path)}"
            processor.save(output_path)
        
        processor.display("Filtered Image")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 