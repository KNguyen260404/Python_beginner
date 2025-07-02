# Document Scanner with OpenCV

This project implements a document scanner that can automatically detect document boundaries, apply perspective transform to get a top-down view, and enhance the scanned document.

## Features
- Automatic document boundary detection
- Perspective correction to get a top-down view
- Image enhancement with adaptive thresholding
- Support for various document sizes and orientations

## Usage
```
python document_scanner.py <image_path> [output_path]
```

If no output path is provided, the result will be saved as `<input_filename>_scanned.<extension>`.

## How it works
The document scanning process involves several steps:

1. **Edge Detection**: The program detects edges in the input image using the Canny edge detector.

2. **Contour Detection**: It finds contours in the edge image and identifies the largest contour with 4 corners, which is likely to be the document.

3. **Perspective Transform**: The program applies a perspective transform to get a top-down view of the document.

4. **Enhancement**: Finally, it enhances the scanned document using adaptive thresholding to improve readability.

## Example
Input image with detected document boundaries:
![Original with Contours](example_contours.jpg)

Output after scanning and enhancement:
![Scanned Document](example_scanned.jpg)

## Requirements
- OpenCV
- NumPy

## Limitations
- The document should have a clear contrast with the background
- The document should be quadrilateral (four corners)
- The document should be fully visible in the image 