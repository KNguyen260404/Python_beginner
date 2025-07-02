# Image Processing with OpenCV

This project demonstrates various image processing techniques using OpenCV.

## Features
- Multiple image filters and transformations:
  - Grayscale conversion
  - Gaussian blur
  - Canny edge detection
  - Image sharpening
  - Sepia filter
  - Color inversion
  - Brightness adjustment
  - Image rotation

## Usage
```
python image_filters.py <image_path> [filter_name]
```

### Available filters:
- `grayscale` - Convert image to grayscale
- `blur` - Apply Gaussian blur
- `edge` - Apply Canny edge detection
- `sharpen` - Sharpen the image
- `sepia` - Apply sepia tone filter
- `invert` - Invert the image colors
- `brighten` - Increase image brightness
- `rotate` - Rotate the image 90 degrees

### Examples:
```
# Apply grayscale filter
python image_filters.py path/to/image.jpg grayscale

# Apply edge detection
python image_filters.py path/to/image.jpg edge
```

## Output
The processed image will be:
1. Displayed in a window
2. Saved to a file with the format `output_<filter_name>_<original_filename>`

## Implementation
The project uses a class-based approach with method chaining to allow for multiple filters to be applied in sequence. Each filter is implemented as a method in the `ImageProcessor` class. 